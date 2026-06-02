# CI Validator Invocation Reference

Validation scripts only protect a repository when CI invokes them against the current tree. A repository should not rely on the mere presence of a checker file, policy file, or test fixture as proof that the behavior is enforced.

## Standard

Every validator that carries a governance claim should have one visible invocation path:

| Validator type | Expected invocation |
| -------------- | ------------------- |
| Workflow syntax | A CI job that runs action linting against repository workflows |
| Markdown and docs layout | CI jobs that run markdown linting and docs layout checks |
| ADR schema | A CI job that compares changed ADRs against the pull request base |
| Baseline manifest | A CI job or drift-gate workflow that checks source and target entries |
| Repo hygiene | Local harness evaluation or the reusable caller, per [ADR-0008](../decision-records/0008-enforce-repo-hygiene-by-repo-type.md) |

## PR Review Questions

- Which CI job invokes this validator?
- Does the job run on pull requests, not only on pushes?
- Does the job inspect the pull request version of the tree?
- If the check compares against `main`, does CI fetch the pull request base safely?
- Does the job fail closed when the validator finds an issue?
- Does a reusable validator get smoke-tested in the repository that publishes it?

## Anti-Patterns

- Adding a checker script without wiring it into CI.
- Adding a policy file that only local developers can run.
- Treating generated fixtures as proof that the production workflow is covered.
- Running a validator only on `main` after a pull request has already merged.
- Using path filters that skip release, security, or policy changes.

## Implementation Notes

When a workflow needs a branch or base-ref value, pass the expression through an environment variable and keep the shell script itself expression-free. This avoids unsafe interpolation patterns and keeps workflow linting useful.

When a reusable workflow is published, add a source-side smoke test that calls it from the publishing repository. Syntax linting catches malformed YAML; smoke tests catch runtime failures in tool installation, input wiring, and conditional job paths.
