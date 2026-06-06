# Alignment Program Lessons

This reference preserves durable lessons from the org workflow and manifest alignment program. It is operational context for future maintainers, not a standalone decision record. Normative rules live in the ADRs linked from each lesson.

## Reusable Workflows

Universal reusable workflows should live once per namespace control plane and be called by full commit SHA. Duplicating their bodies into templates made security fixes slower and manifest obligations less honest. See [ADR-0007](https://github.com/NWarila/.github/blob/main/docs/decision-records/0007-centralize-universal-ci-reusables-within-each-namespace.md).

Reusable workflow syntax checks are not enough. A reusable should be smoke-tested through a real caller path in its source repository, especially when it installs tools, builds policy input, or performs conditional write-token work.

## Repo Hygiene

Repo-hygiene enforcement is a policy requirement, not a specific file-name requirement. A repository with a local verification harness can evaluate the policy there. A data-only repository should use the thin reusable caller. See [ADR-0008](https://github.com/NWarila/.github/blob/main/docs/decision-records/0008-enforce-repo-hygiene-by-repo-type.md).

Privileged `pull_request_target` workflows stay safe by construction, policy, and immutable pinning. The reusable does not need to be local for the policy to inspect unsafe caller patterns.

## Manifests

Manifests should be lean. Byte identity is for inherited governance and files the consumer actually runs. Template-internal tools, tests, fixtures, and policies belong in the template unless the consumer uses them. See [ADR-0009](https://github.com/NWarila/.github/blob/main/docs/decision-records/0009-classify-baseline-manifest-byte-identity.md).

Repo-customizable configs are a common overreach. Mature consumers may have richer `.gitattributes`, pre-commit, lint, or editor settings than a template seed. Treat those files as starters unless the template has a specific reason to enforce exact bytes.

Drift-gate against a type template couples to the template's manifest. If a consumer starts drift-gating against a template whose byte-identical manifest includes a CI harness, adopting the drift gate and adopting the harness are one unit of work.

## Runner Templates

Runner repositories should stay focused on variables, a small number of resources, and execution of a framework or reusable. They should not re-litigate framework internals that the framework repository already proves.

Sibling templates can have paired-drift behavior. A symmetric change may make both PRs show cross-template drift until one side lands and the other is re-run. That is a sequencing issue, not a reason to split the doctrine.

## Documentation

Root scratch files are not a durable source of truth. Extract decisions into ADRs, stable rules into reference docs, rationale into explanation docs, and operator steps into runbooks. After extraction, the target repository history and the in-document changelog are the record.

Documentation claims must be verified on `main`, not from local worktrees or execution logs. A local "done" note is only evidence that something was attempted.

## Review Habits

- Check the repository type before deciding which gates should be present.
- Check whether a dependency is org governance, a type-template dependency, or repo-local material.
- Treat a manifest expansion as a design choice, not bookkeeping.
- Preserve public source-control hygiene by keeping private drafting residue out of committed files and PR commit messages.
