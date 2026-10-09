# Mirroring Reference

This reference describes how inherited files move from control-plane and template repositories into adopting repositories. It is governed by [ADR-0001](https://github.com/NWarila/.github/blob/main/docs/decision-records/0001-use-architecture-decision-records.md), [ADR-0006](https://github.com/NWarila/.github/blob/main/docs/decision-records/0006-keep-github-control-planes-namespace-local.md), and [ADR-0009](https://github.com/NWarila/.github/blob/main/docs/decision-records/0009-classify-baseline-manifest-byte-identity.md).

## Core Rule

Consumers mirror what they inherit as governance or directly run in their own lifecycle. Templates keep files that only templates run. Repo-specific material stays local to the repository that owns it.

## Source Classes

| Source class | Master location | Consumer location | Byte identity |
| ------------ | --------------- | ----------------- | ------------- |
| Org ADRs | Owning namespace `.github/docs/decision-records/` | `docs/decision-records/org/` | Yes |
| Org community files | Owning namespace `.github` | Repository root or `.github/` | Yes when uniform |
| Type-template ADRs | Type template `docs/decision-records/template/` | `docs/decision-records/template/` | Yes |
| Type-specific reusable workflows | Type template `.github/workflows/` | Called by `uses:` or mirrored only when directly run | Depends on contract |
| Universal org reusable workflows | Owning namespace `.github/.github/workflows/` | Called by SHA-pinned thin callers | No local body copy |
| Repo-specific ADRs | Owning repository `docs/decision-records/repo/` | Not mirrored | No |
| Repo-specific docs and diagrams | Owning repository `docs/` | Not mirrored | No |

## Namespace Rule

Org governance is namespace-local. A `NWarila/*` repository mirrors org ADRs and community files from `NWarila/.github`. A repository under another namespace mirrors the same categories from that namespace's `.github` control plane. Cross-namespace references remain valid for explicit type-template or tool dependencies, but not for org-control-plane governance.

## Org ADR Auto-Sync

Repositories that already mirror org ADRs should carry a scheduled caller for the namespace-local `reusable-org-adr-auto-sync.yaml`. The caller runs from the adopting repository, so its sync token can only update that repository. It fetches the owning namespace `.github` `org-adr-manifest.json`, copies only `docs/decision-records/org/` targets, removes stale mirrored ADR Markdown files, updates the adopting repository's ADR-only detector source pin when present, and opens or refreshes a PR.

The reusable keeps `GITHUB_TOKEN` read-only. Real sync writes require the caller to pass an explicit `sync_token` secret with permission to push the sync branch and open the PR.

This auto-sync supplements the drift-gate detector; it does not replace review. The detector stays responsible for byte-identity verification, while the auto-sync keeps the repair path small and namespace-scoped.

## Byte-Identity Rule

Use byte identity when local edits would be drift. Do not use byte identity when local edits would be maturity.

Byte-identical entries are appropriate for:

- Org ADR mirrors.
- Shared community-health files.
- Stable org reference documents that are intentionally inherited.
- Skeleton sentinels that preserve expected directories.

Starter, scaffold, existence, or local entries are appropriate for:

- Repo-customizable lint, hook, editor, or documentation configuration.
- Workflow callers that embed namespace-specific `.github` paths across a multi-namespace target set.
- Template-internal tools, tests, fixtures, and policies that consumers do not run.
- Repo-specific diagrams, inventories, runtime evidence, and runbooks.

## Review Checklist

- Does the target repository inherit or run this file?
- Would a local improvement be drift or maturity?
- Does the file embed a namespace, repository name, branch, environment, or runtime-specific value?
- Is the source an org control plane, a type template, or the repository itself?
- Is the file body needed locally, or should the repository call it by `uses:`?

When the answer is unclear, prefer a smaller byte-identical manifest and a separate starter or reference entry.
