# ADR-template/0001: Pin Packer and Plugin Versions Exactly

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-05-12                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | Existing framework-template pinning ADRs. |
| Informed       | Derivative Packer frameworks.           |
| Reversibility  | Medium                                  |
| Review-by      | N/A (Accepted)                          |

## TL;DR

Packer framework repositories derived from this template pin the Packer CLI and every Packer plugin to exact versions. Version ranges are not used.

## Context and Problem Statement

Packer frameworks are executable image-building boundaries. A framework tested with one Packer or plugin version should not build or publish images with another version that never appeared in review.
That boundary is sharper for image factories than for many static modules: a plugin update can change builder defaults, communicator behavior, post-processor output, or the way installer media is attached.

Runner repositories in this portfolio provide image inventory and call the
framework by SHA. The framework still controls the Packer runtime, plugin graph,
rendering behavior, validation policy, and release evidence. A floating Packer
or plugin constraint would let a runner exercise a toolchain that neither the
framework nor the runner reviewed.

The portfolio mostly consumes frameworks it owns. Broad third-party module
constraint solving is less important here than deterministic, tested execution.
Exact pins make Renovate updates explicit: every Packer or plugin bump appears
as a source diff, reruns the full quality surface, and can be rolled back as one
reviewable dependency change.

The reference template also uses the third-party `github.com/ethanmdavidson/git` plugin so build evidence can include the current commit without requiring a provider credential. Exact pinning makes updates reviewable, but it is not the same thing as plugin signing or checksum-controlled vendoring. Consumers with stricter supply-chain requirements should add a repo-tier ADR that replaces this plugin posture with a mirror or vendored install process.

## Decision Drivers

1. Reproducible image-build behavior.
2. Reviewable dependency changes.
3. Stable Packer plugin behavior across local, CI, and release-evidence runs.
4. Clear failure when local tooling is stale.
5. Renovate compatibility.

## Considered Options

1. Exact pins for Packer and plugins.
2. Exact Packer pin with plugin ranges.
3. Pessimistic ranges.
4. No explicit constraints.

## Decision Outcome

Chosen option: **Option 1, exact pins for Packer and plugins.**

Frameworks derived from this template MUST set `packer.required_version` to `= X.Y.Z` and every `required_plugins` version to `= X.Y.Z`.

## Pros and Cons of the Options

### Option 1: Exact pins for Packer and plugins

- Good, because CI and local runs use one reviewed toolchain.
- Good, because dependency PRs are explicit.
- Bad, because consumers must update local tooling when pins move.

### Option 2: Exact Packer pin with plugin ranges

- Good, because the Packer binary is fixed.
- Bad, because plugin behavior can still drift.

### Option 3: Pessimistic ranges

- Good, because patch releases can land with less friction.
- Bad, because the tested version is not the only allowed version.

### Option 4: No explicit constraints

- Good, because it is easy at first.
- Bad, because it abandons reproducibility.

## Confirmation

1. `packer/packer.pkr.hcl` uses exact pins.
2. OPA rejects non-exact Packer or plugin constraints.
3. `packer/plugin-provenance.json` carries the upstream SHA256SUMS table for pinned third-party plugins.
4. `tools/check_packer_plugin_provenance.py` verifies each required plugin has committed provenance, can compare live upstream SHA256SUMS against the committed lock during release evidence, and checks installed binaries against Packer's checksum sidecars after `packer init`.
5. Renovate opens dependency PRs for pin updates.

## Consequences

### Positive

- Builds are easier to reproduce.
- Dependency bumps are auditable.

### Negative

- Tool updates can require coordinated consumer changes.

### Neutral

- Public forks can supersede this decision with repo-level ADRs.

## Assumptions

1. The portfolio controls the main framework consumers.
2. Packer plugin releases remain addressable by version.
3. The validation surface remains cheap enough for dependency PRs.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

- Initial template implementation: exact `packer.required_version` and `required_plugins` pins.
- Adversarial-review catch-up: expanded `repo_hygiene.rego` tests for comment spoofing, floating workflow refs, and unprefixed plugin versions; added artifact-aware policy for generated Packer evidence; added plugin provenance locking, upstream checksum drift checks, and installed-plugin checksum sidecar verification.

## Related ADRs

- [Org ADR-0004](../org/0004-use-renovate-for-dependency-updates.md)

## Compliance Notes

- The git plugin is pinned by version and its upstream SHA256SUMS table is committed and drift-checked in release evidence, but it remains third-party. This ADR accepts that for the credential-free reference template; provider-backed frameworks should decide whether to vendor or mirror plugins in a repo-tier ADR.
