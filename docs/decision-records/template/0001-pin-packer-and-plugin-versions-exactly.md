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

Packer frameworks are executable image-building boundaries. A framework tested with one Packer or plugin version should not deploy with another version that never appeared in review.

## Decision Drivers

1. Reproducible image-build behavior.
2. Reviewable dependency changes.
3. Clear failure when local tooling is stale.
4. Renovate compatibility.

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
3. Renovate opens dependency PRs for pin updates.

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

Initial template implementation.

## Related ADRs

- [Org ADR-0004](../org/0004-use-renovate-for-dependency-updates.md)

## Compliance Notes

None.
