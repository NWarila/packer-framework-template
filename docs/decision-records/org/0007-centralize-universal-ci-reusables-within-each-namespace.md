# ADR-0007: Centralize Universal CI Reusables Within Each Namespace

| Field            | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| ID               | ADR-0007                                                                    |
| Scope            | Org baseline                                                                |
| Status           | Accepted                                                                    |
| Decision-subject | Namespace-local placement and calling rules for universal CI reusables.     |
| Date accepted    | 2026-06-02                                                                  |
| Date             | 2026-06-02                                                                  |
| Last reviewed    | 2026-06-02                                                                  |
| Authors          | Nick Warila (@NWarila)                                                      |
| Decision-makers  | Nick Warila (sole portfolio maintainer)                                     |
| Consulted        | Alignment audit findings from framework and runner-template migrations.     |
| Informed         | Maintainers of adopting repositories under `NWarila`.                       |
| Reversibility    | Medium                                                                      |
| Review-by        | 2026-11-29                                                                  |

## TL;DR

Universal CI reusable workflows live once in the owning namespace's `.github` control plane and are called by full commit SHA from repositories in that namespace. For `NWarila/*` repositories, that means the universal org reusable workflows are authored in `NWarila/.github`. Stack-specific reusable workflows remain in their type-template repositories, and type-specific release-evidence workflows stay per template. This extends ADR-0006: centralization is namespace-local, not cross-namespace org governance.

## Context and Problem Statement

The alignment work found the same universal GitHub Actions reusable workflows copied across framework templates and consumers. Copies of CodeQL, IaC/security, Scorecard, release automation, auto-merge, and repo-hygiene logic created drift risk, multiplied review work, and made security fixes propagate only after every duplicate was updated.

At the same time, ADR-0006 established that org control planes are namespace-local. A `NWarila/*` repository should not be governed by another namespace's `.github` repository, and repositories in another namespace should not depend on `NWarila/.github` for their org governance.

The portfolio therefore needs a rule that removes duplicated universal CI logic while keeping policy ownership aligned with the namespace that owns the repository.

## Decision Drivers

1. **Single source of truth.** Universal CI behavior should be edited and reviewed in one place per namespace.
2. **Fast security response.** A reusable workflow fix should be available to every adopting repository through a reviewed SHA bump.
3. **Namespace ownership.** Org governance must follow ADR-0006 and stay in the owning namespace.
4. **Template clarity.** Type templates should carry stack-specific behavior, not duplicated org-wide behavior.
5. **Auditability.** A reviewer should be able to identify whether a workflow dependency is org governance or stack-specific reuse from its repository path.

## Considered Options

1. Keep duplicating universal reusable workflows into every template and consumer.
2. Use a single global `NWarila/.github` control plane for all namespaces.
3. Centralize universal reusable workflows once per namespace and keep stack-specific reusables in type templates.

## Decision Outcome

Chosen option: **Option 3, centralize universal reusable workflows once per namespace and keep stack-specific reusable workflows in type templates.**

For `NWarila/*` repositories, the following reusable workflow families are universal org governance and are authored in `NWarila/.github/.github/workflows/`:

- CodeQL analysis.
- IaC and secret scanning.
- OpenSSF Scorecard.
- Release automation.
- Auto-merge.
- Repo hygiene.

Repositories call these reusable workflows with `uses: NWarila/.github/.github/workflows/<workflow>.yaml@<40-character-sha>`. The SHA pin is reviewed like any other dependency update. A repository under another namespace follows the same pattern against that namespace's `.github` control plane.

Stack-specific reusable workflows remain in the type-template that owns the stack. Examples include Terraform validation/deploy workflows, Packer framework build workflows, and Ansible framework run workflows. Type-specific release-evidence workflows also remain per template because their evidence gathering steps use different toolchains even when their envelope is similar.

Templates and consumers must not reintroduce local copies of universal org reusable workflows. A local thin caller is acceptable when the caller belongs to the repository's own CI surface and invokes the namespace-local org reusable by SHA.

## Pros and Cons of the Options

### Option 1: Duplicate universal reusables everywhere

- **Good, because** every repository can run without another reusable-workflow source.
- **Good, because** local review sees the full copied workflow body.
- **Bad, because** universal fixes must be copied into many repositories.
- **Bad, because** copies drift silently.
- **Bad, because** consumer manifests can balloon with files the consumer does not own.

### Option 2: Use one global control plane

- **Good, because** there is exactly one universal reusable source.
- **Good, because** security fixes have the smallest source footprint.
- **Bad, because** it violates ADR-0006 by making another namespace's `.github` repository govern local org policy.
- **Bad, because** blast radius crosses namespace boundaries.
- **Bad, because** ADR mirrors and drift labels become misleading for non-`NWarila` repositories.

### Option 3: Centralize once per namespace and keep type-specific reusables in templates

- **Good, because** duplicated universal workflow bodies disappear inside the namespace.
- **Good, because** org policy ownership remains namespace-local.
- **Good, because** type templates keep only the workflows that are genuinely stack-specific.
- **Good, because** consumers mirror fewer files and have clearer drift-gate obligations.
- **Neutral, because** equivalent reusable workflow families may exist in multiple namespaces.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows RFC 2119 conventions.

1. **Workflow source check.** A `NWarila/*` repository's universal org workflow caller MUST call `NWarila/.github/.github/workflows/...` by full commit SHA.
2. **No-copy check.** Type templates and consumers MUST NOT carry local copies of universal org reusable workflows.
3. **Type-specific exception check.** Stack-specific reusable workflows MUST remain in their owning type-template unless a later ADR deliberately moves them.
4. **Release-evidence check.** Release-evidence workflows MAY remain per template when the evidence core depends on the template's toolchain.
5. **Manifest check.** Baseline manifests SHOULD classify universal org reusable workflow bodies as org-controlled source files, not consumer-mirrored template files.
6. **Namespace check.** A repository under another namespace MUST use that namespace's `.github` control plane for org governance unless a repository-specific ADR documents a narrow exception.

## Consequences

### Positive

- Universal CI policy has one source per namespace.
- Framework and runner templates carry less duplicated code.
- Security workflow fixes are easier to review and propagate.
- Drift-gate manifests are smaller and easier to reason about.

### Negative

- A bad reusable workflow update can affect many repositories after they bump their pins.
- Each namespace must maintain its own `.github` control plane for org governance.
- Consumers need disciplined SHA-bump review instead of local body edits.

### Neutral

- This ADR does not remove stack-specific reusable workflows from type templates.
- This ADR does not require cross-namespace duplication of template repositories.
- This ADR depends on ADR-0006 for namespace ownership boundaries.

## Assumptions

1. Reusable workflow callers remain SHA-pinned by repo-hygiene policy.
2. Namespace `.github` repositories remain accessible to repositories in that namespace.
3. Type templates remain the home for stack-specific workflow behavior.
4. Drift-gate remains the mechanism for mirrored baseline files.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

None yet; this ADR records the accepted governance rule that existing and future alignment PRs enforce.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) defines org, template, and repository ADR scopes.
- [ADR-0006](0006-keep-github-control-planes-namespace-local.md) requires org control planes to stay namespace-local.
- [ADR-0008](0008-enforce-repo-hygiene-by-repo-type.md) defines how repositories enforce the policy around these callers.
- [ADR-0009](0009-classify-baseline-manifest-byte-identity.md) defines how reusable workflow and caller files are classified in manifests.

## Compliance Notes

This decision supports supply-chain governance by centralizing reusable CI logic, requiring SHA-pinned callers, and keeping policy ownership aligned with repository ownership. It is not itself a compliance certification.

## Changelog

| Date       | Change                                    | Reason                                      | Author/Role                       | Body-diff? |
| ---------- | ----------------------------------------- | ------------------------------------------- | --------------------------------- | ---------- |
| 2026-06-02 | Accepted namespace-local centralization for universal CI reusable workflows. | Extract durable alignment doctrine from the org workflow migration program. | Portfolio maintainer / governance | Yes        |
