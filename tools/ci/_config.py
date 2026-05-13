"""Shared CI configuration helpers."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

if sys.version_info < (3, 11):
    raise SystemExit("Python 3.11+ required (tomllib)")

import tomllib  # noqa: E402


def load_ci_config(
    repo_root: Path, config_path: str = "tools/ci/config.toml"
) -> dict[str, Any]:
    with (repo_root / config_path).resolve().open("rb") as handle:
        return tomllib.load(handle)


def select_case(config: dict[str, Any], requested: str | None) -> dict[str, Any]:
    name = requested or config.get("default_case")
    for case in config.get("cases", []):
        if case["name"] == name:
            return case
    raise ValueError(f"CI case not found: {name}")
