# Architecture Decision Records

This directory holds the Architecture Decision Records (ADRs) governing this Packer framework template. Per [org ADR-0001](org/0001-use-architecture-decision-records.md), ADRs are organized into three scopes:

- `org/` - byte-identical mirrors of org-baseline ADRs from [`NWarila/.github`](https://github.com/NWarila/.github). These apply to every repo in the org regardless of stack.
- `template/` - Packer-framework-template ADRs owned by this repository. Derivative frameworks mirror the `byte_identical` baseline entries through `baseline-manifest.json`.
- `repo/` - repository-specific ADRs for this repository only.

`packer-framework-template` is itself a type-template: it owns the canonical framework command surface, Packer image layout, validation tooling, reusable build workflow, and framework-tier decisions that derivative Packer framework repositories inherit.

## Template ADRs

| ADR | Status | Decision |
| --- | --- | --- |
| [ADR-template/0001](template/0001-pin-packer-and-plugin-versions-exactly.md) | Accepted | Pin the Packer CLI and every plugin to exact versions. |
| [ADR-template/0002](template/0002-keep-reference-framework-credential-free.md) | Accepted | Keep this reference framework credential-free, cost-free, and synthetic. |
| [ADR-template/0004](template/0004-isolate-pull-request-target-triggers.md) | Accepted | Keep `pull_request_target` isolated to trusted-bot auto-merge, never release publishing. |
| [ADR-template/0005](template/0005-define-data-only-packer-runner-repositories.md) | Accepted | Define future Packer runners as data-only consumers with a contract required before derivation. |
| [ADR-0006](org/0006-keep-github-control-planes-namespace-local.md) | Accepted | Keep GitHub control planes namespace-local. |
| [ADR-0007](org/0007-centralize-universal-ci-reusables-within-each-namespace.md) | Accepted | Centralize universal CI reusables within each namespace. |
| [ADR-0008](org/0008-enforce-repo-hygiene-by-repo-type.md) | Accepted | Enforce repo hygiene by repo type. |
| [ADR-0009](org/0009-classify-baseline-manifest-byte-identity.md) | Accepted | Classify baseline-manifest byte identity. |
| [ADR-0011](org/0011-adopt-two-organization-portfolio-structure.md) | Proposed | Adopt a two-organization portfolio structure. |

ADR-template/0003 was withdrawn before release and is intentionally absent.

## Org ADRs

The `org/` scope is mirrored from `NWarila/.github` and enforced by the org drift gate.

| ADR | Status | Decision |
| --- | --- | --- |
| [ADR-0001](org/0001-use-architecture-decision-records.md) | Accepted | Use ADRs to document design rationale. |
| [ADR-0002](org/0002-adopt-diataxis-documentation-framework.md) | Accepted | Use DiÃ¡taxis for non-ADR documentation. |
| [ADR-0003](org/0003-use-deny-all-gitignore-strategy.md) | Accepted | Use deny-all `.gitignore` allowlists. |
| [ADR-0004](org/0004-use-renovate-for-dependency-updates.md) | Accepted | Use Renovate for dependency updates. |
| [ADR-0005](org/0005-pin-terraform-and-provider-versions-exactly.md) | Accepted | Pin Terraform and provider versions exactly. |

## Repo ADRs

| ADR | Status | Decision |
| --- | --- | --- |
| [ADR-repo/0001](repo/0001-use-credential-free-file-builder-for-reference-validation.md) | Accepted | Use the credential-free `file` builder for reference validation so CI requires no provider credentials. |
