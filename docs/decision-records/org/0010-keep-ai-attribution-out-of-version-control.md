# ADR-0010: Keep AI Attribution Out of Version Control

| Field            | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| ID               | ADR-0010                                                                    |
| Scope            | Org baseline                                                                |
| Status           | Accepted                                                                    |
| Decision-subject | Attribution hygiene for commits, code, documentation, and generated assets. |
| Date accepted    | 2026-06-02                                                                  |
| Date             | 2026-06-02                                                                  |
| Last reviewed    | 2026-06-02                                                                  |
| Authors          | Nick Warila (@NWarila)                                                      |
| Decision-makers  | Nick Warila (sole portfolio maintainer)                                     |
| Consulted        | Repository cleanup findings from public portfolio polishing work.           |
| Informed         | Maintainers of adopting repositories under `NWarila`.                       |
| Reversibility    | Low                                                                         |
| Review-by        | 2026-11-29                                                                  |

## TL;DR

Version-controlled artifacts in `NWarila/*` repositories must read as maintainer-owned work. Commits, code, documentation, templates, and generated assets must not include assistant-tool bylines, generated-by footers, automated coauthor trailers, or similar public attribution residue. The rule is about source-control hygiene and audience clarity; it does not forbid using tools during private drafting or implementation. A CI gate scans the tree and PR commit messages for known attribution markers. History rewrites are allowed only as a narrowly approved break-glass cleanup when public residue cannot be corrected by an ordinary follow-up commit.

## Context and Problem Statement

The portfolio is intended to be recruiter-readable, learner-readable, and maintainer-readable. Public source history should show the maintainer's engineering judgment, not scattered drafting-tool metadata. Tool bylines and generated footers are noisy in code review, make polished repositories look unfinished, and can create confusion about who owns the design.

The same residue can appear in several places: commit messages, documentation footers, generated asset comments, pull request body drafts copied into files, and rewritten-history cleanup notes. Because the pattern is easy to miss during manual review, it needs both a policy decision and a small automated check.

This decision does not hide collaboration or misrepresent authorship. It sets the standard that public version-controlled artifacts are curated maintainer outputs. Drafting transcripts, prompts, and work logs belong in temporary scratch space, not in repositories.

## Decision Drivers

1. **Maintainer ownership.** Public source should represent intentional maintainer-authored repository state.
2. **Recruiter clarity.** Portfolio repositories should not advertise private drafting mechanics.
3. **Review signal.** Tool attribution footers and trailers distract from the engineering change.
4. **Repeatability.** A small scan can catch common residue before it merges.
5. **Cleanup discipline.** History rewriting should be rare, explicit, and gated.

## Considered Options

1. Allow assistant-tool attribution residue when it is accurate.
2. Rely on manual review to remove residue.
3. Forbid residue in version control and enforce the rule with a CI scan plus a narrow break-glass cleanup runbook.

## Decision Outcome

Chosen option: **Option 3, forbid attribution residue in version control and enforce the rule with a CI scan plus a narrow break-glass cleanup runbook.**

Repositories must not commit assistant-tool attribution markers in tracked files or PR commit messages. Examples of disallowed marker categories include generated-by footers, assistant-tool bylines, automated coauthor trailers, tool-branded comments, and copied prompt or transcript headers.

The rule applies to:

- Commit subjects and bodies in the PR range.
- Source code and scripts.
- Markdown documentation.
- Workflow files, templates, and configuration.
- Generated assets when those assets are checked into source control.

The rule does not apply to:

- Private scratch files outside repositories.
- Local notes that are never committed.
- Ordinary references to machine learning, automation, or artificial intelligence when they are the subject matter of a repository or decision.
- Dependency names or vulnerability reports when the term is part of the real technical artifact being handled.

When residue is found before merge, the normal fix is to amend or replace the PR commit and remove the tracked text. When residue already exists on public protected history and cannot be corrected without leaving the residue visible, a history rewrite may be approved as a break-glass exception. Such a rewrite must be scoped to the affected repository, announced to affected maintainers, and followed by force-push recovery instructions.

## Pros and Cons of the Options

### Option 1: Allow attribution residue

- **Good, because** it avoids cleanup work.
- **Good, because** it may preserve details about drafting tools.
- **Bad, because** public repositories look less curated.
- **Bad, because** the residue distracts from maintainer judgment.
- **Bad, because** copied tool metadata can leak private drafting context.

### Option 2: Manual review only

- **Good, because** no automation is needed.
- **Good, because** reviewers can consider context.
- **Bad, because** residue is easy to miss.
- **Bad, because** the same issue recurs across repositories.
- **Bad, because** cleanup after merge is more disruptive than pre-merge rejection.

### Option 3: Policy plus CI gate

- **Good, because** common residue is caught before merge.
- **Good, because** the public standard is explicit.
- **Good, because** the break-glass rewrite path is constrained.
- **Good, because** private tool use remains outside the repository standard.
- **Neutral, because** rare false positives need reviewer judgment.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows RFC 2119 conventions.

1. **Tree scan.** CI MUST scan tracked text files for known assistant-tool attribution markers.
2. **Commit-message scan.** Pull request CI SHOULD scan commit subjects and bodies in the PR range for the same marker categories.
3. **Review check.** Reviewers SHOULD reject copied prompt logs, transcript headers, bylines, generated-by footers, and assistant coauthor trailers in repository files.
4. **Scratch-space check.** Temporary prompts, logs, and PR-body drafts SHOULD stay in scratch paths outside repositories.
5. **Break-glass check.** Any history rewrite to purge merged residue MUST be explicitly approved, narrowly scoped, and followed by recovery instructions.
6. **False-positive check.** If a repository legitimately discusses a term that resembles an attribution marker, the exception MUST be documented in the residue checker or repository-specific ADR.

## Consequences

### Positive

- Public repositories read as curated maintainer-owned work.
- Common residue is caught before it merges.
- Cleanup expectations are explicit.
- The portfolio avoids advertising private drafting mechanics.

### Negative

- Contributors must clean commit messages and files before merge.
- The scanner may need maintenance as new residue forms appear.
- Rare already-published cleanup may require disruptive history surgery.

### Neutral

- This ADR does not forbid using tools privately during implementation.
- This ADR does not change commit-signing, review, or branch-protection rules.
- This ADR does not require rewriting history unless the owner approves a specific cleanup.

## Assumptions

1. Public repository history is part of the portfolio's presentation surface.
2. Contributors can keep temporary drafting artifacts outside repositories.
3. The initial scanner catches known marker families and can be extended.
4. Break-glass history rewrites remain rare.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

None yet; this ADR is implemented by the residue checker and CI wiring added in the same governance change.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) defines ADR traceability and living changelog rules.
- [ADR-0002](0002-adopt-diataxis-documentation-framework.md) keeps operational cleanup procedure in a runbook rather than in the ADR body.
- [ADR-0009](0009-classify-baseline-manifest-byte-identity.md) defines which shared governance docs are mirrored exactly.

## Compliance Notes

This decision supports source-control hygiene, authorship clarity, and public portfolio presentation. It does not make a legal authorship claim and does not replace normal review, signing, or branch-protection controls.

## Changelog

| Date       | Change                                    | Reason                                      | Author/Role                       | Body-diff? |
| ---------- | ----------------------------------------- | ------------------------------------------- | --------------------------------- | ---------- |
| 2026-06-02 | Accepted version-control attribution hygiene and the residue scanning requirement. | Extract durable cleanup doctrine from public portfolio polishing work. | Portfolio maintainer / governance | Yes        |
