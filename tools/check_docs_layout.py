#!/usr/bin/env python3
"""Enforce repository documentation layout.

This checks placement only. It intentionally does not try to judge prose quality.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
ALLOWED_DOCS_ROOT = {DOCS / "README.md"}
ALLOWED_SUBTREES = {
    DOCS / "tutorials",
    DOCS / "how-to",
    DOCS / "reference",
    DOCS / "runbooks",
    DOCS / "explanation",
    DOCS / "decision-records",
}
ADR_ROOT = DOCS / "decision-records"
ADR_ALLOWED_SUBTREES = {
    ADR_ROOT / "org",
    ADR_ROOT / "template",
    ADR_ROOT / "repo",
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def is_under(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def main() -> int:
    errors: list[str] = []

    if not DOCS.exists():
        errors.append("docs/ does not exist")
        return report(errors)

    markdown_files = sorted(DOCS.rglob("*.md"))

    for md in markdown_files:
        if md.parent == DOCS and md not in ALLOWED_DOCS_ROOT:
            errors.append(f"{rel(md)} is a docs-root Markdown file; only docs/README.md is allowed")

        if md not in ALLOWED_DOCS_ROOT and not any(is_under(md, subtree) for subtree in ALLOWED_SUBTREES):
            errors.append(f"{rel(md)} is outside the allowed Diataxis/ADR subtrees")

    if ADR_ROOT.exists():
        for md in sorted(ADR_ROOT.rglob("*.md")):
            if md == ADR_ROOT / "README.md":
                continue
            if not any(is_under(md, subtree) for subtree in ADR_ALLOWED_SUBTREES):
                errors.append(f"{rel(md)} is an ADR outside docs/decision-records/org/, template/, or repo/")

    readme = DOCS / "README.md"
    if not readme.exists():
        errors.append("docs/README.md is missing")
    else:
        readme_text = readme.read_text(encoding="utf-8")
        quadrants = {
            "tutorials": DOCS / "tutorials",
            "how-to": DOCS / "how-to",
            "reference": DOCS / "reference",
            "explanation": DOCS / "explanation",
        }
        for name, path in quadrants.items():
            populated = path.exists() and any(path.rglob("*.md"))
            if populated and f"{name}/" not in readme_text:
                errors.append(f"docs/README.md does not link to populated quadrant docs/{name}/")

        if ADR_ROOT.exists() and "decision-records/" not in readme_text:
            errors.append("docs/README.md does not mention ADR location docs/decision-records/")

    return report(errors)


def report(errors: list[str]) -> int:
    if errors:
        print("docs layout check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("docs layout check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
