#!/usr/bin/env python3
"""Cross-platform verification entrypoint for the Packer framework template."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
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
    run(
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
    run(
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


def build_steps(case: str) -> dict[str, Step]:
    shell_helpers = sorted(
        path.relative_to(ROOT).as_posix() for path in (ROOT / "tools" / "ci").glob("*.sh")
    )
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
        "inspect": lambda: run(["packer", "inspect", "packer"]),
        "ruff": lambda: (
            install("ruff==0.13.0"),
            run([PYTHON, "-m", "ruff", "check", "tools/"]),
        ),
        "yamllint": lambda: (
            install("yamllint==1.35.1"),
            run([PYTHON, "-m", "yamllint", "-d", YAMLLINT_CONFIG, ".github/workflows/"]),
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
        "opa-test": lambda: run(["opa", "test", "policies/opa"]),
        "opa-policy": opa_policy,
        "opa-artifact": lambda: opa_artifact(case),
        "manifest-check": lambda: run(
            [PYTHON, "tools/check_baseline_manifest.py", "--check-present-sources"]
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
    "lint": (
        "fmt-check",
        "init",
        "plugin-provenance",
        "plugin-install-check",
        "validate",
        "inspect",
        "ruff",
        "yamllint",
    ),
    "policy": ("opa-test", "opa-policy", "opa-artifact"),
    "docs-check": ("docs-diff", "docs-layout", "adr-schema"),
    "ci": ("lint", "test", "workflow-helper-tests", "policy", "docs-check", "manifest-check"),
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
