<!--
  ==============================================================================
  ADR-0001 is the inaugural Architecture Decision Record for the
  NWarila organization. It serves three purposes simultaneously:

    1. The authoritative DECISION that ADRs are the documentation format
       used by the NWarila organization for architecturally
       significant choices.
    2. The canonical TEMPLATE that subsequent ADRs (org-baseline,
       type-template, and repository-specific alike) are copied from.
    3. The worked EXAMPLE that demonstrates a strong ADR in practice.

  Where ADRs live (per ADR-0001 §"Decision Outcome"):

    * Org-baseline ADRs: master copy in NWarila/.github at
      docs/decision-records/NNNN-short-kebab-title.md; byte-identical
      mirror in every adopting child repository at
      docs/decision-records/org/NNNN-short-kebab-title.md.
    * Type-template ADRs: master copy in the type-template repository
      (for example NWarila/terraform-runner-template) at
      docs/decision-records/template/NNNN-short-kebab-title.md;
      byte-identical mirror in every consumer of that template at
      docs/decision-records/template/NNNN-short-kebab-title.md.
    * Repository-specific ADRs: live only in their owning repository at
      docs/decision-records/repo/NNNN-short-kebab-title.md. Numbering
      namespace is independent of the org and template namespaces.

  How to author a new org-baseline ADR (in this NWarila/.github
  repository):

    1. Copy this file to a new file at
       docs/decision-records/NNNN-short-kebab-title.md, where NNNN is
       the next unused four-digit number in this repository's
       docs/decision-records/ directory, allocated monotonically and
       never reused.
    2. Delete this HTML comment block from the new file (keep it in the
       original 0001 so this file continues to serve as the template).
    3. Replace the title, the metadata table, and every section body with
       content that is true for the new decision. Keep the section
       headings in the order shown, including the Changelog.
    4. For sections or metadata fields that have no content, keep them
       and use one of two explicit values. Write "None." when the field
       applies but has zero entries. Write "N/A (reason)." when the field
       does not apply at all in this ADR's situation. Do not delete
       headings. A blank section tells the reader "I forgot"; an explicit
       "None." or "N/A" tells the reader "I considered this and there is
       nothing to record."
    5. Add an initial Changelog row that records the acceptance of the
       decision.
    6. Add a row to docs/decision-records/README.md's Index table.
    7. Open a pull request in this repository. On merge, mirror the new
       ADR into every adopting child repository's
       docs/decision-records/org/ directory (sync PRs per repo).

  How to author a new type-template ADR (in a type-template repository
  such as NWarila/terraform-runner-template): follow the same steps,
  but author the ADR in the type-template repository's
  docs/decision-records/template/ directory, and on merge mirror it into every
  consumer of that template's docs/decision-records/template/
  directory (sync PRs per consumer). The numbering namespace for
  template ADRs is per-template and independent of the org namespace.

  How to author a new repository-specific ADR (in any adopting child
  repository): follow the same steps, but place the file at
  docs/decision-records/repo/NNNN-short-kebab-title.md in that
  repository, list it in that repository's docs/decision-records/README.md,
  and do not mirror it anywhere.
  ==============================================================================
-->

# ADR-0001: Use Architecture Decision Records to Document Design Rationale

| Field            | Value                                                                       |
| ---------------- | --------------------------------------------------------------------------- |
| ID               | ADR-0001                                                                    |
| Scope            | Org baseline                                                                |
| Status           | Accepted                                                                    |
| Decision-subject | ADR scope, format, lifecycle, and maintenance rules for decision records.   |
| Date accepted    | 2026-04-22                                                                  |
| Date             | 2026-06-02                                                                  |
| Last reviewed    | 2026-06-02                                                                  |
| Authors          | Nick Warila (@NWarila)                                                      |
| Decision-makers  | Nick Warila (sole portfolio maintainer)                                     |
| Consulted        | None.                                                                       |
| Informed         | None.                                                                       |
| Reversibility    | Medium                                                                      |
| Review-by        | 2026-11-29                                                                  |

## TL;DR

We will use `docs/decision-records/` as the conventional home for architecturally significant decisions across the `NWarila` organization. ADRs are organized into three scopes: **org-baseline** ADRs whose master copies live in this `NWarila/.github` repository at `docs/decision-records/` and are mirrored into every adopting child repository at `docs/decision-records/org/`; **type-template** ADRs whose master copies live in a type-template repository (for example `NWarila/terraform-runner-template` for Terraform consumers) at `docs/decision-records/template/` and are mirrored into every consumer of that template at `docs/decision-records/template/`; and **repository-specific** ADRs that live only in their owning repository at `docs/decision-records/repo/`. The format is MADR 4.0-aligned but uses a visible Markdown metadata table, adds explicit reversibility, implementing-PR links, `Last reviewed`, an append-only Changelog, and a conservative compliance-notes crosswalk, and uses the more readable `decision-records` directory name in place of MADR's conventional `adr/`. Accepted ADRs are living records when the same decision subject evolves: update the record in place, preserve auditability in the Changelog, and reserve supersession or obsolescence for decisions whose subject has been replaced or is no longer applicable. This gives the organization a single source of truth for org-level governance that travels alongside the code in every adopting repository, a per-stack source of truth that travels alongside every consumer of a given type-template, and a place for each repository to record its own architectural choices without conflicting with either shared baseline.

## Context and Problem Statement

Every nontrivial repository accumulates architectural choices. Why is authentication handled one way and not another? Why was one platform or workflow chosen over another? Why does CI enforce one supply-chain posture instead of a weaker one? A year later, the code can still show *what* exists, but it rarely explains *why* it exists.

This `NWarila/.github` repository is the canonical home for org-level governance artifacts. ADRs that establish org-wide conventions (this one, the documentation framework, the source-control hygiene policy, etc.) are authored here and replicated into every adopting child repository. In addition to the org baseline, each repository may inherit decisions from a **type-template** — a per-stack template repository (for example `NWarila/terraform-runner-template` for Terraform consumers, or `NWarila/packer-framework-template` for Packer consumers) whose ADRs apply to every consumer of that stack but not to consumers of other stacks. Type-template ADRs cover decisions that are too specific for the org baseline (because they only matter to that stack) but too widely applicable for any single repository (because they recur across every consumer of the template). Repositories that participate inherit the org baseline by syncing the mirrored copies into their own `docs/decision-records/org/` directory, mirror their type-template's decisions into `docs/decision-records/template/`, and may add their own repository-scoped ADRs at `docs/decision-records/repo/` for decisions that affect only that repository.

Three audiences matter here:

1. **Future maintainers**, trying to determine whether a past decision still makes sense.
2. **Prospective collaborators, students, and hiring managers**, trying to understand the quality of judgment behind the work.
3. **Reviewers and auditors**, who may need source-controlled rationale for security-relevant or compliance-relevant design choices.

A wiki, a Notion page, a README section, or a folder of ad hoc design notes fails at least one of those audiences. External tools drift from code, READMEs get crowded with user-facing content, and loosely managed documents often disappear or become misleading as ownership changes.

Architecture Decision Records (ADRs) solve this well: they are lightweight, source-controlled, and widely understood. Michael Nygard introduced the pattern in 2011. ThoughtWorks later recommended lightweight ADRs in source control instead of a wiki or website, and MADR 4.0.0, released on 2024-09-17, provides a well-known community template that is easy to adapt. MADR does not require accepted records to be immutable; this portfolio deliberately uses a living ADR model with explicit changelog evidence instead of silently treating git history as the whole audit trail.

The remaining question is not whether to keep a decision log. It is which format to use, how much structure to require, and where those records should live.

## Decision Drivers

The following forces shaped this decision. Subsequent ADRs in repositories that adopt this baseline should name the drivers relevant to their own scope in this same section:

1. **Reader-first clarity.** A reader without deep software-architecture vocabulary should be able to open any ADR and follow the reasoning.
2. **Portfolio-grade professionalism.** The format should read as serious and disciplined without becoming performatively bureaucratic.
3. **Clone-and-use friendliness.** Another developer should be able to fork a repository and use its ADR structure immediately, with no proprietary tools or dashboards.
4. **Traceability.** Readers should be able to connect a decision to the code and pull requests that put it into effect.
5. **Compliance support without overclaim.** Security-relevant ADRs should make it easier to assemble review evidence without pretending that the document alone proves compliance.
6. **Durability.** The format should remain readable even if tools, vendors, or hosting platforms change.
7. **Low authoring friction.** If the format is painful to write, it will not be used consistently.

## Considered Options

1. **No formal decision documentation.** Rely on the README, git history, and commit messages.
2. **Wiki-hosted decision log.** Use GitHub Wiki, Confluence, Notion, or similar.
3. **Canonical Nygard ADRs.** Use the classic five-section ADR format.
4. **Vanilla MADR 4.0.** Use the community standard with its default structure and conventions.
5. **Custom MADR 4.0-aligned format with portfolio-specific extensions.** Keep MADR's core shape, but use a readable `decision-records` directory name, a visible Markdown metadata table, and add reversibility, implementing-PR traceability, and compliance notes.

## Decision Outcome

Chosen option: **Option 5, a MADR 4.0-aligned Markdown template with small portfolio-specific extensions.**

ADRs are organized into three scopes with independent four-digit numbering namespaces:

- **Org-baseline ADRs** capture decisions that apply to the entire `NWarila` organization, regardless of stack. Their master copies live in this `NWarila/.github` repository at `docs/decision-records/NNNN-short-kebab-title.md`. Every adopting child repository mirrors them at `docs/decision-records/org/NNNN-short-kebab-title.md` (identical content, copied byte-for-byte from the master). Numbers in the org namespace are allocated monotonically and never reused.

- **Type-template ADRs** capture decisions that apply to every repository derived from a particular type-template — for example, every Terraform consumer derived from `NWarila/terraform-runner-template`, or every Packer consumer derived from `NWarila/packer-framework-template`. They are the right home for decisions that are too stack-specific for the org baseline (because they only matter to that stack) and too widely applicable for any single repository (because they recur across every consumer of the template). Their master copies live in the type-template at `docs/decision-records/template/NNNN-short-kebab-title.md`. Every consumer of that template mirrors them at `docs/decision-records/template/NNNN-short-kebab-title.md` (identical content, copied byte-for-byte from the master). Numbers in a type-template's namespace are allocated monotonically per template and are independent of the org namespace and of every other type-template's namespace.

- **Repository-specific ADRs** capture decisions that apply only to one repository. They live in that repository at `docs/decision-records/repo/NNNN-short-kebab-title.md` and are not mirrored to any other repository, to the org `.github` repo, or to any type-template. Numbers in a repository's `repo` namespace are independent of the org and template namespaces; the same number can appear in `org/`, `template/`, and `repo/` without conflict because they are in different directories.

Within all three scopes, `NNNN` is the next unused four-digit number in that scope's own namespace, allocated monotonically and never reused. The directory name is `decision-records` because it is immediately understandable to readers who do not already know the acronym. The subdirectory split (`org/`, `template/`, `repo/`) keeps the three scopes visually and structurally distinct, so a reader scanning a repository can immediately see which decisions were inherited from the organization, which were inherited from the repository's type-template, and which were made locally.

ADRs follow the structure demonstrated by this file itself, in this order: metadata table, TL;DR, Context and Problem Statement, Decision Drivers, Considered Options, Decision Outcome, Pros and Cons of the Options, Confirmation, Consequences (Positive / Negative / Neutral), Assumptions, Supersedes, Superseded by, Implementing PRs, Related ADRs, Compliance Notes, and Changelog. Sections that genuinely do not apply are kept and filled with "None." or "N/A (reason)." so readers can distinguish "not applicable" from "forgotten."

The metadata table records `ID`, `Scope`, `Status`, `Decision-subject`, `Date accepted`, `Date`, `Last reviewed`, `Authors`, `Decision-makers`, `Consulted`, `Informed`, `Reversibility`, and `Review-by`. `Date accepted` is immutable once the ADR is accepted. `Date` follows MADR's "last updated" meaning. `Last reviewed` is the most recent explicit review date and is refreshed on the cadence for the ADR scope: 180 days for org-baseline and type-template ADRs, and 365 days for repository-specific ADRs.

A decision is **architecturally significant** and warrants an ADR when any of the following are true:

- It has multiple serious alternatives with nontrivial trade-offs.
- It shapes how future work in the repository will be done, not just one implementation task.
- It materially affects security, compliance posture, or supply-chain posture.
- A reader six months from now would reasonably ask "why did we choose X over Y?" and the answer will not be obvious from the code alone.

Decisions that are **not** ADR-worthy include forced choices with no practical alternatives, style-level preferences with negligible downstream impact, runbook procedures, and single-PR implementation details.

Accepted ADRs are living records when the same `Decision-subject` evolves. A pull request may update the decision, scope, rationale, consequences, or review metadata in place, but every substantive change MUST add a new Changelog row that says what changed, why, who or what role made the change, and whether the ADR body changed. When the active decision text changes, the prior text MUST remain recoverable in the Changelog row or in a `Previous decisions` subsection. A `Last reviewed` bump with no body change still requires an explicit re-review row. Supersession is reserved for a different-subject ADR that replaces this one; obsolescence is reserved for a subject that is no longer applicable and has no replacement.

This ADR is the canonical example for this baseline and the starting point for participating repositories in the portfolio. When another repository seeds its own `ADR-0001` from this file, it must rewrite the metadata, context, consequences, and compliance notes so the record is true for that repository.

## Pros and Cons of the Options

### Option 1: No formal decision documentation

- **Good, because** it has effectively zero authoring overhead.
- **Good, because** it requires no new conventions or templates.
- **Bad, because** reasoning behind important choices is quickly lost.
- **Bad, because** it leaves reviewers and future maintainers to reverse-engineer intent from code and commit messages.
- **Bad, because** it provides no durable source-controlled artifact for security-relevant design rationale.

### Option 2: Wiki-hosted decision log

- **Good, because** wikis are easy to edit and cross-link in a browser.
- **Good, because** they support long-form documentation well.
- **Bad, because** wiki or website content can drift away from the code it describes; ThoughtWorks explicitly recommends source control instead.
- **Bad, because** GitHub wikis are stored and cloned separately from the main repository, which weakens the "docs travel with the code" property.
- **Bad, because** externally hosted tools create additional access, lifecycle, and vendor dependencies.

### Option 3: Canonical Nygard ADRs

- **Good, because** the format is widely recognized and easy to explain.
- **Good, because** its five-section shape is approachable for non-specialist readers.
- **Neutral, because** its minimalism is a strength until stronger traceability or reviewability is needed.
- **Bad, because** it does not natively prompt explicit decision drivers, option-by-option trade-off analysis, or confirmation criteria.
- **Bad, because** reversibility, implementing-PR traceability, and compliance notes would all need to be reinvented locally as ad hoc extensions.

### Option 4: Vanilla MADR 4.0

- **Good, because** MADR 4.0.0 is a well-known and maintained community standard.
- **Good, because** Decision Drivers, Considered Options, option-level pros and cons, and Confirmation add rigor beyond the classic Nygard structure.
- **Good, because** YAML front matter and existing tooling make machine processing feasible.
- **Neutral, because** YAML front matter is slightly less approachable to some readers than a visible Markdown metadata table.
- **Bad, because** the default conventions do not capture this portfolio's preference for the clearer `decision-records` directory name.
- **Bad, because** reversibility, implementing PRs, and conservative compliance mapping still need local conventions.

### Option 5: Custom MADR 4.0-aligned format with portfolio-specific extensions (chosen)

- **Good, because** it stays close to MADR 4.0 while remaining easy to read in plain GitHub Markdown.
- **Good, because** the explicit `decision-records` directory name is clearer for first-time readers.
- **Good, because** a visible Markdown metadata table keeps key governance facts readable in rendered and raw form.
- **Good, because** an explicit **Reversibility** field encourages better judgment about how expensive it will be to change course later.
- **Good, because** **Implementing PRs** and supersession links improve traceability between rationale and code.
- **Good, because** **Compliance Notes** creates a place to record how a decision may support external review frameworks without claiming that the ADR alone proves compliance.
- **Neutral, because** the additional fields only need short entries when a decision is simple.
- **Bad, because** any future automation must target this exact schema rather than stock MADR.
- **Bad, because** readers familiar with vanilla MADR may need a brief orientation to the differences.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) conventions.

1. **Org-baseline mirror check.** A child repository that adopts this baseline MUST contain `docs/decision-records/org/` populated with byte-identical copies of every accepted org-baseline ADR from `NWarila/.github/docs/decision-records/`. A CI job or `pre-commit` hook MAY fail a pull request that adds an `org/` file that does not match the master, removes a master that still exists upstream, or omits a master that has been added upstream.
2. **Type-template mirror check.** A child repository derived from a type-template MUST contain `docs/decision-records/template/` populated with byte-identical copies of every accepted type-template ADR from that template's `docs/decision-records/template/`. The same CI mechanism that enforces the org-baseline mirror SHOULD enforce the template-baseline mirror, run once per type-template the repository derives from.
3. **Layout-skeleton check.** Every adopting child repository MUST contain a complete decision-records directory skeleton — `docs/decision-records/org/`, `docs/decision-records/template/`, and `docs/decision-records/repo/` — even when some scopes contain no ADRs yet. Empty scopes are kept in source control via byte-identical `.gitkeep` placeholders mirrored from the org canonical, so a reader scanning any repo immediately sees the same predictable layout regardless of which scopes are populated. *Content* in each scope remains opt-in per scope (a repo with no repository-specific decisions has an empty `repo/`; a repo that does not derive from a type-template has an empty `template/`); only the *layout* is mandatory.
4. **Repo-scope check.** Repository-specific ADRs MUST live at `docs/decision-records/repo/NNNN-short-kebab-title.md`. They MUST NOT appear in `docs/decision-records/org/` or `docs/decision-records/template/`, and MUST NOT be promoted to either namespace without first being authored as a new ADR in `NWarila/.github` (for the org baseline) or in the appropriate type-template (for a template baseline). A CI script MAY assert this directory split.
5. **Schema check.** A CI script SHOULD verify that every file matching `docs/decision-records/{org,template,repo}/[0-9][0-9][0-9][0-9]-*.md` contains the required section headings from this template: `## TL;DR`, `## Context and Problem Statement`, `## Decision Drivers`, `## Considered Options`, `## Decision Outcome`, `## Pros and Cons of the Options`, `## Confirmation`, `## Consequences`, `## Assumptions`, `## Supersedes`, `## Superseded by`, `## Implementing PRs`, `## Related ADRs`, `## Compliance Notes`, and `## Changelog`. `## Considered Options` and `## Pros and Cons of the Options` are especially important because they preserve rejected alternatives and trade-offs.
6. **Index check.** A repository that has any ADRs MUST contain `docs/decision-records/README.md` listing every ADR (org-mirrored, template-mirrored, and repo-specific, in clearly separated sections) with its current Status and Summary. A CI script SHOULD diff the directory listing against the index and fail on drift.
7. **Human review.** Every pull request that introduces a new ADR MUST be reviewed. Every pull request that materially contradicts an Accepted ADR SHOULD either update the code to comply, supersede the ADR, or explain why the ADR never actually applied to the change in question.
8. **Living-edit rule.** After acceptance, edits MAY change the decision, scope, rationale, consequences, Status, review metadata, supersession fields, or `Implementing PRs` only when the change is explicit in the pull request and recorded in a new Changelog row. Silent changes to the decision body are not allowed.
9. **Changelog check.** CI SHOULD reject a changed ADR when an ADR body diff has no new Changelog row, a `Last reviewed` value advances without either a body diff or an explicit re-review row, a Changelog row was removed or modified instead of appended, a `Superseded` status lacks a resolvable `Superseded by` link, or a supersession link is not reciprocal.

Enforcement tooling is recommended but not mandatory at acceptance time. A solo-maintainer repository MAY rely on manual discipline; a team repository or a compliance-critical repository SHOULD automate at least the presence, schema, index, and living-edit checks.

## Consequences

### Positive

- Decisions are explained, findable, and version-controlled alongside the code they govern.
- The explicit `decision-records` directory name is easier for first-time readers to understand.
- Reviewers, contributors, and hiring audiences can reconstruct the reasoning behind important architectural choices without a synchronous conversation.
- Security-relevant ADRs can contribute reusable evidence for reviews, assessments, and compliance preparation.
- The format is self-documenting: this ADR both adopts the format and demonstrates how to use it.
- Living ADRs keep active decisions current without forcing readers to chase a chain of same-subject replacement records.
- The Changelog is the primary audit trail for ADR edits and survives squash merges, mirrors, and automation-authored sync commits better than git history alone.

### Negative

- Every architecturally significant change now carries some documentation overhead.
- The format is custom enough that future automation and linting will likely need repository-specific support.
- If an adopting repository copies this ADR mechanically instead of rewriting repository-specific content, it can create a polished but false record.
- Without enforcement tooling, ADRs can still drift from the code they describe.
- Living updates require reviewer discipline; without a meaningful Changelog row, they can hide the same decision drift they are meant to prevent.

### Neutral

- The directory layout `docs/decision-records/{org,template,repo}/` and the filename pattern `NNNN-short-kebab-title.md` are established conventions for the organization.
- Each adopting repository's `docs/decision-records/README.md` becomes the canonical local index for its full ADR set (org-mirrored, template-mirrored, and repo-specific) and is the single page to read to understand the repository's decision posture.
- Future repositories may introduce carefully scoped local extensions, but those should be documented in their own repo-specific ADRs (under `docs/decision-records/repo/`) rather than by silently mutating this baseline or any type-template baseline.
- Org-baseline ADRs and type-template ADRs are duplicated content (masters in their respective canonical repositories; mirrors in every adopting child repo). The duplication is deliberate — it keeps governance content traveling with the code that implements it — but it means amendments to either upstream require a coordinated update across all adopting repositories.
- Git history corroborates ADR evolution, but the in-document Changelog is the reader-facing record of what changed and why.

## Assumptions

This decision rests on the following assumptions. If any becomes false, this ADR should be revisited:

1. GitHub, or an equivalent Git-hosting service, remains the primary home for source control in repositories that adopt this baseline.
2. Markdown remains a widely supported, human-readable plain-text format.
3. Participating repositories continue to benefit from keeping governance artifacts near the code instead of in a separate knowledge base.
4. Repositories using this template have a clear decision-making path. In a solo-maintainer repository that may be the maintainer; in a team repository it may be a designated approver or architecture owner.
5. Pull requests that change ADRs have enough base-branch context for CI to detect whether a body diff or Changelog diff occurred.

## Supersedes

None. This is the inaugural ADR.

## Superseded by

None (current).

## Implementing PRs

This section lists downstream pull requests that implement or operationalize the decision described in this ADR. It does not need to list the pull request that introduced the ADR itself; that is already discoverable from version control. This is one of the few sections expected to gain entries after acceptance.

None yet. The primary expected follow-ons for this ADR are enforcement checks for presence, schema, and index drift, plus propagation of the structure into participating repositories that adopt this baseline.

## Related ADRs

None at this time. Subsequent ADRs that depend on this one, refine this format, or add repository-specific extensions should back-link here in their own `Related ADRs` sections.

## Compliance Notes

This ADR establishes a documentation mechanism, not a deployed security control. Its value is evidentiary: later ADRs can capture rationale, alternatives, and security trade-offs in a form that is reusable during reviews. The table below indicates where such evidence may help; it is illustrative rather than exhaustive, and it is not a claim that a repository is compliant merely because ADRs exist.

| Framework              | Control / Practice ID                                    | Potential Evidence Contribution                                                                 |
| ---------------------- | -------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| NIST SP 800-53 Rev. 5  | SA-17 (Developer Security and Privacy Architecture and Design) | ADRs can document the architecture and design rationale considered during development.     |
| NIST SP 800-53 Rev. 5  | PL-8 (Security and Privacy Architectures)                | ADRs can support architecture narratives and link design choices to source-controlled artifacts. |
| NIST SP 800-53 Rev. 5  | SA-8 (Security and Privacy Engineering Principles)       | Security-relevant ADRs can record how engineering principles shaped specific choices.          |
| NIST SP 800-218 (SSDF) | PW.1 (Design Software to Meet Security Requirements and Mitigate Security Risks) | Security-focused ADRs can record identified risks, planned mitigations, and why a requirement was accepted, relaxed, or judged out of scope. |
| FedRAMP SSP artifacts  | System-description and architecture narratives           | ADRs can provide reusable source material and traceability for SSP drafting, but they do not replace the SSP or the assessment evidence set. |

Subsequent ADRs should keep only the rows that genuinely apply to the decision at hand and should describe the relationship conservatively.

## Changelog

| Date       | Change                                      | Reason                                                    | Author/Role                       | Body-diff? |
| ---------- | ------------------------------------------- | --------------------------------------------------------- | --------------------------------- | ---------- |
| 2026-06-02 | Adopted the living ADR lifecycle guardrails. | Keep accepted ADRs current while preserving auditability. | Portfolio maintainer / governance | Yes        |
