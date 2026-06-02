# ADR-0008: Enforce Repo Hygiene by Repo Type

| Field            | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| ID               | ADR-0008                                                                    |
| Scope            | Org baseline                                                                |
| Status           | Accepted                                                                    |
| Decision-subject | Mechanisms for applying repo-hygiene policy across repository types.        |
| Date accepted    | 2026-06-02                                                                  |
| Date             | 2026-06-02                                                                  |
| Last reviewed    | 2026-06-02                                                                  |
| Authors          | Nick Warila (@NWarila)                                                      |
| Decision-makers  | Nick Warila (sole portfolio maintainer)                                     |
| Consulted        | Framework-template, runner-template, and consumer CI alignment findings.    |
| Informed         | Maintainers of adopting repositories under `NWarila`.                       |
| Reversibility    | Medium                                                                      |
| Review-by        | 2026-11-29                                                                  |

## TL;DR

Every repository that carries GitHub workflow policy must run the same repo-hygiene rules, but the correct wiring depends on the repository type. Repositories with a local `make ci` or equivalent verification harness that evaluates the repo-hygiene policy over their own workflows do not need a standalone `repo-hygiene.yaml` caller. Repositories without that local policy path, including data-only runner templates and runner consumers, must carry a thin `repo-hygiene.yaml` caller to the namespace-local reusable workflow.

## Context and Problem Statement

The repo-hygiene policy enforces controls that are shared across the portfolio: workflow `uses:` pinning, privileged `pull_request_target` restrictions, and exact Terraform pinning when Terraform version files exist. The same policy applies to framework templates, runner templates, and consumers, but those repositories do not all have the same internal shape.

Framework templates already run local CI harnesses that execute repository validators and policy checks as part of `make ci` or an equivalent verification command. Data-only runner templates and their consumers intentionally avoid carrying local tooling, tests, and policy directories. Requiring those data-only repositories to add a full local toolchain would violate their contract, while omitting repo-hygiene entirely would leave privileged workflow safety unenforced.

The organization needs a single doctrine for enforcement that avoids both false gaps and cargo-cult tooling.

## Decision Drivers

1. **Uniform policy.** SHA pinning and privileged-workflow safety should be enforced everywhere.
2. **Repo-type fit.** Enforcement wiring should match the repository's contract and not force data-only repositories to carry local tooling.
3. **No duplicate gates.** A repository should not need both a local policy evaluation and a standalone caller when one already covers the current workflow tree.
4. **Review clarity.** The absence or presence of `repo-hygiene.yaml` should be explainable from the repo type.
5. **Runtime proof.** The reusable policy path must be smoke-tested in its source control plane.

## Considered Options

1. Require every repository to carry a standalone `repo-hygiene.yaml` caller.
2. Require every repository to carry local policy tooling and run it in `make ci`.
3. Select the enforcement mechanism by repository type while keeping the policy itself uniform.

## Decision Outcome

Chosen option: **Option 3, select the enforcement mechanism by repository type while keeping the policy itself uniform.**

Repositories that already evaluate repo-hygiene through their local verification harness do not carry a standalone repo-hygiene caller. This is the expected shape for framework templates when their `make ci`, `tools/verify.py`, or equivalent command evaluates the repo-hygiene policy against the repository's own workflows.

Repositories without that local policy path must carry `.github/workflows/repo-hygiene.yaml` as a thin caller to the namespace-local reusable repo-hygiene workflow. This is the expected shape for data-only runner templates, runner consumers, and other repositories whose contract deliberately avoids local policy tooling.

The policy semantics remain the same. The choice is only the invocation mechanism. A repository-specific exception is allowed only when the repository has no applicable workflow surface or a documented equivalent gate that evaluates the same policy against the current tree. Exceptions must not weaken SHA pinning, privileged workflow restrictions, or Terraform exact-pin rules where applicable.

The source `.github` repository must smoke-test the reusable repo-hygiene workflow against itself so runtime failures in the reusable are caught before consumers pin it.

## Pros and Cons of the Options

### Option 1: Standalone caller everywhere

- **Good, because** every repository has the same visible workflow caller.
- **Good, because** data-only repositories stay lean.
- **Bad, because** framework templates that already run the policy would duplicate a gate.
- **Bad, because** reviewers may mistake duplicate checks for stronger assurance.

### Option 2: Local tooling everywhere

- **Good, because** every repository evaluates policy the same local way.
- **Good, because** policy tests can sit beside policy code.
- **Bad, because** data-only repositories would need to carry tools and policies they do not otherwise own.
- **Bad, because** runner manifests would become bloated with template-internal files.

### Option 3: Mechanism by repo type

- **Good, because** the same policy applies everywhere.
- **Good, because** each repository uses the invocation path that fits its contract.
- **Good, because** standalone caller absence is not misclassified as a gap when local CI already evaluates the policy.
- **Good, because** data-only repositories stay data-only.
- **Neutral, because** auditors must look at either local CI or the standalone caller depending on repository type.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows RFC 2119 conventions.

1. **Local harness check.** A repository that omits `.github/workflows/repo-hygiene.yaml` MUST have a local CI path that evaluates the repo-hygiene policy against its own workflow tree, or it must document why the policy is not applicable.
2. **Caller check.** A repository without that local policy path MUST carry a thin `repo-hygiene.yaml` caller to the namespace-local reusable workflow.
3. **Policy equivalence check.** Alternate local wiring MUST evaluate the same repo-hygiene policy semantics rather than a weaker subset.
4. **Data-only check.** Data-only runner templates and consumers SHOULD use the reusable caller instead of local policy tooling.
5. **Smoke-test check.** The namespace `.github` repository MUST smoke-test the reusable repo-hygiene workflow against itself.
6. **Review check.** PRs that add privileged workflow behavior MUST show that repo-hygiene covers the changed workflow.

## Consequences

### Positive

- Repo-hygiene enforcement matches repository shape.
- Data-only repositories avoid unnecessary local tooling.
- Framework templates avoid duplicate checks when their harness already evaluates the policy.
- Reviewers get a durable rule for deciding whether a missing caller is acceptable.

### Negative

- Enforcement wiring is not visually identical across every repository.
- Reviewers must know the repository type before judging the expected shape.
- Exceptions need documentation to avoid becoming quiet policy gaps.

### Neutral

- This ADR does not change the repo-hygiene policy body.
- This ADR does not change which workflow patterns repo-hygiene denies.
- This ADR works together with ADR-0007's namespace-local reusable placement.

## Assumptions

1. Repo-hygiene remains the shared policy for workflow pinning and privileged workflow safety.
2. Framework templates continue to expose a local CI harness that can evaluate policies.
3. Runner templates and many runner consumers remain intentionally lean.
4. The reusable repo-hygiene workflow remains smoke-tested in the namespace control plane.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

None yet; this ADR records the accepted enforcement doctrine that existing and future alignment PRs apply.

## Related ADRs

- [ADR-0006](0006-keep-github-control-planes-namespace-local.md) defines the namespace-local control plane for the reusable workflow.
- [ADR-0007](0007-centralize-universal-ci-reusables-within-each-namespace.md) defines where the universal reusable workflow lives.
- [ADR-0009](0009-classify-baseline-manifest-byte-identity.md) explains why data-only repositories should not mirror local policy tooling they do not run.

## Compliance Notes

This decision supports consistent CI control enforcement while preserving repository-type contracts. It provides an auditable rule for why the policy may be invoked through different mechanisms without weakening the policy itself.

## Changelog

| Date       | Change                                    | Reason                                      | Author/Role                       | Body-diff? |
| ---------- | ----------------------------------------- | ------------------------------------------- | --------------------------------- | ---------- |
| 2026-06-02 | Accepted repo-type-specific invocation of the shared repo-hygiene policy. | Extract durable enforcement doctrine from framework and runner alignment work. | Portfolio maintainer / governance | Yes        |
