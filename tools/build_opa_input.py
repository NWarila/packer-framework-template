#!/usr/bin/env python3
"""Build OPA input from this repository's real files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


USES_LINE_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*(.+?)\s*(?:#.*)?$")
WORKFLOW_GLOBS = ("*.yml", "*.yaml")
POLICY_FILE_PATHS = ("packer/packer.pkr.hcl",)


def normalize_uses(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value.strip()


def collect_workflow_uses(repo_root: Path) -> dict[str, list[dict[str, Any]]]:
    workflows_dir = repo_root / ".github" / "workflows"
    workflows: dict[str, list[dict[str, Any]]] = {}
    if not workflows_dir.is_dir():
        return workflows

    paths: list[Path] = []
    for pattern in WORKFLOW_GLOBS:
        paths.extend(workflows_dir.glob(pattern))

    for path in sorted(set(paths)):
        refs: list[dict[str, Any]] = []
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = USES_LINE_RE.match(line)
            if match:
                refs.append({"line": line_no, "uses": normalize_uses(match.group(1))})
        if refs:
            workflows[path.relative_to(repo_root).as_posix()] = refs
    return workflows


def collect_files(repo_root: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in POLICY_FILE_PATHS:
        path = repo_root / rel
        if path.is_file():
            files[rel] = path.read_text(encoding="utf-8")

    workflows_dir = repo_root / ".github" / "workflows"
    if workflows_dir.is_dir():
        paths: list[Path] = []
        for pattern in WORKFLOW_GLOBS:
            paths.extend(workflows_dir.glob(pattern))
        for path in sorted(set(paths)):
            files[path.relative_to(repo_root).as_posix()] = path.read_text(encoding="utf-8")
    return files


def build_input(repo_root: Path) -> dict[str, Any]:
    return {
        "workflows": collect_workflow_uses(repo_root),
        "files": collect_files(repo_root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root to inspect (default: current working directory).",
    )
    args = parser.parse_args()

    json.dump(build_input(args.repo_root.resolve()), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
