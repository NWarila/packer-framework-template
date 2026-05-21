#!/usr/bin/env python3
"""Static check for pull_request_target workflow safety.

Flags privileged workflows -- those triggered by ``pull_request_target`` --
that checkout or execute PR-controlled code, including via local reusable
workflows.

``pull_request_target`` grants the workflow access to repository secrets and
a write-capable ``GITHUB_TOKEN`` while running in the base repository's
context. Combining that privilege with executing PR-controlled code is a
documented GitHub Actions supply-chain footgun
(https://securitylab.github.com/research/github-actions-preventing-pwn-requests/).

Exit codes:
    0 - clean
    1 - findings
    2 - setup error
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


PR_HEAD_TOKENS = (
    "github.event.pull_request.head",
    "github.head_ref",
    "refs/pull/",
)
CHECKOUT_RE = re.compile(r"^actions/checkout(?:@.*)?$")


@dataclass(frozen=True)
class Finding:
    path: Path
    detail: str
    via: Path | None = None


def _load_yaml(path: Path):
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _on_section(doc: dict):
    # PyYAML safe_load treats the bare key ``on:`` as boolean True under
    # YAML 1.1 truthy semantics, so we check both keys.
    if "on" in doc:
        return doc["on"]
    if True in doc:
        return doc[True]
    return None


def triggers_pull_request_target(doc: dict) -> bool:
    on = _on_section(doc)
    if on is None:
        return False
    if isinstance(on, str):
        return on == "pull_request_target"
    if isinstance(on, list):
        return "pull_request_target" in on
    if isinstance(on, dict):
        return "pull_request_target" in on
    return False


def references_pr_head(value: str) -> bool:
    return any(token in value for token in PR_HEAD_TOKENS)


def resolve_local_reusable(uses: str, repo_root: Path) -> Path | None:
    if not uses.startswith("./"):
        return None
    candidate = (repo_root / uses[2:]).resolve()
    return candidate if candidate.is_file() else None


def iter_steps(job: dict):
    for step in job.get("steps") or []:
        if isinstance(step, dict):
            yield step


def scan_workflow(
    path: Path,
    repo_root: Path,
    *,
    chain: tuple[Path, ...] = (),
    cache: dict[Path, list[Finding]] | None = None,
) -> list[Finding]:
    if cache is not None and path in cache:
        return list(cache[path])

    findings: list[Finding] = []
    try:
        doc = _load_yaml(path)
    except Exception as exc:  # pragma: no cover - surfaced as a finding
        findings.append(Finding(path, f"yaml parse error: {exc}"))
        if cache is not None:
            cache[path] = findings
        return findings

    for job_name, job in (doc.get("jobs") or {}).items():
        if not isinstance(job, dict):
            continue

        job_uses = job.get("uses")
        if isinstance(job_uses, str):
            sub = resolve_local_reusable(job_uses, repo_root)
            if sub and sub not in chain:
                for sub_finding in scan_workflow(
                    sub, repo_root, chain=chain + (path,), cache=cache
                ):
                    findings.append(
                        Finding(sub_finding.path, sub_finding.detail, via=path)
                    )

        for step in iter_steps(job):
            uses = step.get("uses")
            if isinstance(uses, str) and CHECKOUT_RE.match(uses):
                findings.append(
                    Finding(
                        path,
                        f"job '{job_name}': actions/checkout is not allowed "
                        "in a pull_request_target workflow",
                    )
                )
                step_with = step.get("with") or {}
                ref = step_with.get("ref")
                if isinstance(ref, str) and references_pr_head(ref):
                    findings.append(
                        Finding(
                            path,
                            f"job '{job_name}': checkout ref references "
                            f"PR-controlled content ({ref!r})",
                        )
                    )

            run_block = step.get("run")
            if isinstance(run_block, str) and references_pr_head(run_block):
                findings.append(
                    Finding(
                        path,
                        f"job '{job_name}': run block references "
                        "PR-controlled content (github.event.pull_request.head / "
                        "github.head_ref / refs/pull/)",
                    )
                )

    if cache is not None:
        cache[path] = findings
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--workflows-dir",
        type=Path,
        default=None,
        help="Directory of workflows to scan (default: <repo-root>/.github/workflows).",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    workflows_dir = (args.workflows_dir or repo_root / ".github" / "workflows").resolve()
    if not workflows_dir.is_dir():
        sys.stderr.write(f"error: workflow directory not found: {workflows_dir}\n")
        return 2

    paths = sorted(workflows_dir.glob("*.yml")) + sorted(workflows_dir.glob("*.yaml"))

    privileged: list[Path] = []
    for path in paths:
        try:
            doc = _load_yaml(path)
        except Exception:
            continue
        if triggers_pull_request_target(doc):
            privileged.append(path)

    cache: dict[Path, list[Finding]] = {}
    all_findings: list[Finding] = []
    for path in privileged:
        all_findings.extend(scan_workflow(path, repo_root, cache=cache))

    for finding in all_findings:
        rel = finding.path.relative_to(repo_root).as_posix()
        via = ""
        if finding.via is not None:
            via_rel = finding.via.relative_to(repo_root).as_posix()
            via = f" (reachable from {via_rel})"
        print(f"[FAIL] {rel}{via} - {finding.detail}")

    if all_findings:
        print(
            f"summary: {len(all_findings)} issue(s) across "
            f"{len(privileged)} privileged workflow(s)"
        )
        return 1

    print(
        f"summary: scanned {len(privileged)} pull_request_target workflow(s); "
        "no PR-content access detected"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
