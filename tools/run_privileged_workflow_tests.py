#!/usr/bin/env python3
"""Drive check_privileged_workflows.py against good and bad fixtures.

Mirrors the run_contract_tests.py convention: each subdirectory of
``tests/fixtures/privileged-workflows/`` is a miniature repo layout with
its own ``.github/workflows/``. The runner asserts the validator's exit
code and the presence of expected ``[FAIL]`` markers per fixture.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Fixture:
    name: str
    should_pass: bool
    expected_failures: tuple[str, ...] = field(default_factory=tuple)


# Each ``expected_failures`` entry is a substring asserted to appear in the
# validator's stdout for that fixture. Substrings, not full lines, so the
# tests stay robust against detail-message tweaks.
FIXTURES: tuple[Fixture, ...] = (
    Fixture(name="good", should_pass=True),
    Fixture(
        name="bad",
        should_pass=False,
        expected_failures=(
            "actions/checkout is not allowed",
            "checkout ref references PR-controlled content",
        ),
    ),
    Fixture(
        name="reusable-bad",
        should_pass=False,
        expected_failures=(
            "reachable from .github/workflows/caller.yaml",
            "actions/checkout is not allowed",
        ),
    ),
)


@dataclass
class Result:
    fixture: Fixture
    returncode: int
    stdout: str
    stderr: str
    passed: bool
    detail: str


def run_fixture(validator: Path, fixtures_root: Path, fixture: Fixture) -> Result:
    fixture_root = fixtures_root / fixture.name
    completed = subprocess.run(
        [sys.executable, str(validator), "--repo-root", str(fixture_root)],
        capture_output=True,
        text=True,
        check=False,
    )

    if fixture.should_pass:
        passed = completed.returncode == 0
        detail = "expected clean exit"
        if not passed:
            detail = f"expected exit 0, got {completed.returncode}"
    else:
        missing = [
            needle
            for needle in fixture.expected_failures
            if needle not in completed.stdout
        ]
        passed = completed.returncode == 1 and not missing
        if completed.returncode == 0:
            detail = "expected non-zero exit, got 0"
        elif missing:
            detail = "missing expected marker(s): " + ", ".join(repr(m) for m in missing)
        else:
            detail = "expected failure markers present"

    return Result(
        fixture=fixture,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        passed=passed,
        detail=detail,
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validator",
        type=Path,
        default=repo_root / "tools" / "check_privileged_workflows.py",
    )
    parser.add_argument(
        "--fixtures-root",
        type=Path,
        default=repo_root / "tests" / "fixtures" / "privileged-workflows",
    )
    args = parser.parse_args()

    validator = args.validator.resolve()
    fixtures_root = args.fixtures_root.resolve()
    if not validator.is_file():
        sys.stderr.write(f"error: validator not found: {validator}\n")
        return 2
    if not fixtures_root.is_dir():
        sys.stderr.write(f"error: fixtures root not found: {fixtures_root}\n")
        return 2

    results = [run_fixture(validator, fixtures_root, f) for f in FIXTURES]
    for result in results:
        marker = "PASS" if result.passed else "FAIL"
        print(
            f"[{marker}] {result.fixture.name}: {result.detail} "
            f"(exit {result.returncode})"
        )
        if not result.passed:
            if result.stdout.strip():
                print(f"--- {result.fixture.name} stdout ---")
                print(result.stdout.rstrip())
            if result.stderr.strip():
                print(f"--- {result.fixture.name} stderr ---")
                print(result.stderr.rstrip())

    failures = sum(1 for r in results if not r.passed)
    print(f"summary: {len(results) - failures} passed, {failures} failed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
