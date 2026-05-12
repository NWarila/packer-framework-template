#!/usr/bin/env python3
"""Validate ADR section schema and decision-record index drift."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR_ROOT = ROOT / "docs" / "decision-records"
ADR_SCOPES = ("org", "template", "repo")
ADR_FILE_RE = re.compile(r"^[0-9]{4}-.*\.md$")
H2_RE = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
INDEX_LINK_RE = re.compile(
    r"\((?P<target>(?:org|template|repo)/[0-9]{4}-[^)#\s]+\.md)\)"
)

REQUIRED_SECTIONS = (
    "TL;DR",
    "Context and Problem Statement",
    "Decision Drivers",
    "Considered Options",
    "Decision Outcome",
    "Pros and Cons of the Options",
    "Confirmation",
    "Consequences",
    "Assumptions",
    "Supersedes",
    "Superseded by",
    "Implementing PRs",
    "Related ADRs",
    "Compliance Notes",
)


def adr_files() -> list[Path]:
    files: list[Path] = []
    for scope in ADR_SCOPES:
        scope_dir = ADR_ROOT / scope
        if not scope_dir.is_dir():
            continue
        files.extend(
            sorted(path for path in scope_dir.glob("*.md") if ADR_FILE_RE.match(path.name))
        )
    return files


def rel(path: Path) -> str:
    return path.relative_to(ADR_ROOT).as_posix()


def check_schema(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    headings = [match.group(1).strip() for match in H2_RE.finditer(text)]
    errors: list[str] = []

    missing = [section for section in REQUIRED_SECTIONS if section not in headings]
    if missing:
        errors.append(f"{rel(path)} missing section(s): {', '.join(missing)}")
        return errors

    positions = [headings.index(section) for section in REQUIRED_SECTIONS]
    if positions != sorted(positions):
        errors.append(f"{rel(path)} required sections are not in ADR-0001 order")
    return errors


def check_index(files: list[Path]) -> list[str]:
    index = ADR_ROOT / "README.md"
    if not index.is_file():
        return ["docs/decision-records/README.md is missing"]

    text = index.read_text(encoding="utf-8")
    indexed = {match.group("target") for match in INDEX_LINK_RE.finditer(text)}
    actual = {rel(path) for path in files}
    errors: list[str] = []

    for missing in sorted(actual - indexed):
        errors.append(f"docs/decision-records/README.md missing ADR row for {missing}")
    for stale in sorted(indexed - actual):
        errors.append(f"docs/decision-records/README.md links to missing ADR {stale}")
    return errors


def main() -> int:
    files = adr_files()
    errors: list[str] = []
    for path in files:
        errors.extend(check_schema(path))
    errors.extend(check_index(files))

    if errors:
        print("ADR schema/index check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"ADR schema/index check passed: {len(files)} ADRs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
