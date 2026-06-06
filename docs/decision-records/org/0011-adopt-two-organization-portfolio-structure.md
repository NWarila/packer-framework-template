# ADR-0011: Adopt a Two-Organization Portfolio Structure

| Field            | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| ID               | ADR-0011                                                                    |
| Scope            | Org baseline                                                                |
| Status           | Proposed                                                                    |
| Decision-subject | The two-organization split and the architecture/engineering ownership boundary between `NWarila` and `nwarila-platform`. |
| Date accepted    | 2026-06-03                                                                  |
| Date             | 2026-06-03                                                                  |
| Last reviewed    | 2026-06-03                                                                  |
| Authors          | Nick Warila (@NWarila)                                                      |
| Decision-makers  | Nick Warila (sole portfolio maintainer)                                     |
| Consulted        | Cross-repo alignment audit and ADR critical-review findings (2026-06).      |
| Informed         | Maintainers of adopting repositories under `NWarila` and `nwarila-platform`.|
| Reversibility    | Low                                                                         |
| Review-by        | 2026-11-30                                                                  |

## TL;DR

The portfolio is intentionally split across two GitHub organizations with distinct roles. `NWarila` is the **architecture-and-planning** organization: it owns the canonical type-templates, the org-baseline ADR master copies, and the universal reusable-workflow master copies — the design of how repositories should be built. `nwarila-platform` is the **engineering** organization: it owns the real implementations (Terraform frameworks, clusters, container images, utilities) that consume and prove out the `NWarila` standards. Each organization runs its own `.github` control plane; `nwarila-platform`'s control plane is maintained as an automatically-synchronized, byte-identical mirror of the `NWarila` masters. This decision is the parent of [ADR-0006](0006-keep-github-control-planes-namespace-local.md) and [ADR-0007](0007-centralize-universal-ci-reusables-within-each-namespace.md): namespace-local governance is the *consequence* of this split, not an independent choice.

## Context and Problem Statement

The implementations came first. Individual framework repositories were built independently, and each re-solved the same structural problems — module shape, CI gates, policy, release evidence, documentation layout — in similar but subtly different ways. That divergence was the signal to step back and build a unified set of `*-template` repositories: a highly structured, standardized, professional baseline from which every repository of a given type is derived, so that a single change to a template can be replicated across all repositories of that type.

That consolidation introduced a second, larger structural choice that was never written down: the portfolio lives in **two** GitHub organizations, and they play different roles. `NWarila` carries the design surface (templates, governance, reusable workflows). `nwarila-platform` carries the execution surface (the real infrastructure and image repositories).

Because the two-organization split was never recorded, every governance decision that depends on it — namespace-local control planes (ADR-0006), per-namespace reusables (ADR-0007), and byte-identity classification for mirrored files (ADR-0009) — reads as unmotivated complexity. A reviewer cannot tell whether two organizations is a deliberate architecture or an accident of history, and the maintainer cannot defend the resulting dual control plane without first defending the split that creates it. The alignment audit confirmed the cost is real and currently unpaid: `nwarila-platform/.github` is a skeleton, the two organizations' shared ADR copies have already diverged, and framework workflows point at four different namespaces. The portfolio needs an explicit, defensible decision about why two organizations exist and what each one owns.

## Decision Drivers

1. **Showcase clarity.** The portfolio doubles as a staff/principal engineering showcase. Separating the architecture-and-planning signal from the engineering-execution signal lets each read cleanly to a reviewer instead of blurring into one repository pile.
2. **Proof by consumption.** Implementations that live in a *separate* namespace and consume the standards demonstrate that the standards are portable and real, not self-referential. The engineering org proves the architecture org's design works.
3. **Ownership and blast radius.** Design changes (templates, ADRs, reusables) and implementation churn (real infrastructure) have different change cadences and risk profiles; separating them keeps a design change from being lost in implementation noise and vice versa.
4. **Honest governance.** Namespace-local control planes and byte-identity mirroring only make sense if the two-organization split is itself a recorded, defended decision that they descend from.
5. **Solo-maintainer cost control.** A single maintainer cannot afford a manual 2× governance maintenance tax. The split is only acceptable if replication between the two control planes is automated, not hand-maintained.

## Considered Options

1. **Single organization.** Collapse everything into one GitHub organization with one control plane.
2. **Two independent organizations.** Two organizations whose governance is fully independent, with no shared masters and no synchronization.
3. **Two organizations with a master/mirror relationship.** `NWarila` is the architecture/master namespace that owns the canonical templates, ADR masters, and reusable-workflow masters; `nwarila-platform` is the engineering namespace that consumes and proves out those standards and runs its own control plane as an automatically-synchronized, byte-identical mirror of the `NWarila` masters.

## Decision Outcome

Chosen option: **Option 3 — two organizations with a master/mirror relationship.**

- **`NWarila` owns the design surface.** Canonical type-templates (for example `terraform-framework-template`, `terraform-runner-template`, `packer-framework-template`), the org-baseline ADR master copies under `NWarila/.github/docs/decision-records/`, and the universal reusable-workflow master bodies under `NWarila/.github/.github/workflows/` are authored and versioned here. `NWarila` is curated to read as an architecture-and-planning portfolio.
- **`nwarila-platform` owns the execution surface.** The real Terraform frameworks, clusters, container images, and utilities live here and are derived from the `NWarila` type-templates. `nwarila-platform` is curated to read as an engineering portfolio whose repositories prove the `NWarila` standards in practice.
- **Each organization runs its own `.github` control plane.** Per ADR-0006, repositories consume org governance from their *own* namespace's control plane. `nwarila-platform/.github` is therefore a full control plane in its own right — but it is maintained as a **byte-identical mirror** of the `NWarila/.github` masters, kept in sync by the automated mirror plus drift-gate rather than by hand. Genuinely namespace-specific values (the org name embedded in workflow callers, mirroring references) are the only intended differences and are classified as starter/customizable, not byte-identical, per ADR-0009.
- **Interim rule (transitional).** Until `nwarila-platform/.github` is built out to a complete mirror, a `nwarila-platform/*` repository MAY consume `NWarila/.github` reusables directly by full commit SHA, but every such reference MUST be marked transitional and removed once the namespace-local mirror exists. This interim state is a migration artifact, not the target architecture.
- **This ADR is the parent of ADR-0006 and ADR-0007.** Those ADRs record the *consequences* of this split (namespace-local control planes and per-namespace reusables); they are scoped by this decision and should cite it.

## Pros and Cons of the Options

### Option 1: Single organization

- **Good, because** there is exactly one control plane, so byte-identity is trivially true and the dual-maintenance tax disappears.
- **Good, because** it is the simplest possible governance topology for a solo maintainer.
- **Bad, because** it erases the architecture-versus-engineering narrative that is a deliberate showcase signal.
- **Bad, because** consuming the standards from the same org that authors them is self-referential and proves less about portability.
- **Bad, because** moving the existing `nwarila-platform/*` repositories is the most disruptive change available (repo transfers, remote and `uses:` ref rewrites across the fleet).

### Option 2: Two independent organizations

- **Good, because** each namespace is fully self-contained with the smallest possible blast radius.
- **Bad, because** independent governance guarantees drift between the two ADR baselines and reusable sets.
- **Bad, because** it forfeits the "one change replicates everywhere" capability that motivated the consolidation in the first place.
- **Bad, because** two hand-maintained governance baselines is the worst maintenance tax for a solo maintainer.

### Option 3: Two organizations with a master/mirror relationship

- **Good, because** it preserves the architecture/engineering showcase narrative and the proof-by-consumption signal.
- **Good, because** a single authoritative master per asset eliminates the ambiguity of "which copy is canonical."
- **Good, because** automated mirroring plus drift-gate pays the duplication tax with machines, not maintainer time, and turns divergence into a CI failure.
- **Neutral, because** it requires building and maintaining the synchronization machinery before the namespace-local doctrine is real.
- **Bad, because** until the mirror is complete the namespace-local invariant is only partially satisfied and an interim cross-namespace allowance is required.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows RFC 2119 conventions.

1. **Asset-ownership check.** Canonical type-templates, org-baseline ADR masters, and universal reusable-workflow master bodies MUST live in `NWarila`. Real implementation repositories MUST live in `nwarila-platform`.
2. **Mirror-identity check.** The org-baseline ADRs and universal reusable workflows in `nwarila-platform/.github` MUST be byte-identical to their `NWarila/.github` masters except for classified namespace-specific values, as enforced by the drift-gate.
3. **Interim-consumption check.** A `nwarila-platform/*` repository that consumes `NWarila/.github` org-control-plane reusables directly MUST mark the reference as transitional, and the reference MUST be retired once the namespace-local mirror exists.
4. **Narrative check.** Each organization's profile or landing repository SHOULD state its role (architecture/planning versus engineering) so the split is legible to a reviewer.
5. **Review rule.** Adding a third organization, or moving the architecture/engineering ownership boundary, MUST update this ADR before the change lands.

## Consequences

### Positive

- The portfolio presents two coherent, distinct stories instead of one undifferentiated repository list.
- The canonical source of every shared asset is unambiguous, and divergence becomes a detectable, fixable CI failure rather than silent rot.
- Namespace-local governance (ADR-0006/0007) gains an explicit parent rationale, so it no longer reads as unmotivated complexity.

### Negative

- The portfolio carries two `.github` control planes, which only stays affordable if the automated mirror is built and kept working.
- A transitional period exists during which the namespace-local invariant is not yet fully satisfied and cross-namespace consumption is temporarily allowed.
- Equivalent reusable-workflow bodies exist in both namespaces, increasing the surface that the synchronization machinery must cover.

### Neutral

- This ADR does not change the ADR format or the three-scope model from ADR-0001.
- This ADR does not mandate any particular synchronization implementation; the mechanism is recorded by the mirroring/sync ADR and ADR-0009.
- This ADR documents an organizational structure that already existed implicitly; it records and defends the choice rather than introducing it.

## Assumptions

1. `NWarila/.github` and `nwarila-platform/.github` remain accessible to their consumers.
2. An automated mirror plus drift-gate is built and maintained so the dual control plane does not become a manual tax.
3. The maintainer continues to value the architecture-versus-engineering showcase separation enough to justify two organizations over one.
4. Type-template repositories may live in `NWarila` while serving consumers in `nwarila-platform`, as an explicit cross-namespace type-template dependency permitted by ADR-0006.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

None yet.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) establishes the org, template, and repository ADR scopes that this split distributes across two namespaces.
- [ADR-0006](0006-keep-github-control-planes-namespace-local.md) records the namespace-local control-plane rule that descends from this decision.
- [ADR-0007](0007-centralize-universal-ci-reusables-within-each-namespace.md) records the per-namespace reusable-workflow rule that descends from this decision.
- [ADR-0009](0009-classify-baseline-manifest-byte-identity.md) governs which mirrored files are byte-identical versus namespace-specific.

## Compliance Notes

This decision supports configuration management and separation of duties by making the authoritative source of design assets explicit and distinct from the implementations that consume them. It is not, by itself, a compliance claim.

## Changelog

| Date       | Change                                  | Reason                                                        | Author/Role                       | Body-diff? |
| ---------- | --------------------------------------- | ------------------------------------------------------------- | --------------------------------- | ---------- |
| 2026-06-03 | Initial draft recording the two-organization split and the architecture/engineering ownership boundary. | Record the portfolio's most consequential, previously-implicit structural decision so its descendant governance ADRs are motivated and defensible. | Portfolio maintainer / governance | Yes        |
