#!/usr/bin/env python3
"""Build OPA input from generated Packer manifests and rendered artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


MAX_TEXT_BYTES = 512 * 1024


def read_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return raw


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def collect_manifests(repo_root: Path, manifests_root: Path) -> list[dict[str, Any]]:
    manifests: list[dict[str, Any]] = []
    if not manifests_root.is_dir():
        return manifests
    for path in sorted(manifests_root.glob("*.json")):
        manifest = read_json(path)
        manifest["path"] = rel(path, repo_root)
        manifests.append(manifest)
    return manifests


def collect_rendered_templates(repo_root: Path, artifacts_root: Path) -> list[dict[str, str]]:
    rendered: list[dict[str, str]] = []
    if not artifacts_root.is_dir():
        return rendered
    for path in sorted(item for item in artifacts_root.rglob("*") if item.is_file()):
        if path.name == ".gitkeep" or path.name == "build-context.json":
            continue
        data = path.read_bytes()
        if len(data) > MAX_TEXT_BYTES:
            continue
        rendered.append(
            {
                "path": rel(path, repo_root),
                "image_key": path.parent.name,
                "content": data.decode("utf-8", errors="replace"),
            }
        )
    return rendered


def build_input(repo_root: Path, artifacts_root: Path, manifests_root: Path) -> dict[str, Any]:
    return {
        "manifests": collect_manifests(repo_root, manifests_root),
        "rendered_templates": collect_rendered_templates(repo_root, artifacts_root),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--artifacts-root", default="packer/artifacts")
    parser.add_argument("--manifests-root", default="packer/manifests")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    payload = build_input(
        repo_root,
        (repo_root / args.artifacts_root).resolve(),
        (repo_root / args.manifests_root).resolve(),
    )
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
