# Purge AI Attribution From Published History

This runbook is the break-glass procedure for removing assistant-tool attribution residue that has already landed in public protected history and cannot be cleaned up by an ordinary follow-up commit. It implements [ADR-0010](../decision-records/0010-keep-ai-attribution-out-of-version-control.md).

Use this only after ordinary cleanup is insufficient. History rewriting disrupts every clone and should be rare.

## Preconditions

- The repository owner has explicitly approved the cleanup.
- The exact residue marker, affected commits, and affected branches are known.
- The rewrite scope is limited to the smallest repository and branch set that solves the issue.
- A rollback or recovery note is prepared for maintainers who have local clones.
- Branch protection, release tags, and open pull requests have been reviewed for impact.

## Preferred Fix Before Rewrite

If the residue appears only in the current pull request, amend or replace the PR commits and re-run CI.

If the residue appears in tracked files on `main` but not in commit messages, remove it in a normal cleanup PR unless keeping the old blob visible is unacceptable for the approved reason.

## Break-Glass Procedure

1. Create a fresh clone in a temporary directory.
2. Confirm the active account has permission to force-push the target branch.
3. Search the tree and commit messages for the approved marker. Use the concrete marker string from the approval record, not a broad pattern.
4. Rewrite only the affected commits. Prefer a targeted history rewrite tool or an interactive rebase over a broad repository-wide rewrite.
5. Re-run the residue checker against the rewritten tree and rewritten commit range.
6. Re-run the repository's normal verification suite.
7. Force-push only the approved branch or branches.
8. Re-run GitHub Actions on the rewritten branch.
9. Notify maintainers with recovery steps.
10. Record the cleanup in the implementing pull request, issue, or repository-specific ADR named by the approval.

## Recovery Note Template

Use this shape when notifying maintainers:

```text
History was rewritten on <repo>/<branch> to remove approved source-control residue.

If you have no local changes:
  git fetch origin
  git switch <branch>
  git reset --hard origin/<branch>

If you have local changes:
  git fetch origin
  git switch <branch>
  git rebase --rebase-merges origin/<branch>

Contact the repository owner before force-pushing any stale local branch.
```

## Verification

After cleanup, confirm all of the following:

- The residue checker passes.
- The repository's normal CI checks pass.
- The affected marker no longer appears in tracked files.
- The affected marker no longer appears in the rewritten commit-message range.
- The force-push and recovery notice are documented.

## Do Not

- Do not rewrite history for routine typos or ordinary documentation cleanup.
- Do not rewrite every branch when one branch is affected.
- Do not use broad search patterns that can remove legitimate technical content.
- Do not delete release tags without a separate owner decision.
- Do not treat this runbook as approval; it is only the procedure after approval.
