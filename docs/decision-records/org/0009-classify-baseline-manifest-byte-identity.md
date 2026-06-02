# ADR-0009: Classify Baseline Manifest Byte Identity

| Field            | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| ID               | ADR-0009                                                                    |
| Scope            | Org baseline                                                                |
| Status           | Accepted                                                                    |
| Decision-subject | Classification rules for byte-identical baseline-manifest entries.         |
| Date accepted    | 2026-06-02                                                                  |
| Date             | 2026-06-02                                                                  |
| Last reviewed    | 2026-06-02                                                                  |
| Authors          | Nick Warila (@NWarila)                                                      |
| Decision-makers  | Nick Warila (sole portfolio maintainer)                                     |
| Consulted        | Drift-gate findings from framework, runner, and consumer alignment PRs.     |
| Informed         | Maintainers of adopting repositories under `NWarila`.                       |
| Reversibility    | Medium                                                                      |
| Review-by        | 2026-11-29                                                                  |

## TL;DR

Baseline manifests use byte identity only for files that are truly uniform across the target repositories. Fleet-canonical community files, org ADR mirrors, docs skeleton sentinels, and stable org reference docs may be byte-identical. Repo-customizable configs, namespace-specific workflow callers, repo-specific docs, and template-internal test fixtures should be starters, existence checks, or local files rather than byte-enforced mirrors. The rule is simple: consumers mirror what they actually run or inherit as governance; templates keep what only templates run.

## Context and Problem Statement

The alignment program found that some baseline manifests were too broad. They treated reusable workflow bodies, local tools, tests, policies, and repo-customizable configs as byte-identical consumer obligations. That made consumers mirror files they did not invoke, discouraged useful local improvements, and turned drift-gate into a cargo-cult compliance check instead of a precise governance check.

The same problem appears at the documentation layer. Some documents are fleet-canonical and should be mirrored exactly, such as org ADRs and shared governance references. Other documents are repo-specific or namespace-specific and should not be forced into byte identity.

The organization needs a durable classification rule so future manifests stay small, meaningful, and enforceable.

## Decision Drivers

1. **Meaningful drift.** Drift-gate should fail only when a repository diverges from something it truly inherits.
2. **Consumer ergonomics.** Consumers should not mirror tools, tests, or policies they never run.
3. **Local maturity.** Repositories should be able to improve configs and docs that are intentionally local.
4. **Namespace correctness.** Files that embed namespace-local control-plane paths should not be byte-identical across namespaces.
5. **Recruiter clarity.** A repository should look intentional, not like a dumped copy of a template's internals.

## Considered Options

1. Put every useful template file into `byte_identical`.
2. Treat all files as starter material and avoid byte identity.
3. Use byte identity only for files that are uniform governance, and classify everything else by how it is actually used.

## Decision Outcome

Chosen option: **Option 3, use byte identity only for files that are uniform governance, and classify everything else by how it is actually used.**

Files belong in `byte_identical` when all of the following are true:

- The file is intentionally the same for every target repository in the manifest scope.
- The target repository either inherits the file as governance or directly uses it in its own lifecycle.
- A local edit would be drift rather than maturity.
- The file does not embed namespace-specific or repo-specific values unless the manifest scope is limited to that namespace or repository.

Files do not belong in `byte_identical` when any of the following are true:

- The file is template-internal tooling, policy, tests, or fixtures that consumers do not run.
- The file is a repo-customizable config such as editor, lint, or hook configuration where mature consumers may have richer local variants.
- The file is a workflow caller that embeds a namespace-local `.github` repository path and the manifest applies across namespaces.
- The file is repo-specific documentation, diagram content, inventory, or runtime evidence.

Those files should instead be classified as starter material, scaffold content, source-existence checks, shape checks, or local repository files, depending on how the repository uses them.

## Pros and Cons of the Options

### Option 1: Byte-enforce every useful template file

- **Good, because** consumers start with a complete copy of the template's working tree.
- **Good, because** drift-gate can detect any deviation.
- **Bad, because** consumers inherit files they do not run.
- **Bad, because** mature local configs are downgraded to template defaults.
- **Bad, because** namespace-specific files are forced into false uniformity.

### Option 2: Avoid byte identity

- **Good, because** repositories can adapt freely.
- **Good, because** manifests are less likely to block local maturity.
- **Bad, because** inherited governance can silently drift.
- **Bad, because** org ADR mirrors and community-health files lose mechanical protection.
- **Bad, because** reviewers must manually spot differences that automation should catch.

### Option 3: Classify by actual use

- **Good, because** inherited governance stays exact.
- **Good, because** consumers are not forced to carry template internals.
- **Good, because** repo-specific docs and configs can mature locally.
- **Good, because** namespace-local control-plane paths are handled honestly.
- **Neutral, because** manifest authors must decide classification deliberately.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows RFC 2119 conventions.

1. **Use test.** A manifest entry marked byte-identical MUST describe a file that the target repository inherits as governance or directly uses in its lifecycle.
2. **Uniformity test.** A byte-identical file MUST be intended to have the same bytes across the manifest's target scope.
3. **Customization test.** Repo-customizable configs SHOULD be starter or scaffold entries rather than byte-identical entries.
4. **Namespace test.** Files embedding namespace-local `.github` paths MUST NOT be byte-identical across namespaces.
5. **Docs test.** Fleet-canonical docs MAY be byte-identical; repo-specific docs and diagrams SHOULD be governed by existence, shape, or local review.
6. **Review test.** PRs that add broad byte-identical entries SHOULD explain why local divergence would be drift rather than maturity.

## Consequences

### Positive

- Baseline manifests stay smaller and more truthful.
- Consumers mirror only files they actually inherit or run.
- Mature repositories can keep richer local configs.
- Drift-gate failures carry clearer signal.

### Negative

- Manifest authors must classify files instead of copying whole directories.
- Some starter files may drift locally without byte-level automation.
- Existing bloated manifests need cleanup PRs to comply.

### Neutral

- This ADR does not remove drift-gate.
- This ADR does not weaken existing byte-identical entries that are truly uniform governance.
- This ADR applies to documentation and configuration as well as workflow files.

## Assumptions

1. Drift-gate remains the primary byte-identity enforcement mechanism.
2. Templates continue to carry starter or scaffold categories for seed files.
3. Repositories may add local docs and configs beyond inherited governance.
4. Namespace-local control-plane doctrine from ADR-0006 remains in force.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

None yet; this ADR records the accepted classification rule that future manifest cleanups apply.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) defines mirrored org, template, and repo ADR scopes.
- [ADR-0006](0006-keep-github-control-planes-namespace-local.md) defines namespace-local control-plane ownership.
- [ADR-0007](0007-centralize-universal-ci-reusables-within-each-namespace.md) explains why universal reusable bodies do not belong in type-template consumer manifests.
- [ADR-0008](0008-enforce-repo-hygiene-by-repo-type.md) explains why data-only repositories should not mirror local policy tooling.

## Compliance Notes

This decision supports configuration management by making inherited baseline files explicit and limiting byte-level enforcement to files that are meant to be identical. It reduces false compliance artifacts while preserving auditable governance mirrors.

## Changelog

| Date       | Change                                    | Reason                                      | Author/Role                       | Body-diff? |
| ---------- | ----------------------------------------- | ------------------------------------------- | --------------------------------- | ---------- |
| 2026-06-02 | Accepted byte-identity classification rules for baseline manifests. | Extract durable manifest lessons from framework, runner, and consumer alignment work. | Portfolio maintainer / governance | Yes        |
