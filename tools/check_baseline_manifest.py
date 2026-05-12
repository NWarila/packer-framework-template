"""Validate baseline-manifest.json without importing drift-gate."""

from __future__ import annotations

import json
from pathlib import Path, PurePosixPath
from typing import Any


def fail(message: str) -> None:
    raise SystemExit(f"manifest-check: {message}")


def manifest_path(field: str, value: Any) -> str:
    if not isinstance(value, str) or not value:
        fail(f"{field} must be a non-empty string")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        fail(f"{field} must be repo-rooted and must not contain '..': {value!r}")
    return value


def require_keys(raw: dict[str, Any], expected: set[str]) -> None:
    keys = set(raw)
    if keys != expected:
        fail(f"root must contain exactly {sorted(expected)!r}")


def validate_entries(field: str, entries: Any, *, allow_empty: bool) -> tuple[list[str], set[str]]:
    if not isinstance(entries, list) or (not entries and not allow_empty):
        fail(f"'{field}' must be a {'possibly empty ' if allow_empty else ''}list")

    sources: list[str] = []
    targets: set[str] = set()
    for idx, item in enumerate(entries):
        if not isinstance(item, dict) or set(item) != {"source", "target"}:
            fail(f"{field}[{idx}] must contain exactly 'source' and 'target'")
        source = manifest_path(f"{field}[{idx}].source", item["source"])
        target = manifest_path(f"{field}[{idx}].target", item["target"])
        if target in targets:
            fail(f"duplicate target path: {target!r}")
        sources.append(source)
        targets.add(target)
    return sources, targets


def main() -> None:
    try:
        raw = json.loads(Path("baseline-manifest.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"baseline-manifest.json is not valid JSON: {exc}")
    if not isinstance(raw, dict) or "version" not in raw:
        fail("root must be an object with a 'version' field")
    if raw["version"] not in {"1", "2"}:
        fail(f"unsupported manifest version: {raw['version']!r}")

    if raw["version"] == "1":
        require_keys(raw, {"version", "files"})
        byte_identical_sources, byte_identical_targets = validate_entries(
            "files", raw["files"], allow_empty=False
        )
        scaffold_sources: list[str] = []
        scaffold_targets: set[str] = set()
    else:
        require_keys(raw, {"version", "byte_identical", "scaffold_starter"})
        byte_identical_sources, byte_identical_targets = validate_entries(
            "byte_identical", raw["byte_identical"], allow_empty=False
        )
        scaffold_sources, scaffold_targets = validate_entries(
            "scaffold_starter", raw["scaffold_starter"], allow_empty=True
        )

    duplicate_targets = sorted(byte_identical_targets & scaffold_targets)
    if duplicate_targets:
        fail(f"target path listed in multiple categories: {duplicate_targets}")

    sources = byte_identical_sources + scaffold_sources

    missing = [source for source in sources if not Path(source).is_file()]
    if missing:
        fail(f"sources missing: {missing}")
    print(
        f"manifest: version={raw['version']}, "
        f"byte_identical={len(byte_identical_sources)}, "
        f"scaffold_starter={len(scaffold_sources)}"
    )
    print("all sources resolve on disk")


if __name__ == "__main__":
    main()
