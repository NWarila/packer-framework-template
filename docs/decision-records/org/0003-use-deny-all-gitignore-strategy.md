# ADR-0003: Use a Deny-All `.gitignore` Strategy

| Field          | Value                                    |
| -------------- | ---------------------------------------- |
| Status         | Accepted                                 |
| Date           | 2026-04-25                               |
| Authors        | Nick Warila (@NWarila)                   |
| Decision-maker | Nick Warila (sole portfolio maintainer)  |
| Consulted      | None.                                    |
| Informed       | None.                                    |
| Reversibility  | Cheap                                    |
| Review-by      | N/A (Accepted)                           |

## TL;DR

In repositories that adopt this baseline, `.gitignore` is structured as **deny-all by default** with an **explicit allowlist** of files and directories that are intended to be tracked. The first non-comment rule in `.gitignore` is `**` (ignore everything), followed by `!`-prefixed allowlist entries. New files are not tracked unless their path is explicitly added to the allowlist. This inverts the dominant `.gitignore` convention (allow-all with scattered denies) in exchange for default-safe behaviour: secrets, terraform state, build artifacts, IDE files, and any future class of accidentally-introduced sensitive content cannot enter the repository through `git add` alone.

## Context and Problem Statement

The default `.gitignore` convention across the open-source community is **allow-all with explicit denies**: a base of "track everything" with a list of patterns to ignore. Tooling reinforces this default — IDEs, scaffolding tools, and language ecosystems ship pre-built `.gitignore` files that enumerate known build artifacts, vendor directories, and temporary files for that ecosystem.

The dominant convention has a structural failure mode: anything *not* in the deny list is tracked. New tooling, new build outputs, new artifact types, and new categories of sensitive file all default to tracked. The list of patterns to deny is open-ended and grows with every new tool a repository adopts. A repository that integrates a new tool without simultaneously updating `.gitignore` silently begins tracking that tool's outputs.

For the categories of file that matter most to a security-aware portfolio, this failure mode is dangerous:

1. **Credentials.** `.env`, `credentials.json`, `.aws/`, OAuth tokens, GitHub Personal Access Tokens accidentally written to disk by a script.
2. **Terraform state.** `terraform.tfstate` files contain decrypted secrets and resource metadata in plaintext after `apply`. A leaked tfstate is an immediate compromise of the infrastructure it describes.
3. **Build artifacts.** Compiled binaries, bundled JavaScript, container layers, and similar outputs that bloat the repository and add no source-of-truth value.
4. **Personal-environment leakage.** IDE configuration, editor swap files, OS-level metadata files (`.DS_Store`, `Thumbs.db`, `desktop.ini`).
5. **Tool-specific transient files.** `.terraform/` plugin caches, `node_modules/` (when the project intends to commit `package-lock.json` only), `__pycache__/`, `.coverage`, `.pytest_cache/`, and a long tail.

A repository that uses the dominant convention defends against (5) and parts of (3) and (4) only because someone, at some point, added each pattern to `.gitignore`. The defence against (1) and (2) is implicit — *if* the repository's `.gitignore` was thoughtful enough to deny `*.env`, `*.tfstate`, etc., the file is excluded; otherwise it is tracked the moment someone runs `git add .`. There is no signal at the moment of failure: `git add` does not distinguish between intended commits and accidental commits, and `git status` shows the file as a normal addition.

This portfolio's `github-terraform-framework` repository has carried a deny-all `.gitignore` since its initial commit, and the strategy has prevented multiple categories of accidental commit during normal development. The remaining question is whether to elevate that ad hoc choice into an explicit, named decision that other repositories in the portfolio inherit, and to document the trade-offs honestly so future contributors understand both the value and the friction.

## Decision Drivers

The following forces shaped this decision:

1. **Default-safe behaviour.** A new file should be ignored unless explicit action is taken to track it. The cost of one extra allowlist line is negligible; the cost of one accidentally committed credential is potentially catastrophic.
2. **Reviewability.** Every new tracked file should be visible in pull-request review as an `.gitignore` allowlist edit, not as a silent inclusion. This makes "what files does this PR start tracking?" a single grep, not a directory walk.
3. **Failure-mode visibility.** The strategy should fail in a way that is *visible*. A file that is silently ignored is bad if the contributor expected it to be tracked; the absence from `git status` should be diagnosable in seconds with documented tooling.
4. **Consistency across repositories.** Contributors who learn the pattern in one repository should encounter the same pattern in others. Mixing strategies across the portfolio costs cognitive overhead disproportionate to any per-repo optimisation.
5. **Reversibility.** A repository that adopts this strategy and later regrets it should be able to migrate back to allow-all-with-denies in a single PR. The choice should not lock the repository in.
6. **Compatibility with established tooling.** Pre-commit hooks, CI lint stages, and IDE integrations should not need to be retrained. The strategy must use only standard `.gitignore` syntax.
7. **Community familiarity.** The dominant convention is allow-all-with-denies. Choosing the opposite imposes a learning cost on contributors. The strategy should carry enough documentation that the cost is paid once, by the contributor's first encounter, not repeatedly.

## Considered Options

1. **No `.gitignore`.** Track every file in the working directory.
2. **Allow-all with explicit denies (community default).** Use a base of "track everything" with `.gitignore` entries that enumerate patterns to skip.
3. **Hybrid.** Allow-all base with periodic deny additions, supplemented by ad hoc per-directory `.gitignore` files.
4. **Deny-all with explicit allowlist (chosen).** First non-comment rule is `**` (ignore everything); subsequent `!`-prefixed entries explicitly allowlist tracked paths.
5. **`git add` discipline only.** No `.gitignore`; rely on contributors to use `git add <path>` rather than `git add .`.
6. **Sparse checkout / worktree partitioning.** Use git's sparse-checkout to limit which files are visible.

## Decision Outcome

Chosen option: **Option 4, deny-all with an explicit allowlist.**

In a repository that adopts this baseline, `.gitignore` is organised as follows:

1. The first non-comment rule is `**` (or an equivalent globstar that excludes the entire working tree).
2. Subsequent rules are `!`-prefixed allowlist entries that re-include specific files and directories. Allowlist entries are organised in groups corresponding to the categories of tracked content (source code, configuration, fixtures, documentation, CI workflows, license, README).
3. Each allowlist group is preceded by a `#`-prefixed comment that names the group and, where useful, explains why those entries are tracked.
4. New files added to the repository require an `.gitignore` allowlist edit. The allowlist edit and the new file MUST be in the same pull request and ideally in the same commit. A pull request that adds a file without allowlisting it is a reviewer-detectable defect: the new file will not appear in `git status` after `git add`.
5. Directories require **two** allowlist entries: one for the directory itself (`!/path/to/dir/`) and one for its contents (`!/path/to/dir/**`). A single entry of either form does not suffice in all git versions.

The strategy applies recursively. A repository's top-level `.gitignore` SHOULD carry the deny-all rule and the full allowlist. Per-directory `.gitignore` files MAY exist but MUST NOT contradict the top-level deny: a per-directory file may add denials, never re-add allows.

This baseline ADR establishes the default. Repositories that have a sustained reason to opt out — for example, a repository whose primary purpose is hosting a large generated artifact tree where allowlisting every file is impractical — MAY do so by recording a repository-level ADR that supersedes ADR-0003 in scope. An opt-out is itself an architectural decision and is treated as such.

The strategy explicitly does not prescribe enforcement tooling. A pre-commit hook, CI check, or `git hook` MAY verify that the first non-comment line of `.gitignore` is the deny-all rule, that the allowlist contains no contradictions, or that every tracked file in the working tree is explicitly allowlisted. None of these checks are mandatory at acceptance time. Adopting repositories MAY add them as separate decisions.

## Pros and Cons of the Options

### Option 1: No `.gitignore`

- **Good, because** it has zero authoring overhead and zero rule maintenance.
- **Bad, because** every transient file (build artifacts, IDE files, OS metadata, secrets) lands in pull requests by default.
- **Bad, because** it is not a viable strategy for any real-world repository and is included only for completeness.

### Option 2: Allow-all with explicit denies (community default)

- **Good, because** it is the dominant convention; contributors recognise it without explanation.
- **Good, because** language and tool ecosystems ship pre-built `.gitignore` files that contributors can drop in.
- **Good, because** small repositories with predictable noise (a single language, a single build system) can rely on community templates with minimal customisation.
- **Neutral, because** the rule list grows over time with every new tool the repository adopts.
- **Bad, because** anything *not* in the deny list is tracked by default. New file types slip through silently.
- **Bad, because** the failure mode for sensitive files (credentials, state, secrets) is "tracked unless explicitly denied." A forgotten deny is a security incident.
- **Bad, because** there is no review-time signal that a new tracked file was *intentionally* tracked rather than accidentally swept in by `git add .`.

### Option 3: Hybrid

- **Good, because** it allows incremental adoption: existing allow-all repositories can add per-directory denies without restructuring the top-level file.
- **Bad, because** it inherits all of Option 2's failure modes.
- **Bad, because** per-directory `.gitignore` files are easy to overlook; the strategy is implicitly distributed and hard to audit.
- **Bad, because** it picks the worst of both ends: contributors must understand both top-level and per-directory rules, but the safety properties of deny-all are not gained.

### Option 4: Deny-all with explicit allowlist (chosen)

- **Good, because** new files default to ignored; sensitive files (credentials, state, secrets) cannot enter the repository through `git add` alone.
- **Good, because** each new tracked file is an explicit, reviewable allowlist edit. "What files does this PR begin tracking?" reduces to a `.gitignore` diff.
- **Good, because** the inventory of intentionally tracked file paths *is* `.gitignore` itself; the file becomes self-documenting.
- **Good, because** the failure mode (a file not appearing in `git status` after `git add`) is detectable in seconds with `git check-ignore -v <path>`, which names the rule that is excluding it.
- **Good, because** it requires only standard `.gitignore` syntax; pre-commit hooks, IDEs, and CI tooling work without modification.
- **Neutral, because** the initial setup of the allowlist for an existing repository is a one-time effort proportional to the breadth of currently tracked content.
- **Bad, because** it is unusual; contributors familiar only with the dominant convention can be surprised when a new file does not appear in `git status`.
- **Bad, because** a directory addition requires two allowlist entries (the directory and its contents); the most-elegant single-entry form `!/foo/**` does not allow the directory itself in all git versions.
- **Bad, because** repositories that legitimately track a very large number of file types (e.g., a generated documentation site with thousands of files) face high allowlist-maintenance overhead. Such repositories should consider opting out.

### Option 5: `git add` discipline only

- **Good, because** it imposes no rule maintenance.
- **Bad, because** human discipline is the weakest possible control. A single `git add .` undoes years of careful commits.
- **Bad, because** it provides no defence against IDE-driven file additions, automated tooling, or contributors unfamiliar with the discipline.
- **Bad, because** it provides no review-time signal for intentional vs. accidental tracking.

### Option 6: Sparse checkout / worktree partitioning

- **Good, because** it limits the surface area of `git add .` per checkout configuration.
- **Bad, because** sparse checkout is a *per-clone* setting, not a repository property. It does not protect contributors who do not configure it.
- **Bad, because** it is a checkout strategy, not a tracking strategy. Files outside the sparse area are still tracked in the repository if they were ever committed.
- **Bad, because** it adds significant tooling complexity that is disproportionate to the problem being solved.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) conventions.

1. **Structural check.** A repository that adopts this baseline MUST contain a top-level `.gitignore` whose first non-comment, non-blank line is `**` (or an equivalent globstar excluding the entire working tree). A `pre-commit` hook or CI script MAY assert this.
2. **Allowlist-only-after-deny check.** All `!`-prefixed allowlist entries in the top-level `.gitignore` MUST appear *after* the deny-all rule. A reversed order silently negates the strategy. A CI script MAY assert this.
3. **No-orphan-tracked-files check.** Every file in `git ls-files` SHOULD have a corresponding `!`-prefixed allowlist entry. A CI script MAY enforce this; in practice it is reviewer-detectable because adding a file without allowlisting it produces `git status: nothing to commit` after `git add`.
4. **Per-directory file scope.** Per-directory `.gitignore` files MAY exist but MUST NOT contain `!`-prefixed entries that re-allow content that the top-level deny-all rule excludes. A reviewer SHOULD reject any per-directory allow that contradicts the top-level intent.
5. **PR review rule.** Pull requests that add new tracked files MUST modify `.gitignore` in the same change. A reviewer SHOULD reject a PR that introduces a new file without a corresponding allowlist edit; a CI check MAY automate the detection.
6. **Opt-out rule.** A repository that opts out of this strategy MUST record a repository-level ADR that names ADR-0003 in its `Supersedes` section (scoped to that repository) and explains why the trade-offs differ.

Enforcement tooling is recommended but not mandatory at acceptance time. A solo-maintainer repository MAY rely on manual discipline; a team repository or a compliance-critical repository SHOULD automate at least the structural and allowlist-only-after-deny checks.

## Consequences

### Positive

- New files default to ignored. Credentials, terraform state, build artifacts, and IDE files cannot enter the repository through `git add .` alone.
- Each new tracked file is an explicit allowlist edit, visible in pull-request review.
- `.gitignore` becomes the inventory of intentionally tracked content, making the repository's tracked surface auditable from a single file.
- The diagnostic for "why isn't this file showing up?" is `git check-ignore -v <path>`, which names the rule responsible — fast and unambiguous.
- The strategy applies uniformly across the portfolio: contributors learn it once and recognise it everywhere it is adopted.

### Negative

- Initial allowlist setup is a one-time effort per repository. For an existing repository, this means walking `git ls-files` and producing the allowlist that matches it.
- Contributors unfamiliar with the pattern may be surprised when a new file does not appear in `git status`. This is mitigated by documentation but not eliminated.
- Each new directory requires two allowlist entries. The most-elegant single-entry form is not portable.
- Repositories that legitimately track very large generated trees may find the per-file allowlist impractical and should opt out.

### Neutral

- Repositories MAY adopt enforcement tooling (pre-commit hooks, CI checks). The strategy works without it but is more durable with it.
- Per-directory `.gitignore` files are not forbidden but are constrained to additive denies; they cannot re-allow content excluded at the top level.
- The dominant community convention (allow-all with denies) remains the default outside this portfolio. Contributors who work across both conventions must context-switch.

## Assumptions

This decision rests on the following assumptions. If any becomes false, this ADR should be revisited:

1. Git's `**` and `!`-prefixed pattern semantics continue to behave as documented in `gitignore(5)`.
2. Adopting repositories' tooling (IDEs, pre-commit, CI, vendor-specific build systems) does not require allow-all `.gitignore` semantics to function. To date, none observed in this portfolio do.
3. Contributors to adopting repositories have access to this ADR and to the per-repository `.gitignore` documentation, so the unfamiliar pattern is learnable in seconds.
4. Repositories that legitimately need allow-all semantics are a minority and will opt out via repository-level ADR rather than pretending to adopt this baseline.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

This section lists downstream pull requests that implement or operationalize the decision described in this ADR. It does not need to list the pull request that introduced the ADR itself.

`github-terraform-framework` already implements this strategy and predates the ADR; the implementation does not require a new PR. Subsequent adopting repositories will record their adoption in this section as they migrate.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) — establishes the ADR convention. ADR-0003 is governed by ADR-0001's format and lifecycle rules.
- [ADR-0002](0002-adopt-diataxis-documentation-framework.md) — establishes the Diátaxis documentation framework. Companion documentation for ADR-0003 (an explanation of how the strategy works in practice and a how-to for adding allowlist entries) belongs in adopting repositories' `docs/explanation/` and `docs/how-to/` directories per ADR-0002.

## Compliance Notes

This ADR establishes a source-control hygiene practice that contributes to the prevention of accidental disclosure of sensitive information. The table below indicates where evidence produced under this convention may help during reviews; it is illustrative rather than exhaustive, and is not a claim that a repository is compliant merely because the strategy is adopted.

| Framework              | Control / Practice ID                                                | Potential Evidence Contribution                                                                                                                                                                |
| ---------------------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| NIST SP 800-53 Rev. 5  | SC-28 (Protection of Information at Rest)                            | A deny-all `.gitignore` reduces the risk that sensitive at-rest content (terraform state, credentials, environment files) enters version control through accidental `git add` operations. |
| NIST SP 800-53 Rev. 5  | SI-12 (Information Management and Retention)                         | Explicitly allowlisting tracked content provides a source-of-truth inventory of what data the repository retains.                                                                            |
| NIST SP 800-53 Rev. 5  | IA-5 (Authenticator Management)                                      | The strategy contributes to authenticator-management hygiene by blocking common credential-bearing files (`.env`, `credentials.json`, `*.pem`, `*.key`) from accidental commit.              |
| NIST SP 800-218 (SSDF) | PS.1 (Protect All Forms of Code from Unauthorized Access and Tampering) | The pull-request-visible `.gitignore` allowlist edit creates a reviewable trail of what content is intentionally added to the source-controlled artifact set.                              |
| OWASP                  | A02:2021 — Cryptographic Failures                                    | Default-blocking `.env`, `*.key`, `*.pem`, and similar files reduces the most common vector for cryptographic-material disclosure: accidental commit.                                       |

Subsequent repository-level ADRs that scope this convention to specific compliance contexts should keep only the rows that genuinely apply to their decision.
