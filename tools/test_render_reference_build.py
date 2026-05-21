#!/usr/bin/env python3
"""Unit tests for the reference Packer render helper."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "render_reference_build.py"
REQUEST_ENV = "PACKER_RENDER_REQUEST_B64"


def encode_request(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def run_helper(payload: dict[str, Any], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env[REQUEST_ENV] = encode_request(payload)
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def assert_success(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise AssertionError(f"expected success, got {result.returncode}: {result.stderr}")


def assert_failure(result: subprocess.CompletedProcess[str], expected: str) -> None:
    if result.returncode == 0:
        raise AssertionError("expected failure")
    if expected not in result.stderr:
        raise AssertionError(f"expected {expected!r} in stderr, got {result.stderr!r}")


def test_writes_requested_files(repo_root: Path) -> None:
    payload = {
        "repo_root": str(repo_root),
        "image_key": "reference-linux",
        "files": [
            {
                "path": str(repo_root / "packer" / "artifacts" / "reference-linux" / "user-data"),
                "content_b64": base64.b64encode(b"#cloud-config\n").decode("ascii"),
            },
            {
                "path": str(
                    repo_root / "packer" / "artifacts" / "reference-linux" / "build-context.json"
                ),
                "content_b64": base64.b64encode(b'{"image_key":"reference-linux"}\n').decode(
                    "ascii"
                ),
            },
        ],
    }

    result = run_helper(payload, cwd=repo_root)
    assert_success(result)
    assert (repo_root / "packer" / "artifacts" / "reference-linux" / "user-data").is_file()
    assert "Rendered 2 reference build file(s) for reference-linux" in result.stdout


def test_rejects_paths_outside_repo(repo_root: Path, tmp_root: Path) -> None:
    payload = {
        "repo_root": str(repo_root),
        "image_key": "bad",
        "files": [
            {
                "path": str(tmp_root / "outside.txt"),
                "content_b64": base64.b64encode(b"bad").decode("ascii"),
            }
        ],
    }

    result = run_helper(payload, cwd=repo_root)
    assert_failure(result, "must resolve under repository root")


def test_rejects_quote_in_path(repo_root: Path) -> None:
    payload = {
        "repo_root": str(repo_root),
        "image_key": "bad",
        "files": [
            {
                "path": str(repo_root / "packer" / "artifacts" / "bad'quote"),
                "content_b64": base64.b64encode(b"bad").decode("ascii"),
            }
        ],
    }

    result = run_helper(payload, cwd=repo_root)
    assert_failure(result, "contains a quote or line break")


def test_golden_minimal_render(repo_root: Path) -> None:
    """Snapshot test: rendered files must byte-match committed golden fixtures.

    Regression detector for the renderer's path-resolution and write path.
    If the renderer behavior legitimately changes, regenerate the golden
    files in tests/fixtures/render-golden/minimal/expected/ and re-commit.
    """
    fixture_root = ROOT / "tests" / "fixtures" / "render-golden" / "minimal"
    request_template = json.loads((fixture_root / "request.json").read_text(encoding="utf-8"))
    expected_dir = fixture_root / "expected"

    repo_str = str(repo_root)

    def substitute(value: Any) -> Any:
        if isinstance(value, str):
            return value.replace("__REPO_ROOT__", repo_str)
        if isinstance(value, list):
            return [substitute(v) for v in value]
        if isinstance(value, dict):
            return {k: substitute(v) for k, v in value.items()}
        return value

    payload = substitute(request_template)
    result = run_helper(payload, cwd=repo_root)
    assert_success(result)

    for expected_file in sorted(expected_dir.rglob("*")):
        if expected_file.is_dir():
            continue
        rel = expected_file.relative_to(expected_dir)
        actual = repo_root / "packer" / "artifacts" / "reference-minimal" / rel
        if not actual.is_file():
            raise AssertionError(f"golden file missing in rendered output: {rel}")
        if actual.read_bytes() != expected_file.read_bytes():
            raise AssertionError(
                f"golden mismatch for {rel}: "
                f"rendered {len(actual.read_bytes())} bytes != "
                f"expected {len(expected_file.read_bytes())} bytes"
            )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp).resolve()
        repo_root = tmp_root / "repo"
        repo_root.mkdir()
        test_writes_requested_files(repo_root)
        test_rejects_paths_outside_repo(repo_root, tmp_root)
        test_rejects_quote_in_path(repo_root)
    with tempfile.TemporaryDirectory() as tmp:
        repo_root = Path(tmp).resolve()
        test_golden_minimal_render(repo_root)
    print("render_reference_build.py tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
