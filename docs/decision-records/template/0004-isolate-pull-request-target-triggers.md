# ADR-template/0004: Isolate Pull Request Target Triggers

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-05-10                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | zizmor findings and pull-request-target OPA policy. |
| Informed       | Derivative frameworks via release and auto-merge docs. |
| Reversibility  | Medium                                  |
| Review-by      | N/A (Accepted)                          |

## TL;DR

`pull_request_target` is allowed only for the narrow trusted-bot auto-merge
surface. Release publication, release evidence, Packer validation,
and all other framework workflows must stay on `push`, `pull_request`,
`release`, `workflow_dispatch`, `merge_group`, or `workflow_call` triggers as
appropriate. The release workflow must never add `pull_request_target`.

## Context and Problem Statement

`pull_request_target` runs in the security context of the base repository. That
is useful for a tiny auto-merge caller that needs write permission to enable
auto-merge for trusted dependency bots. It is dangerous when mixed with
release, evidence, or build logic because those paths handle published
artifacts, attestations, Packer commands, and workflow credentials.

Before this decision, auto-merge and release plumbing were close enough that a
future edit could accidentally put release maintenance inside a privileged PR
trigger. That creates a hard-to-review surface: a reviewer trying to reason
about release evidence would also need to reason about attacker-controlled PR
metadata and the special permissions model of `pull_request_target`.

Framework repositories need a simple rule that keeps the exceptional trigger
exceptional. Auto-merge can use `pull_request_target` because it does not check
out or execute PR-controlled code. Release and deploy workflows do not need that
trigger, so they must not carry it.

## Decision Drivers

1. **Least privilege.** Workflows should receive the privileged PR event only
   when the job cannot function without it.
2. **Review locality.** Release and deploy changes should be reviewable without
   also auditing the privileged PR trigger model.
3. **Artifact integrity.** Release evidence and attestations should be produced
   only from trusted release events or explicit maintainer dispatch.
4. **Consumer safety.** Derivative frameworks mirror this workflow surface, so
   a template mistake multiplies across consumers.
5. **Machine enforcement.** The rule should be checkable by OPA against the
   committed workflow files.

## Considered Options

1. Keep auto-merge, release-please, and release evidence in one workflow.
2. Split the release workflow but allow `pull_request_target` if future release
   logic needs it.
3. Isolate `pull_request_target` to `auto-merge.yaml` and forbid it from
   `release.yaml`.
4. Remove `pull_request_target` entirely and require humans to merge dependency
   PRs manually.

## Decision Outcome

Chosen option: **Option 3, isolate `pull_request_target` to auto-merge and
forbid it from release.**

Framework templates keep trusted-bot auto-merge in `auto-merge.yaml`, which is a
small caller of `reusable-auto-merge.yaml`. The reusable auto-merge workflow is
the single implementation of the trusted-author convention; OPA enforces that
the privileged path does not read PR-controlled content or check out PR code.

Release publication and release evidence stay in `release.yaml`. That workflow
may be triggered by `push`, `release`, and `workflow_dispatch`. It must not use
`pull_request_target`. Packer validation and build-evidence workflows also
remain outside `pull_request_target`; they run on ordinary PR, dispatch,
reusable, or release-oriented events depending on purpose.

## Pros and Cons of the Options

### Option 1: Keep all release and auto-merge behavior together

- **Good, because** there is one workflow file to inspect.
- **Good, because** shared release and auto-merge permissions are easy to wire
  once.
- **Bad, because** a release edit can accidentally inherit a privileged PR
  trigger.
- **Bad, because** reviewers must audit unrelated trust boundaries together.
- **Bad, because** one mistake would propagate to every derivative framework.

### Option 2: Split release but allow future `pull_request_target` in release

- **Good, because** the current files are separated while leaving flexibility.
- **Neutral, because** future flexibility is useful only if release work truly
  needs a privileged PR event.
- **Bad, because** the rule is too soft to enforce mechanically.
- **Bad, because** a future maintainer may interpret the allowance as approval
  to mix release artifacts with PR-controlled metadata.

### Option 3: Isolate `pull_request_target` to auto-merge (chosen)

- **Good, because** the privileged PR event has one narrow purpose.
- **Good, because** release evidence stays on trusted release/dispatch paths.
- **Good, because** the OPA policy can reject `pull_request_target` in every
  workflow except the explicit auto-merge allowlist entry.
- **Good, because** consumers inherit a smaller and more explainable workflow
  trust boundary.
- **Bad, because** a future release feature that genuinely needs
  `pull_request_target` would require a superseding ADR instead of a quick edit.

### Option 4: Remove `pull_request_target` entirely

- **Good, because** it eliminates the privileged PR trigger class.
- **Good, because** dependency PR merging becomes purely human-governed.
- **Bad, because** trusted dependency updates lose safe auto-merge ergonomics.
- **Bad, because** it discards an already narrow two-job authorize-then-act
  design instead of enforcing its boundary.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording
`MUST`, `SHOULD`, and `MAY` follows RFC 2119 conventions.

1. **Privileged trigger allowlist.** `.github/workflows/auto-merge.yaml` is the
   only workflow allowed to use `pull_request_target`. The OPA `repo_hygiene`
   policy enforces this against the repository's real workflow files.
2. **Release trigger policy.** `.github/workflows/release.yaml` MUST NOT contain
   a `pull_request_target` trigger.
3. **Auto-merge reusable guard.** `reusable-auto-merge.yaml` MUST NOT read
   PR-controlled content or check out PR code. The OPA `repo_hygiene` policy
   enforces those content boundaries; the trusted-author list is maintained by
   convention and branch protection.
4. **Release evidence path.** `release.yaml` invokes release evidence only from
   `release` or explicit `workflow_dispatch` events; release-please dispatches
   the evidence task after publishing a release with `GITHUB_TOKEN`.
5. **Human review.** Any PR that adds `pull_request_target` to a new workflow
   MUST explain why the ordinary event model is insufficient and SHOULD include
   a superseding ADR.

## Consequences

### Positive

- Release maintenance no longer touches the privileged PR trigger surface.
- The workflow trust model is easier to explain and review.
- OPA can enforce the key boundary with a direct content rule.
- Derivative frameworks inherit a safer default when they mirror this template.

### Negative

- A future workflow that genuinely needs `pull_request_target` must go through
  an ADR update instead of a small YAML-only change.
- The auto-merge and release surfaces are split across two caller workflows.

### Neutral

- The reusable auto-merge workflow remains privileged, but only for trusted-bot
  authorization and merge enablement.
- Release evidence still has both `release` and `workflow_dispatch` paths; the
  latter exists because `GITHUB_TOKEN`-created release events do not cascade.

## Assumptions

1. Release publication and release evidence do not require reading
   PR-controlled content.
2. GitHub continues to treat `GITHUB_TOKEN`-created release events as
   non-cascading, requiring explicit dispatch for release evidence after
   release-please publishes.
3. Trusted dependency bots remain the only principals eligible for auto-merge.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

Initial template implementation.

## Related ADRs

- [ADR-template/0001](0001-pin-packer-and-plugin-versions-exactly.md)
  establishes exact toolchain pinning, which release evidence records.
- `tools/verify.py` keeps framework validation separate from release and
  auto-merge concerns.
- [Org ADR-0004](../org/0004-use-renovate-for-dependency-updates.md)
  establishes the dependency-update mechanism that produces trusted-bot PRs.

## Compliance Notes

None.
