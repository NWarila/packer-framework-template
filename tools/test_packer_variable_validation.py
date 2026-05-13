#!/usr/bin/env python3
"""Regression tests for Packer variable validation blocks."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKER = os.environ.get("PACKER", "packer")


def base_payload() -> dict[str, Any]:
    return {
        "selected_image": "reference-linux",
        "images": {
            "reference-linux": {
                "os_family": "linux",
                "os_name": "reference-linux",
                "os_version": "0.1.0",
                "architecture": "x86_64",
                "tags": ["reference", "linux"],
                "install_template": {
                    "template_path": "examples/linux/cloud-init.pkrtpl.hcl",
                    "output_file": "user-data",
                    "vars": {
                        "hostname": "reference-linux",
                        "username": "platform",
                    },
                },
                "metadata": {
                    "owner": "platform",
                    "purpose": "validation-regression-test",
                },
            }
        },
    }


def validate(payload: dict[str, Any], workspace: Path) -> subprocess.CompletedProcess[str]:
    var_file = workspace / "case.pkrvars.json"
    var_file.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return subprocess.run(
        [PACKER, "validate", "-var-file", str(var_file), "packer"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def with_mutation(mutator: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
    payload = copy.deepcopy(base_payload())
    mutator(payload)
    return payload


def assert_invalid(
    workspace: Path,
    name: str,
    mutator: Callable[[dict[str, Any]], None],
    expected: str,
) -> None:
    completed = validate(with_mutation(mutator), workspace)
    output = (completed.stdout + completed.stderr).lower()
    if completed.returncode == 0:
        raise AssertionError(f"{name} unexpectedly passed validation")
    if expected.lower() not in output:
        raise AssertionError(f"{name} did not report {expected!r}; output was:\n{output}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="packer-validation-") as raw_tmp:
        workspace = Path(raw_tmp)
        valid = validate(base_payload(), workspace)
        if valid.returncode != 0:
            raise AssertionError(valid.stdout + valid.stderr)

        assert_invalid(
            workspace,
            "artifact_root traversal",
            lambda data: data.update({"artifact_root": "../outside"}),
            "Artifact_root",
        )
        assert_invalid(
            workspace,
            "manifest_dir absolute path",
            lambda data: data.update({"manifest_dir": "/tmp/manifests"}),
            "Manifest_dir",
        )
        assert_invalid(
            workspace,
            "template_path traversal",
            lambda data: data["images"]["reference-linux"]["install_template"].update(
                {"template_path": "../examples/linux/cloud-init.pkrtpl.hcl"}
            ),
            "install_template.template_path",
        )
        assert_invalid(
            workspace,
            "output_file quote injection",
            lambda data: data["images"]["reference-linux"]["install_template"].update(
                {"output_file": "user-data'; import os"}
            ),
            "install_template.output_file",
        )
        assert_invalid(
            workspace,
            "unsupported os_family",
            lambda data: data["images"]["reference-linux"].update({"os_family": "solaris"}),
            "os_family",
        )

    print("packer variable validation tests passed")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
    except Exception as exc:
        print(f"test_packer_variable_validation.py: {exc}", file=sys.stderr)
        sys.exit(1)
