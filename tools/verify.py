#!/usr/bin/env python3
"""Cross-platform verification entrypoint for the Packer framework template."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path


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


def build_steps() -> dict[str, Step]:
    return {
        "fmt": lambda: run(["packer", "fmt", "-recursive", "packer", "examples"]),
        "fmt-check": lambda: run(
            ["packer", "fmt", "-check", "-recursive", "packer", "examples"]
        ),
        "init": lambda: run(["packer", "init", "packer"]),
        "validate": lambda: run(
            ["packer", "validate", "-var-file=examples/linux/reference-linux.pkrvars.hcl", "packer"]
        ),
        "inspect": lambda: run(["packer", "inspect", "packer"]),
        "ruff": lambda: (
            install("ruff==0.13.0"),
            run([PYTHON, "-m", "ruff", "check", "tools/"]),
        ),
        "yamllint": lambda: (
            install("yamllint==1.35.1"),
            run([PYTHON, "-m", "yamllint", "-d", YAMLLINT_CONFIG, ".github/workflows/"]),
        ),
        "opa-test": lambda: run(["opa", "test", "policies/opa"]),
        "opa-policy": opa_policy,
        "manifest-check": lambda: run([PYTHON, "tools/check_baseline_manifest.py"]),
        "docs-layout": lambda: run([PYTHON, "tools/check_docs_layout.py"]),
        "adr-schema": lambda: run([PYTHON, "tools/check_adr_schema.py"]),
        "integration": lambda: run(
            ["packer", "build", "-force", "-var-file=examples/linux/reference-linux.pkrvars.hcl", "packer"]
        ),
    }


TARGETS: dict[str, tuple[str, ...]] = {
    "lint": ("fmt-check", "init", "validate", "inspect", "ruff", "yamllint"),
    "policy": ("opa-test", "opa-policy"),
    "docs-check": ("docs-layout", "adr-schema"),
    "ci": ("lint", "policy", "docs-check", "manifest-check"),
    "verify": ("ci", "integration"),
}


def execute(name: str, steps: dict[str, Step]) -> None:
    if name in TARGETS:
        for child in TARGETS[name]:
            execute(child, steps)
        return
    steps[name]()


def main() -> int:
    steps = build_steps()
    choices = sorted(set(TARGETS) | set(steps))
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default="verify", choices=choices)
    args = parser.parse_args()

    execute(args.target, steps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
