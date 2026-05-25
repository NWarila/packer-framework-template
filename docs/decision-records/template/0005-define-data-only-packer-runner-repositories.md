# ADR-template/0005: Define Data-Only Packer Runner Repositories

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-05-25                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | Terraform runner contract and current `github-terraform-runner` shape. |
| Informed       | Future Packer framework and runner repositories. |
| Reversibility  | Medium                                  |
| Review-by      | N/A (Accepted)                          |

## TL;DR

Future Packer runner repositories are data-only consumers of a pinned Packer
framework. They own inventory, public-safe fixtures, caller workflows, thin
docs, and a runner PR template. They must not copy framework-maintainer
surfaces such as `Makefile`, `tools/`, `policies/`, contract fixtures, or local
reusable workflow implementations. A `packer-runner-template` must not be
derived until it has a runner contract equivalent to the Terraform runner
contract.

## Context and Problem Statement

`packer-framework-template` already owns the reusable Packer build workflow,
policy checks, plugin provenance checks, integration harness, and release
evidence shape. A future Packer runner will need to provide build input and call
that reusable workflow, but it should not become a second framework repository.

The Terraform runner model has already shown the intended split: the runner is a
thin deployer that owns data and caller workflows, while the template/framework
owns executable validation. Copying framework-maintainer directories into a
runner would create duplicated policy, duplicated tooling, and a misleading
review surface. A reviewer should be able to tell at a glance that a runner is
input plus evidence, not the engine.

This decision records the Packer runner boundary before a runner template exists
so future work does not clone the framework template by accident.

## Decision Drivers

1. **Thin ownership boundary.** Runners should own input data and orchestration,
   not framework internals.
2. **Reviewer clarity.** A reviewer should not have to distinguish copied
   framework tooling from runner-owned behavior.
3. **Automation-first evidence.** Confidence should come from GitHub PR
   validation, drift gates, security summaries, and release evidence.
4. **Derivation safety.** The first `packer-runner-template` should start from a
   contract, not from memory or broad copy-paste.
5. **Consistency with Terraform runners.** Packer runners should follow the
   proven data-only consumer pattern unless Packer-specific evidence requires a
   different shape.

## Considered Options

1. Clone `packer-framework-template` into every Packer runner.
2. Create thin Packer runners with no machine-readable contract.
3. Create thin Packer runners and require a contract before derivation.
4. Delay the Packer runner decision until the first runner repository is built.

## Decision Outcome

Chosen option: **Option 3, create thin Packer runners and require a contract
before derivation.**

Future Packer runner repositories may contain:

- `.github/workflows/` caller workflows.
- `.github/PULL_REQUEST_TEMPLATE.md`.
- `.github/renovate.json5`.
- `docs/`.
- `packer/repos/` or the equivalent runner-owned inventory path.
- `packer/fixtures/runtime/` or public-safe runtime fixtures.
- `tests/fixtures/` for public-safe input examples.
- `.template-type`.
- `README.md`.

Future Packer runner repositories must not contain:

- `Makefile`.
- `tools/`.
- `policies/`.
- `contract/`.
- Template-maintainer contract fixtures.
- Framework-maintainer logic.
- Local reusable workflow implementations other than an explicitly reviewed
  privileged auto-merge exception, if one is still required.

Before creating `packer-runner-template`, the implementation PR must add a
machine-readable Packer runner contract with positive and negative fixtures. At
minimum, that contract must enforce the data-only boundary, pinned caller
workflows, PR validation trigger shape, org and runner-template drift gates,
Renovate inheritance, security workflow delegation, and release evidence
delegation.

## Pros and Cons of the Options

### Option 1: Clone `packer-framework-template` into every Packer runner

- **Good, because** it is fast to bootstrap.
- **Good, because** every local tool is immediately present.
- **Bad, because** runners inherit framework-maintainer ballast they do not own.
- **Bad, because** policy and helper drift become inevitable.
- **Bad, because** reviewer attention shifts from input evidence to duplicated
  tooling.

### Option 2: Create thin Packer runners with no machine-readable contract

- **Good, because** the repo shape stays small.
- **Good, because** the first runner can be created quickly.
- **Bad, because** the thin boundary relies on memory and review discipline.
- **Bad, because** future runners can drift without an automated contract
  failure.

### Option 3: Create thin Packer runners with a contract first (chosen)

- **Good, because** the runner starts small and stays enforceable.
- **Good, because** the model matches the Terraform runner split.
- **Good, because** negative fixtures can reject framework-maintainer surfaces
  before they appear in real runners.
- **Bad, because** creating the first Packer runner requires one extra contract
  implementation step.

### Option 4: Delay the decision until the first runner is built

- **Good, because** implementation details can be discovered while coding.
- **Bad, because** the first implementation may accidentally set the wrong
  precedent.
- **Bad, because** remediation after derivation is more expensive than deciding
  the boundary now.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording
`MUST`, `SHOULD`, and `MAY` follows RFC 2119 conventions.

1. **Pre-derivation review.** A `packer-runner-template` PR MUST include a
   machine-readable runner contract before any real runner is derived from it.
2. **Data-only contract rules.** The future contract MUST forbid `Makefile`,
   `tools/`, `policies/`, `contract/`, and local framework-maintainer reusable
   workflow implementations in runner repositories.
3. **Caller workflow rules.** The future contract MUST require pinned reusable
   workflow callers and pinned `framework_ref` or equivalent input refs.
4. **Drift gates.** The future contract MUST require both org-baseline drift and
   Packer runner-template drift when runner consumers carry mirrored org or
   template files.
5. **Renovate inheritance.** The future contract MUST require runner consumers
   to extend the Packer runner template's Renovate preset by valid explicit
   preset path.
6. **Human review.** Any PR that adds framework-maintainer tooling to a runner
   MUST either remove it or add a superseding ADR explaining why the data-only
   boundary no longer applies.

## Consequences

### Positive

- Future Packer runners have the same simple ownership boundary as Terraform
  runners.
- Reviewers can focus on inventory, caller workflows, and automated evidence.
- The first Packer runner template has a concrete stop condition before
  derivation.

### Negative

- The first Packer runner template requires contract work before it can be used.
- Some framework convenience commands are intentionally unavailable in runner
  repositories.

### Neutral

- Framework repositories still own all executable Packer validation and release
  evidence logic.
- Runner repositories may still carry public-safe fixtures when CI cannot access
  production-private inputs.

## Assumptions

1. Packer runner inputs can be represented as inventory, var files, and runtime
   fixtures overlaid into a framework checkout.
2. The framework reusable workflow remains the right place to run Packer
   validation and build logic.
3. The Terraform runner contract remains a useful model for Packer runner
   enforcement.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

Initial decision record only. The `packer-runner-template` implementation PR
will add the machine-readable contract and fixtures required by this ADR.

## Related ADRs

- [ADR-template/0001](0001-pin-packer-and-plugin-versions-exactly.md)
  establishes exact Packer and plugin pinning.
- [ADR-template/0002](0002-keep-reference-framework-credential-free.md)
  keeps the reference framework safe and synthetic.
- [ADR-template/0004](0004-isolate-pull-request-target-triggers.md)
  isolates privileged PR triggers.
- [Org ADR-0004](../org/0004-use-renovate-for-dependency-updates.md)
  defines the per-template Renovate inheritance model.

## Compliance Notes

None.
