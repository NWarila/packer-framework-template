#!/usr/bin/env python3
"""Run a credential-free Packer integration case and assert its evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from _config import load_ci_config, select_case


def run(command: list[str], cwd: Path) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def read_json(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return raw


def assert_case_outputs(repo_root: Path, case: dict[str, Any]) -> None:
    image_key = case["expected_image_key"]
    output_file = case["expected_output_file"]
    artifact = repo_root / "packer" / "artifacts" / image_key / output_file
    build_context = repo_root / "packer" / "artifacts" / image_key / "build-context.json"
    builder_contract = repo_root / "packer" / "artifacts" / image_key / "builder-contract.json"
    manifest = repo_root / "packer" / "manifests" / f"{image_key}.json"

    for path in (artifact, build_context, builder_contract, manifest):
        if not path.is_file():
            raise FileNotFoundError(f"expected integration evidence missing: {path}")

    content = artifact.read_text(encoding="utf-8")
    for expected in case.get("expected_content", []):
        if expected not in content:
            raise ValueError(f"{artifact} missing expected content: {expected!r}")

    context = read_json(build_context)
    if context.get("image_key") != image_key:
        raise ValueError(f"{build_context} image_key mismatch")
    if context.get("secret_seed_id") == "reference-only":
        raise ValueError(f"{build_context} leaked the raw secret_seed value")

    contract = read_json(builder_contract)
    if contract.get("image_key") != image_key:
        raise ValueError(f"{builder_contract} image_key mismatch")
    if not contract.get("http_directory") or not contract.get("cd_files"):
        raise ValueError(f"{builder_contract} must declare builder wiring paths")

    manifest_json = read_json(manifest)
    builds = manifest_json.get("builds")
    if not isinstance(builds, list) or not builds:
        raise ValueError(f"{manifest} must contain at least one build")
    custom_data = builds[-1].get("custom_data", {})
    if custom_data.get("image_key") != image_key:
        raise ValueError(f"{manifest} custom_data.image_key mismatch")
    if custom_data.get("secret_seed_id") == "reference-only":
        raise ValueError(f"{manifest} leaked the raw secret_seed value")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to cwd.")
    parser.add_argument("--config", default="tools/ci/config.toml", help="Path to CI config.")
    parser.add_argument("--case", default=None, help="Integration case name.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    config = load_ci_config(repo_root, args.config)
    case = select_case(config, args.case)
    packer_root = config.get("packer_root", "packer")
    var_file = case["var_file"]

    run(["packer", "fmt", "-check", "-recursive", "packer", "examples"], repo_root)
    run(["packer", "init", packer_root], repo_root)
    run(["packer", "validate", "-var-file", var_file, packer_root], repo_root)
    run(["packer", "inspect", packer_root], repo_root)
    if case.get("build", True):
        run(["packer", "build", "-force", "-var-file", var_file, packer_root], repo_root)
        assert_case_outputs(repo_root, case)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
    except Exception as exc:
        print(f"run_integration.py: {exc}", file=sys.stderr)
        sys.exit(1)
