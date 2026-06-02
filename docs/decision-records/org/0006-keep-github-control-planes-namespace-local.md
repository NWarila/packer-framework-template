# ADR-0006: Keep GitHub Control Planes Namespace-Local

| Field            | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| ID               | ADR-0006                                                                    |
| Scope            | Org baseline                                                                |
| Status           | Accepted                                                                    |
| Decision-subject | Namespace-local ownership for GitHub control-plane governance.              |
| Date accepted    | 2026-06-01                                                                  |
| Date             | 2026-06-02                                                                  |
| Last reviewed    | 2026-06-02                                                                  |
| Authors          | Nick Warila (@NWarila)                                                      |
| Decision-makers  | Nick Warila (sole portfolio maintainer)                                     |
| Consulted        | CI findings from repo-hygiene, ADR drift, and reusable workflow rollout.    |
| Informed         | Maintainers of adopting repositories under `NWarila`.                       |
| Reversibility    | Medium                                                                      |
| Review-by        | 2026-11-29                                                                  |

## TL;DR

Repositories under `NWarila` use `NWarila/.github` as their org control plane for org-baseline ADRs, community-health files, org repo-hygiene policy, and reusable workflow callers. Repositories under another namespace, including `nwarila-platform`, use that namespace's own `.github` repository for the same control-plane concerns. Cross-namespace dependencies remain allowed for type-template repositories and explicit tools, but not for org governance that should be owned by the consuming repository's namespace.

## Context and Problem Statement

The portfolio has two related but distinct namespaces: `NWarila` and `nwarila-platform`. They share patterns, maintainers, and some type-template dependencies, but they are separate GitHub organizations with separate default community files, ADR baselines, repository policies, and reusable workflow control surfaces.

Before this decision was written down, some `nwarila-platform/*` repositories called reusable workflows from `NWarila/.github`. That worked technically because the repositories are public, but it blurred ownership. A platform repository could be governed by an org control plane outside its namespace, and a change to `NWarila/.github` could affect platform repository checks without the platform namespace carrying the source policy itself.

The same ambiguity appeared in drift-gate manifests. Files such as workflow callers and mirroring documentation have the same shape across templates, but their org-control-plane references must differ by namespace. Treating those files as byte-identical across namespaces makes the automated drift check fight the intended trust boundary.

The portfolio needs a clear rule that keeps org governance local to the namespace while still allowing cross-namespace reuse of type-template assets where that is the deliberate architecture.

## Decision Drivers

1. **Ownership clarity.** A repository's org governance should be owned by the organization that owns the repository.
2. **Blast-radius control.** A change in one namespace's `.github` repository should not silently change another namespace's policy surface.
3. **Auditability.** Reviewers should be able to identify the authoritative org ADRs, community-health files, and workflow policies from the repository's owner/name.
4. **Useful automation.** Drift gates should detect real drift, not force namespace-specific files to pretend they are byte-identical.
5. **Template reuse.** Stack templates can still live in `NWarila` when they are explicitly type-template dependencies rather than org governance.

## Considered Options

1. Use a single shared `NWarila/.github` control plane for both namespaces.
2. Duplicate all templates and tools into each namespace, forbidding cross-namespace dependencies entirely.
3. Keep org control planes namespace-local, while allowing explicit cross-namespace type-template and tool dependencies.

## Decision Outcome

Chosen option: **Option 3, keep org control planes namespace-local while allowing explicit type-template and tool dependencies.**

For repositories whose owner is `NWarila`:

- Org-baseline ADRs are sourced from `NWarila/.github/docs/decision-records/`.
- Community-health files and org defaults are sourced from `NWarila/.github`.
- Org reusable workflow callers such as repo hygiene, CodeQL, IaC/security, Scorecard, release-please, and auto-merge call `NWarila/.github`.
- `repo-hygiene` callers set `source_ref` to the same `NWarila/.github` commit SHA used in the reusable workflow `uses:` reference.

For repositories owned by another namespace, the same categories are sourced from that namespace's `.github` repository. A `nwarila-platform/*` repository therefore calls `nwarila-platform/.github` for org reusable workflows and mirrors org ADRs from `nwarila-platform/.github`.

Cross-namespace references remain valid when they are not org control planes. Examples include type-template repositories, drift-gate itself, and framework reusable workflows that are intentionally published as stack templates. Those dependencies must still be pinned by full commit SHA where repo-hygiene requires it.

Template manifests must distinguish byte-identical files from namespace-specific starter files. A file that embeds an org-control-plane repository name, such as `.github/workflows/security.yaml` or a mirroring reference document, is not byte-identical across namespaces unless the source and consumer share the same namespace. Such files belong in `scaffold_starter` or an equivalent non-byte-enforced propagation group.

## Pros and Cons of the Options

### Option 1: Single shared `NWarila/.github`

- **Good, because** one repository carries all org reusable workflows and policy files.
- **Good, because** consumers have fewer source repositories to track.
- **Bad, because** `nwarila-platform/*` repositories would depend on a different namespace for org governance.
- **Bad, because** a `NWarila/.github` change could affect platform repositories without a platform-owned policy update.
- **Bad, because** it makes ADR mirrors and drift-gate source labels misleading.

### Option 2: Duplicate all templates and tools per namespace

- **Good, because** every dependency is namespace-local.
- **Good, because** blast radius is smallest.
- **Bad, because** type-template code and tools would be copied unnecessarily.
- **Bad, because** duplicated stack templates drift and multiply maintenance work.
- **Bad, because** it prevents deliberate reuse of mature templates.

### Option 3: Namespace-local org control planes with explicit cross-namespace templates

- **Good, because** org governance follows repository ownership.
- **Good, because** reusable workflow and ADR source labels match the owning namespace.
- **Good, because** drift-gate can enforce the right files exactly and allow the right files to vary.
- **Good, because** type-template reuse remains possible when that dependency is explicit.
- **Neutral, because** consumers must distinguish org-control-plane dependencies from type-template dependencies.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows RFC 2119 conventions.

1. **Workflow namespace check.** A `NWarila/*` repository's reusable workflow calls to org governance workflows MUST use `NWarila/.github/.github/workflows/...` pinned by full commit SHA.
2. **Repo-hygiene source check.** A `NWarila/*` repo-hygiene caller MUST set `source_ref` to the same `NWarila/.github` commit SHA used in the workflow `uses:` reference.
3. **ADR mirror source check.** A `NWarila/*` repository that mirrors org ADRs MUST mirror them from `NWarila/.github`.
4. **Cross-namespace exception check.** A cross-namespace dependency MUST be recognizable as a type-template, tool, or other explicit non-org-control-plane dependency.
5. **Manifest classification check.** Type-template manifests SHOULD classify files that embed org-control-plane repository names as starter or customizable files unless the template and all consumers share the same namespace.
6. **Review rule.** Any PR that introduces a reusable workflow caller to another namespace's `.github` repository MUST explain why it is not an org-control-plane dependency, or it should be rejected.

## Consequences

### Positive

- Org policy ownership is obvious from repository ownership.
- A namespace can harden its reusable workflows without unexpectedly changing another namespace's repositories.
- Drift-gate failures become more meaningful because namespace-specific files are not forced into byte identity.
- Cross-namespace type-template reuse remains available and explicit.

### Negative

- Equivalent reusable workflows may exist in more than one `.github` repository.
- Consumers that move between namespaces need an intentional workflow and ADR mirror repointing PR.
- Template authors must classify manifest entries more carefully.

### Neutral

- This ADR does not change the ADR format or the three-scope ADR model from ADR-0001.
- This ADR does not forbid `NWarila/*` repositories from consuming `nwarila-platform/*` tools if a later repository-specific decision justifies that dependency.
- This ADR documents an ownership rule that was already implicit in the separate org-baseline ADR sets.

## Assumptions

1. `NWarila/.github` and `nwarila-platform/.github` remain public or otherwise accessible to their consumers.
2. Each namespace continues to maintain its own org ADRs, community-health files, and reusable workflow baselines.
3. Type-template repositories may continue to live in one namespace while serving consumers in another namespace.
4. Repo-hygiene and drift-gate remain the main machine checks for workflow pinning and mirrored baseline drift.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

- [`NWarila/.github#18`](https://github.com/NWarila/.github/pull/18) removed the repo-hygiene advisory bypass and produced the current hard-fail org reusable baseline.
- [`NWarila/chiseled-application-template#13`](https://github.com/NWarila/chiseled-application-template/pull/13) pinned `NWarila` template workflow callers and org ADR sync to the current `NWarila/.github` baseline.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) establishes the org, template, and repository ADR scopes.
- [ADR-0004](0004-use-renovate-for-dependency-updates.md) establishes the same general principle for dependency-update baselines: stack-specific concerns belong to type-template baselines, not a single org-wide config.

## Compliance Notes

This decision supports configuration management and separation of duties. It keeps policy authority aligned with repository ownership and makes the source of CI, ADR, and community-health controls explicit in source control. It is not, by itself, a compliance claim.

## Changelog

| Date       | Change                                    | Reason                                      | Author/Role                       | Body-diff? |
| ---------- | ----------------------------------------- | ------------------------------------------- | --------------------------------- | ---------- |
| 2026-06-02 | Refreshed metadata and removed final blank lint drift. | Apply ADR-0001 living metadata and keep Markdown lint green. | Portfolio maintainer / governance | Yes        |
