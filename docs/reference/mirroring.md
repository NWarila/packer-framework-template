# Mirroring And Consumer Baseline

This template is intentionally split into shared repo-quality baseline and Packer implementation layers so derivative image frameworks can stay easy to adapt without losing platform controls.

## Required Shared Baseline

Derivative Packer frameworks should mirror the files listed under `byte_identical` in [`baseline-manifest.json`](../../baseline-manifest.json). That set is the stable scaffold: repository hygiene, docs layout checks, security callers, Packer-oriented Renovate rules, universal OPA policy, and the Python verification entrypoint.

The manifest is intentionally narrower than a full repo copy. It does not require downstream frameworks to keep the reference `null` source or the starter examples byte-identical.

## Framework-Owned Layer

The `packer/` implementation, examples, provider choices, and repo-tier ADRs are allowed to diverge. This reference uses the `null` builder so the pattern is visible without infrastructure; real frameworks replace that source with provider-specific builders while preserving the same validation interface.

## Optional Release Layer

`release.yaml`, release-please config, release evidence, and trusted-bot auto-merge are supported by this template, but downstream frameworks do not have to mirror them byte-for-byte. Keep that layer when the repo publishes versioned releases or framework evidence. Drop it when the repo is only a private implementation detail.

Push-triggered release-please is opt-in through `RELEASE_PLEASE_ON_PUSH=true` because GitHub requires an explicit repository setting before Actions can create release PRs.

## New Framework Checklist

1. Rewrite `README.md` for the real framework.
2. Replace the `null` source under `packer/`.
3. Update examples for supported guest OS families.
4. Add provider-specific threat model notes under `docs/explanation/`.
5. Decide whether to keep the optional release layer.
6. Run `python tools/verify.py verify`.
