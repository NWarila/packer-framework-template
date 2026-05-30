# Mirroring And Consumer Baseline

This template is intentionally split into shared repo-quality baseline and Packer implementation layers so derivative image frameworks can stay easy to adapt without losing platform controls.

## Required Shared Baseline

Derivative Packer frameworks should mirror the files listed under
`byte_identical` in this template's `baseline-manifest.json`. In a consumer,
the authoritative check is the Drift Gate workflow pointed at this template's
manifest; the consumer does not need its own copy of `baseline-manifest.json`
unless it is also publishing a downstream template.

That mirrored set is intentionally small: the shared security caller and the
reference docs that define the mirroring and runner protocol contracts. Local
verification entrypoints, OPA policies, and richer repository-specific config
belong to the repo that actually runs them.

Use `byte_identical` only for files a downstream framework should keep byte-for-byte with this template. Use `scaffold_starter` for examples, fixtures, and implementation seeds that demonstrate the pattern but are expected to change in a real framework.

The manifest is intentionally narrower than a full repo copy. It does not require downstream frameworks to keep the reference `file` source or the starter examples byte-identical.

## Framework-Owned Layer

The `packer/` implementation, examples, provider choices, and repo-tier ADRs are allowed to diverge. This reference uses the `file` builder so the pattern is visible without infrastructure while still consuming rendered installer content; real frameworks replace that source with provider-specific builders while preserving the same validation interface.

## Optional Release Layer

`release.yaml`, release-please config, release evidence, and trusted-bot auto-merge are supported by this template, but downstream frameworks do not have to mirror them byte-for-byte. Keep that layer when the repo publishes versioned releases or framework evidence. Drop it when the repo is only a private implementation detail.

Push-triggered release-please is opt-in through `RELEASE_PLEASE_ON_PUSH=true` because GitHub requires an explicit repository setting before Actions can create release PRs.

## New Framework Checklist

1. Rewrite `README.md` for the real framework.
2. Replace the `file` source under `packer/`.
3. Update examples for supported guest OS families.
4. Add provider-specific threat model notes under `docs/explanation/`.
5. Decide whether to keep the optional release layer.
6. Run the repository's local validation entrypoint. For this template, that is
   `python tools/verify.py verify`; for a consumer, use its documented CI or
   contract-check command.
