#!/usr/bin/env python3
"""Cross-platform verification entrypoint for the Packer framework template."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import shlex
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

from ci._config import load_ci_config, select_case


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
YAMLLINT_CONFIG = (
    "{ extends: relaxed, rules: { line-length: disable, document-start: disable, "
    "comments: disable, truthy: {check-keys: false} } }"
)

Step = Callable[[], None]


def run(args: list[str], *, input_text: str | None = None) -> None:
    print("+ " + " ".join(args), flush=True)
    try:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            input=input_text,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"missing executable: {args[0]}") from exc
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


class ProcessMemoryCountersEx(ctypes.Structure):
    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("PageFaultCount", ctypes.c_ulong),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
        ("PrivateUsage", ctypes.c_size_t),
    ]


def process_private_bytes(process: subprocess.Popen[str]) -> int | None:
    if os.name != "nt":
        return None
    counters = ProcessMemoryCountersEx()
    counters.cb = ctypes.sizeof(counters)
    handle = getattr(process, "_handle", None)
    if handle is None:
        return None
    ok = ctypes.windll.psapi.GetProcessMemoryInfo(
        ctypes.c_void_p(handle), ctypes.byref(counters), counters.cb
    )
    if not ok:
        return None
    return int(counters.PrivateUsage)


def run_opa(args: list[str], *, input_text: str | None = None) -> None:
    """Run OPA under a wall-clock timeout and (on Windows) a private-memory cap.

    A pathological Rego policy can drive ``opa eval`` to tens of GB of committed
    memory and hang the host. This bounds it so OPA aborts with a clear error
    instead of wedging the machine. Tunable via OPA_TIMEOUT_SECONDS and
    OPA_MAX_PRIVATE_MB environment variables.
    """
    timeout_seconds = int(os.environ.get("OPA_TIMEOUT_SECONDS", "30"))
    max_private_mb = int(os.environ.get("OPA_MAX_PRIVATE_MB", "1024"))
    max_private_bytes = max_private_mb * 1024 * 1024

    print("+ " + " ".join(args), flush=True)
    try:
        process = subprocess.Popen(
            args,
            cwd=ROOT,
            stdin=subprocess.PIPE if input_text is not None else None,
            text=True,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"missing executable: {args[0]}") from exc

    if input_text is not None and process.stdin is not None:
        process.stdin.write(input_text)
        process.stdin.close()

    deadline = time.monotonic() + timeout_seconds
    peak_private = 0
    killed_reason: str | None = None
    while process.poll() is None:
        private_bytes = process_private_bytes(process)
        if private_bytes is not None:
            peak_private = max(peak_private, private_bytes)
            if private_bytes > max_private_bytes:
                killed_reason = (
                    f"private memory exceeded {max_private_mb} MiB "
                    f"(observed {private_bytes // (1024 * 1024)} MiB)"
                )
                process.kill()
                break
        if time.monotonic() > deadline:
            killed_reason = f"timeout exceeded {timeout_seconds} seconds"
            process.kill()
            break
        time.sleep(0.1)

    returncode = process.wait()
    if killed_reason is not None:
        if peak_private:
            print(f"opa peak private memory: {peak_private // (1024 * 1024)} MiB")
        raise SystemExit(f"opa aborted: {killed_reason}")
    if returncode != 0:
        raise SystemExit(returncode)


def capture(args: list[str], *, input_text: str | None = None) -> str:
    print("+ " + " ".join(args), flush=True)
    try:
        completed = subprocess.run(
            args,
            cwd=ROOT,
            capture_output=True,
            input=input_text,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise SystemExit(f"missing executable: {args[0]}") from exc
    if completed.returncode != 0:
        sys.stdout.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode)
    return completed.stdout


def install(package: str) -> None:
    if os.environ.get("CI", "").lower() != "true":
        print(f"local run: not installing {package}; expecting it to be available", flush=True)
        return
    run([PYTHON, "-m", "pip", "install", "--no-cache-dir", package])


def command_from_env(name: str, default: str) -> list[str]:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return [default]

    raw = raw.strip()
    if raw.startswith("["):
        parsed = json.loads(raw)
        if not isinstance(parsed, list) or not all(
            isinstance(item, str) and item for item in parsed
        ):
            raise SystemExit(f"{name} must be a JSON array of command strings.")
        return parsed

    if Path(raw).exists():
        return [raw]

    return shlex.split(raw, posix=os.name != "nt")


def opa_policy() -> None:
    install("pyyaml==6.0.3")
    opa_input = capture([PYTHON, "tools/build_opa_input.py"])
    run_opa(
        [
            "opa",
            "eval",
            "--fail-defined",
            "--format",
            "pretty",
            "--stdin-input",
            "--data",
            "policies/opa",
            "data.repo_hygiene.deny[_]",
        ],
        input_text=opa_input,
    )


def opa_artifact(case: str) -> None:
    run([PYTHON, "tools/ci/run_integration.py", "--case", case])
    opa_input = capture([PYTHON, "tools/build_packer_artifact_input.py"])
    run_opa(
        [
            "opa",
            "eval",
            "--fail-defined",
            "--format",
            "pretty",
            "--stdin-input",
            "--data",
            "policies/opa",
            "data.packer_artifact.deny[_]",
        ],
        input_text=opa_input,
    )


def validate(case: str) -> None:
    config = load_ci_config(ROOT)
    try:
        case_config = select_case(config, case)
    except ValueError as exc:
        raise SystemExit(str(exc)) from None
    run(
        [
            "packer",
            "validate",
            "-var-file",
            case_config["var_file"],
            config.get("packer_root", "packer"),
        ]
    )


def validate_syntax_only() -> None:
    config = load_ci_config(ROOT)
    run(["packer", "validate", "-syntax-only", config.get("packer_root", "packer")])


def build_steps(case: str) -> dict[str, Step]:
    shell_helpers = sorted(
        path.relative_to(ROOT).as_posix() for path in (ROOT / "tools" / "ci").glob("*.sh")
    )
    install_helper = ROOT / "tools" / "install_ci_tools.sh"
    if install_helper.is_file():
        shell_helpers.append(install_helper.relative_to(ROOT).as_posix())
    bats_tests = sorted(
        path.relative_to(ROOT).as_posix() for path in (ROOT / "tests" / "ci").glob("*.bats")
    )
    return {
        "fmt": lambda: run(["packer", "fmt", "-recursive", "packer", "examples"]),
        "fmt-check": lambda: run(
            ["packer", "fmt", "-check", "-recursive", "packer", "examples"]
        ),
        "init": lambda: run(["packer", "init", "packer"]),
        "plugin-provenance": lambda: run([PYTHON, "tools/check_packer_plugin_provenance.py"]),
        "plugin-install-check": lambda: run(
            [PYTHON, "tools/check_packer_plugin_provenance.py", "--installed"]
        ),
        "validate": lambda: validate(case),
        "validate-syntax-only": validate_syntax_only,
        "inspect": lambda: run(["packer", "inspect", "packer"]),
        "ruff": lambda: (
            install("ruff==0.13.0"),
            run([PYTHON, "-m", "ruff", "check", "tools/"]),
        ),
        "yamllint": lambda: (
            install("yamllint==1.35.1"),
            run([PYTHON, "-m", "yamllint", "-d", YAMLLINT_CONFIG, ".github/workflows/"]),
        ),
        "actionlint": lambda: run([*command_from_env("ACTIONLINT", "actionlint")]),
        "markdownlint": lambda: run(
            [*command_from_env("MARKDOWNLINT", "markdownlint-cli2"), "**/*.md"]
        ),
        "test": lambda: (
            run([PYTHON, "tools/test_render_reference_build.py"]),
            run([PYTHON, "tools/test_packer_variable_validation.py"]),
        ),
        "workflow-helper-tests": lambda: (
            run([*command_from_env("SHELLCHECK", "shellcheck"), *shell_helpers]),
            run([PYTHON, "tools/ci/check_workflow_run_inputs.py", ".github/workflows"]),
            run([*command_from_env("BATS", "bats"), *bats_tests]),
        ),
        "privileged-workflows": lambda: (
            install("pyyaml==6.0.3"),
            run([PYTHON, "tools/check_privileged_workflows.py", "--repo-root", "."]),
            run([PYTHON, "tools/run_privileged_workflow_tests.py"]),
        ),
        "opa-test": lambda: run_opa(["opa", "test", "policies/opa"]),
        "opa-policy": opa_policy,
        "opa-artifact": lambda: opa_artifact(case),
        "manifest-check": lambda: run(
            [PYTHON, "tools/check_baseline_manifest.py"]
        ),
        "docs": lambda: run([PYTHON, "tools/gen_packer_docs.py"]),
        "docs-diff": lambda: run([PYTHON, "tools/gen_packer_docs.py", "--check"]),
        "docs-layout": lambda: run([PYTHON, "tools/check_docs_layout.py"]),
        "adr-schema": lambda: run([PYTHON, "tools/check_adr_schema.py"]),
        "integration": lambda: run(
            [PYTHON, "tools/ci/run_integration.py", "--case", case]
        ),
    }


TARGETS: dict[str, tuple[str, ...]] = {
    "packer-syntax": ("fmt-check", "validate-syntax-only"),
    "packer-validate-safe": ("opa-policy", "validate"),
    "lint": (
        "packer-syntax",
        "init",
        "plugin-provenance",
        "plugin-install-check",
        "packer-validate-safe",
        "inspect",
        "ruff",
        "yamllint",
    ),
    "policy": ("opa-test", "opa-policy", "opa-artifact"),
    "docs-check": ("docs-diff", "docs-layout", "adr-schema"),
    "ci": (
        "lint",
        "actionlint",
        "test",
        "workflow-helper-tests",
        "privileged-workflows",
        "policy",
        "markdownlint",
        "docs-check",
        "manifest-check",
    ),
    "verify": ("ci", "integration"),
}


def execute(name: str, steps: dict[str, Step]) -> None:
    if name in TARGETS:
        for child in TARGETS[name]:
            execute(child, steps)
        return
    steps[name]()


def main() -> int:
    choices = sorted(set(TARGETS) | set(build_steps("reference-linux")))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default="verify", choices=choices)
    parser.add_argument(
        "--case",
        default="reference-linux",
        help="Case to run for case-aware targets.",
    )
    args = parser.parse_args()

    execute(args.target, build_steps(args.case))
    return 0


if __name__ == "__main__":
    sys.exit(main())
