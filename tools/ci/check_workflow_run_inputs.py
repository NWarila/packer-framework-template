#!/usr/bin/env python3
"""Reject workflow_call inputs interpolated directly inside shell run blocks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


INPUT_EXPR = "${{ inputs."
RUN_LINE = re.compile(r"^(?P<indent>\s*)(?:-\s*)?run:\s*(?P<value>.*)$")


def iter_workflows(paths: list[str]) -> list[Path]:
    workflows: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_dir():
            workflows.extend(sorted(path.glob("*.yaml")))
            workflows.extend(sorted(path.glob("*.yml")))
        else:
            workflows.append(path)
    return workflows


def indentation(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def scan_workflow(path: Path) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    failures: list[str] = []
    active_run_indent: int | None = None

    for index, line in enumerate(lines, start=1):
        if active_run_indent is not None:
            if line.strip() and indentation(line) <= active_run_indent:
                active_run_indent = None
            elif INPUT_EXPR in line:
                failures.append(f"{path}:{index}: {line.strip()}")

        match = RUN_LINE.match(line)
        if match is None:
            continue

        run_indent = len(match.group("indent"))
        inline_value = match.group("value").strip()
        if INPUT_EXPR in inline_value:
            failures.append(f"{path}:{index}: {line.strip()}")

        if inline_value in {"|", "|-", "|+", ">", ">-", ">+"}:
            active_run_indent = run_indent

    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Workflow YAML files or directories to scan.")
    args = parser.parse_args()

    failures: list[str] = []
    for workflow in iter_workflows(args.paths):
        failures.extend(scan_workflow(workflow))

    if failures:
        print("workflow run-block input interpolation is not allowed:", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        print("Bind workflow inputs through env: and read the environment variable in shell.", file=sys.stderr)
        return 1

    print("workflow run blocks do not interpolate inputs directly")
    return 0


if __name__ == "__main__":
    sys.exit(main())
