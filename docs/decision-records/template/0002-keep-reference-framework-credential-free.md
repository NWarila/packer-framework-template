# ADR-template/0002: Keep Reference Framework Credential-Free

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-05-12                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | Proxmox Packer framework direction.     |
| Informed       | Derivative Packer frameworks.           |
| Reversibility  | Low                                     |
| Review-by      | N/A (Accepted)                          |

## TL;DR

The reference framework uses Packer's `null` source and local evidence output so CI can validate the framework contract without infrastructure credentials.

## Context and Problem Statement

A template repository should be runnable by any consumer and by CI without owning Proxmox, cloud, ISO, or artifact-publishing credentials.

## Decision Drivers

1. Safe public CI.
2. Fast local validation.
3. No secret bootstrap requirement.
4. Clear boundary between reference pattern and real providers.

## Considered Options

1. Use the `null` source and generated local evidence.
2. Use a real Proxmox source.
3. Mock Packer with scripts only.

## Decision Outcome

Chosen option: **Option 1, `null` source and local evidence.**

Real frameworks replace the source block while keeping the surrounding repo-quality surface.

## Pros and Cons of the Options

### Option 1: `null` source and local evidence

- Good, because validation requires no external systems.
- Good, because Packer still parses and runs the real template.
- Bad, because it does not prove provider-specific image publishing.

### Option 2: Real provider source

- Good, because it is closer to production.
- Bad, because it requires secrets and infrastructure.

### Option 3: Script-only mock

- Good, because it is simple.
- Bad, because it stops testing Packer itself.

## Confirmation

1. `packer/source.pkr.hcl` uses `source "null"`.
2. `python tools/verify.py integration` runs without provider credentials.
3. Generated artifacts remain untracked.

## Consequences

### Positive

- The template is safe to run in public CI.
- Consumers can learn the framework contract before choosing a provider.

### Negative

- Provider semantics must be tested in derivative frameworks.

### Neutral

- The template still uses Packer plugins for metadata where useful.

## Assumptions

1. Derivative frameworks add provider-specific tests.
2. Local generated evidence is enough for template-level validation.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

Initial template implementation.

## Related ADRs

- [Template ADR-0001](0001-pin-packer-and-plugin-versions-exactly.md)

## Compliance Notes

None.
