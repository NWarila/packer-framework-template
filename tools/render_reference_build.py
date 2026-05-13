#!/usr/bin/env python3
"""Render reference Packer build files from a validated environment payload."""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path
from typing import Any


REQUEST_ENV = "PACKER_RENDER_REQUEST_B64"
FORBIDDEN_PATH_CHARS = {"'", '"', "\n", "\r"}


def fail(message: str) -> None:
    raise SystemExit(f"render_reference_build.py: {message}")


def decode_request() -> dict[str, Any]:
    raw = os.environ.get(REQUEST_ENV)
    if not raw:
        fail(f"{REQUEST_ENV} is required")
    raw = "".join(raw.strip().strip('"').split())
    try:
        decoded = base64.b64decode(raw, validate=True).decode("utf-8")
        payload = json.loads(decoded)
    except (ValueError, json.JSONDecodeError) as exc:
        fail(f"{REQUEST_ENV} is not valid base64 JSON: {exc}")
    if not isinstance(payload, dict):
        fail("request payload must be a JSON object")
    return payload


def resolve_repo_path(repo_root: Path, raw_path: object, label: str) -> Path:
    if not isinstance(raw_path, str) or not raw_path:
        fail(f"{label} must be a non-empty string")
    if any(char in raw_path for char in FORBIDDEN_PATH_CHARS):
        fail(f"{label} contains a quote or line break")

    resolved = Path(raw_path).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError:
        fail(f"{label} must resolve under repository root: {raw_path}")
    return resolved


def write_outputs(payload: dict[str, Any]) -> list[Path]:
    repo_root = resolve_repo_path(Path.cwd().resolve(), payload.get("repo_root"), "repo_root")
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        fail("files must be a non-empty list")

    written: list[Path] = []
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            fail(f"files[{index}] must be an object")
        output_path = resolve_repo_path(repo_root, item.get("path"), f"files[{index}].path")
        content_b64 = item.get("content_b64")
        if not isinstance(content_b64, str):
            fail(f"files[{index}].content_b64 must be a string")
        try:
            content = base64.b64decode(content_b64, validate=True)
        except ValueError as exc:
            fail(f"files[{index}].content_b64 is not valid base64: {exc}")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(content)
        written.append(output_path)
    return written


def main() -> int:
    payload = decode_request()
    image_key = payload.get("image_key", "unknown")
    written = write_outputs(payload)
    print(f"Rendered {len(written)} reference build file(s) for {image_key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
