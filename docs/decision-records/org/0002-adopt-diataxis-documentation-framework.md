# ADR-0002: Adopt Diátaxis as the Documentation Framework

| Field          | Value                                    |
| -------------- | ---------------------------------------- |
| Status         | Accepted                                 |
| Date           | 2026-04-24                               |
| Authors        | Nick Warila (@NWarila)                   |
| Decision-maker | Nick Warila (sole portfolio maintainer)  |
| Consulted      | None.                                    |
| Informed       | None.                                    |
| Reversibility  | Medium                                   |
| Review-by      | N/A (Accepted)                           |

## TL;DR

We will use the [Diátaxis](https://diataxis.fr) documentation framework for all non-ADR documentation in repositories that adopt this baseline. Each adopting repository organizes long-form documentation into the four Diátaxis quadrants — **tutorials**, **how-to guides**, **reference**, and **explanation** — under a `docs/` directory whose immediate subdirectories mirror those quadrant names. ADRs themselves remain governed by [ADR-0001](0001-use-architecture-decision-records.md) and live in their own subtree at `docs/decision-records/{org,template,repo}/` (org-mirrored, template-mirrored, or repository-specific). This gives every repository a consistent, reader-first information architecture that is easy to navigate, easy to maintain, and easy for new contributors to understand.

## Context and Problem Statement

[ADR-0001](0001-use-architecture-decision-records.md) established a format for *decisions*, but a repository's documentation surface is much larger than its decision log. Repositories accumulate setup procedures, permission matrices, troubleshooting guides, conceptual explainers, contributor onboarding material, and operational runbooks. Without a shared organizing principle, that material lands wherever the original author thought to put it — a `README.md` section, a long monolithic design document, a folder of unstructured Markdown files, or worse, an out-of-band tool.

Three failure modes consistently follow from ad-hoc documentation organization:

1. **Drift.** Reference material, procedural material, and conceptual material accumulate in the same file. Updates to one type silently invalidate the others, and readers cannot tell which sentences are authoritative reference and which are narrative explanation.
2. **Findability collapse.** A reader who needs a specific permission, a specific command, or a specific definition cannot predict where to look. Repositories develop "you have to know to look in `DESIGN.md` §15.2" tribal knowledge.
3. **Authoring paralysis.** Without a framework that names what kind of document is needed, every contributor reinvents structure from scratch. Some attempts produce comprehensive prose explainers when a one-page reference would suffice; others produce bare command listings when readers actually need conceptual grounding.

This portfolio is solo-maintained today but is built to be reviewable, hireable-from, and potentially shared with collaborators. Documentation that fails the three modes above is invisible work: it costs time to write, costs time to maintain, and produces little durable value.

The remaining question is which documentation framework to adopt. The choice has to balance authoring cost, reader experience, durability against the framework's own future, and accessibility for solo and small-team maintainers.

## Decision Drivers

The following forces shaped this decision:

1. **Reader-first organization.** A reader's first question is rarely "what topic is this?" — it is usually "what am I trying to do?" The framework should organize by user need, not by author convenience.
2. **Authorial clarity.** A contributor sitting down to write should know what kind of document they are producing before they begin. A framework that names doc types reduces the "what should this be?" decision to a one-step lookup.
3. **Findability.** A reader who has visited the documentation once should be able to predict the location of any subsequent piece of information from the framework's conventions alone.
4. **Active community and durability.** The framework's own home should still be active in five years. Frameworks whose flagship implementations are archived create future migration cost.
5. **Named-adopter signal.** Adoption by recognized organizations is empirical evidence that the framework survives contact with real engineering teams.
6. **Accessibility.** A solo maintainer must be able to produce a useful first draft without building tooling, hiring a writer, or reading a 200-page manual on documentation theory.
7. **Co-existence with ADR-0001.** Whatever framework is chosen must accommodate ADRs as a distinct, separately governed artifact rather than competing with them.
8. **Co-existence with operational reality.** Some real-world documentation is composite by necessity — runbooks naturally combine reference, procedure, and troubleshooting. The framework must accommodate composite documents without forcing artificial fragmentation.

## Considered Options

1. **No formal documentation framework.** Continue with ad-hoc structure: `README.md`, monolithic `DESIGN.md`, scattered notes.
2. **POSIX `man(7)` format.** Use the Unix manual-page convention with `NAME / SYNOPSIS / DESCRIPTION / OPTIONS / EXAMPLES / SEE ALSO`.
3. **The Good Docs Project templates.** Use the community-maintained per-doc-type Markdown templates.
4. **Single-doc-per-topic runbook structure.** Use one Markdown file per topic, internally structured along Google SRE / Atlassian / PagerDuty runbook conventions (`Purpose / Prerequisites / Procedure / Verification / Rollback / Troubleshooting`).
5. **Diátaxis.** Organize all documentation into four quadrants (tutorials, how-to guides, reference, explanation) with each document classified into exactly one quadrant.
6. **Custom in-house framework.** Define a bespoke documentation taxonomy specific to this portfolio.

## Decision Outcome

Chosen option: **Option 5, Diátaxis.**

In a repository that adopts this baseline, all non-ADR documentation lives under `docs/` with subdirectories named exactly `tutorials/`, `how-to/`, `reference/`, and `explanation/`. Every Markdown file under those four subdirectories (other than an index `README.md`) lives in exactly one of them and is authored to one Diátaxis purpose. ADRs live in their own sibling subtree at `docs/decision-records/{org,template,repo}/` as established by ADR-0001 and are not subject to the Diátaxis quadrant rule.

A repository is not required to populate every quadrant. A repository that has no learning-oriented onboarding need not create `docs/tutorials/`. A repository may begin by populating only the quadrants that solve current pain (commonly `docs/reference/` and `docs/how-to/`) and grow into the others over time. A repository's `docs/README.md` MAY serve as the index across populated quadrants and SHOULD label each linked document with its quadrant.

Composite operational documents — runbooks, troubleshooting guides, and other artifacts that combine reference, procedural, and explanatory content by necessity — are treated as belonging to the **how-to** quadrant when their primary purpose is to walk an operator through a goal-directed task, and to the **reference** quadrant when their primary purpose is lookup. Composite documents MUST use explicit second-level section headings labelled with the quadrant they touch (`## Reference`, `## How to ...`, `## Why ...`) so readers can predict where the lookup material ends and the procedural material begins. Composite documents are an explicit accommodation of operational reality and are not an exception that is allowed to expand silently into general non-operational docs.

The directory name `docs/` is preferred over alternatives such as `documentation/` or `book/` for terseness and broad community familiarity. The subdirectory names match Diátaxis terminology exactly: `tutorials`, `how-to`, `reference`, `explanation`. Plural for `tutorials` matches Diátaxis usage. Hyphenated `how-to` matches Diátaxis usage and avoids an awkward `how_to` or `howto`. The plural `references` is explicitly avoided because Diátaxis uses the mass noun `reference`.

## Pros and Cons of the Options

### Option 1: No formal documentation framework

- **Good, because** it has zero authoring overhead at the framework level.
- **Good, because** it imposes no structure on contributors who already know what they want to write.
- **Bad, because** it allows reference, procedural, and conceptual material to accumulate in the same files, where one type silently invalidates the others.
- **Bad, because** readers cannot predict the location of new information without reading the whole repository.
- **Bad, because** every contributor reinvents the wheel; the result reads as a collage rather than a documentation set.

### Option 2: POSIX `man(7)` format

- **Good, because** the format is one of the most stable in software history, with effectively 100% adoption in Unix-derived CLI tooling for over fifty years.
- **Good, because** the structure is well-defined and predictable: `NAME / SYNOPSIS / DESCRIPTION / OPTIONS / EXAMPLES / SEE ALSO`.
- **Bad, because** the format is designed for CLI program reference, not for operational documentation, conceptual explainers, onboarding tutorials, or repository-level governance docs.
- **Bad, because** it has no equivalent of how-to guides, tutorials, or explanation, so it would force every non-reference document into an awkward shape.
- **Bad, because** community familiarity outside CLI tooling is limited; readers expect this format only for executable manuals.

### Option 3: The Good Docs Project templates

- **Good, because** it provides explicit Markdown templates for several distinct document types.
- **Good, because** templates lower the barrier to authoring, especially for non-writers.
- **Bad, because** the project's flagship templates repository on GitHub was archived on 2022-09-24, and active development has migrated to a less-discoverable GitLab home; the public signal of momentum has weakened.
- **Bad, because** the project has no publicly named enterprise adopters of comparable visibility to the framework chosen below.
- **Bad, because** it is a templates-bundle rather than a documentation philosophy; it tells contributors what template to use but not why a particular reader needs a particular type of document.

### Option 4: Single-doc-per-topic runbook structure

- **Good, because** it is the most accessible structure when the constraint is "one URL per topic for a hurried operator."
- **Good, because** it matches the mental model of operations and SRE teams, who already think in runbooks.
- **Good, because** it accommodates reference, procedure, and troubleshooting in a single file, which simplifies cross-linking.
- **Neutral, because** it is a structure pattern rather than a documentation framework; it does not categorize non-operational documentation at all.
- **Bad, because** it encourages exactly the drift problem this ADR is trying to prevent: reference, how-to, and explanation accumulate in one file with no enforced separation.
- **Bad, because** it has no taxonomy for tutorials, conceptual explainers, or repository-level governance, so non-operational docs end up unfiled.
- **Bad, because** there is no canonical runbook standard; choosing this option requires also choosing one of several competing runbook templates and maintaining it as a local convention.

### Option 5: Diátaxis (chosen)

- **Good, because** it is the most-adopted explicit documentation methodology in modern software-engineering practice, with public adopters including Canonical, Cloudflare, Gatsby, LangChain, Vonage, Sequin, and StreamingFast, and an active framework repository at over a thousand stars.
- **Good, because** it is reader-first: it organizes documentation by what the reader is trying to do, not by what topic it is about.
- **Good, because** the four quadrants are mutually exclusive and collectively exhaustive in everyday practice; an authoring contributor knows in seconds which quadrant their document belongs in.
- **Good, because** it is a *philosophy* not just a *template bundle*; it explains why a particular reader needs a particular type of document, which is more durable than any single template.
- **Good, because** it accommodates ADR-0001 cleanly: ADRs are a specialized governance artifact, not a Diátaxis category, and live in their own directory governed by their own ADR.
- **Good, because** repositories may adopt it incrementally, populating only the quadrants they currently need.
- **Neutral, because** composite operational documents (runbooks, troubleshooting guides) span quadrant lines and require explicit accommodation; this ADR provides that accommodation in the Decision Outcome.
- **Bad, because** topics that today live in a single file may need to be split across two or more files when adopted, creating short-term re-shelving cost.
- **Bad, because** it requires authors to classify each new document, which is a small but nonzero per-doc decision.

### Option 6: Custom in-house framework

- **Good, because** it could be tailored to this portfolio's exact needs.
- **Bad, because** the maintenance and onboarding cost of a bespoke framework is unjustified when an actively maintained external framework already covers the same ground.
- **Bad, because** it provides no signal of community recognition to external readers, contributors, or hiring audiences.
- **Bad, because** it directly contradicts ADR-0001's preference for established community standards over local invention.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) conventions.

1. **Layout check.** A repository that adopts this baseline MUST place all non-ADR documentation under `docs/`. Where any quadrant is populated, it MUST be in a top-level subdirectory named exactly `tutorials`, `how-to`, `reference`, or `explanation`. A CI script or `pre-commit` hook MAY fail a pull request that adds a Markdown file under `docs/` outside one of the four quadrant subdirectories.
2. **Layout-skeleton check.** Every adopting repository MUST contain all four quadrant directories — `docs/tutorials/`, `docs/how-to/`, `docs/reference/`, `docs/explanation/` — even when some are empty. Empty quadrants are kept in source control via byte-identical `.gitkeep` placeholders mirrored from the org canonical, so a reader scanning any repo immediately sees the same predictable layout. *Content* in each quadrant remains opt-in (a repo with no learning-oriented onboarding has an empty `tutorials/`); only the *layout* is mandatory.
3. **Quadrant-purity check.** Each non-composite document under `docs/` SHOULD address exactly one Diátaxis quadrant. Composite operational documents (runbooks, troubleshooting guides) MAY span quadrants but MUST mark each section with its quadrant via an explicit second-level heading (`## Reference`, `## How to ...`, `## Why ...`).
4. **Index check.** A repository's `docs/README.md`, if present, SHOULD link to every populated quadrant and SHOULD label each linked document with the quadrant it belongs to. A CI script MAY diff the directory listing against the index and fail on drift.
5. **Co-existence check.** ADRs live at `docs/decision-records/{org,template,repo}/` (a sibling subtree, not a Diátaxis quadrant) and are not subject to the quadrant rule. A pull request that misfiles an ADR under one of the four quadrant directories SHOULD be rejected with a pointer to ADR-0001.
6. **Editorial rule.** After acceptance of this ADR, document re-shelving (moving an existing doc into the appropriate quadrant) is editorial, not architectural; it does not require its own ADR. A material *change* to the framework choice — adopting a different framework, abandoning Diátaxis, or extending the quadrant taxonomy — does require a superseding ADR.

Enforcement tooling is recommended but not mandatory at acceptance time. A solo-maintainer repository MAY rely on manual discipline; a team repository SHOULD automate at least the layout and index checks.

## Consequences

### Positive

- New documentation has a predictable home from the moment it is written.
- Readers can navigate any adopting repository's `docs/` tree using the same mental model.
- Authoring decisions reduce to a one-step quadrant classification rather than open-ended structural design.
- Drift between reference, procedural, and conceptual material becomes harder, because each document has a single declared purpose.
- The choice carries community recognition: external readers, contributors, and hiring audiences encounter a framework they likely already know.

### Negative

- Existing monolithic documents (in particular `DESIGN.md` in `github-terraform-framework`, and any plan documents in other repositories) do not yet conform to Diátaxis. Re-shelving them is a non-trivial editorial pass that is deferred to per-repository follow-on work.
- Some topics that today live in a single file will need to be split across two or more files; readers who already know the old single-file layout will have a one-time re-orientation cost.
- Authors must perform a small classification step per document.

### Neutral

- The four Diátaxis quadrant names are now reserved at `docs/{tutorials,how-to,reference,explanation}/` in adopting repositories. Future ADRs that need additional top-level directories under `docs/` should reference this ADR explicitly.
- Composite operational documents are an explicit accommodation rather than a violation; their boundaries are codified in the Decision Outcome and Confirmation sections above.
- ADRs continue to be governed by ADR-0001 and are unaffected by this decision other than by cross-reference.

## Assumptions

This decision rests on the following assumptions. If any becomes false, this ADR should be revisited:

1. The Diátaxis framework remains actively maintained and documented at [diataxis.fr](https://diataxis.fr) or an equivalent successor URL.
2. The four-quadrant taxonomy continues to map cleanly to the documentation needs that arise in this portfolio. If a sustained category of need cannot be classified into one of the four quadrants, that pattern is itself evidence to reconsider.
3. Markdown remains the primary documentation format in adopting repositories.
4. Repositories prefer source-controlled documentation that travels with the code over externally hosted knowledge bases.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

This section lists downstream pull requests that implement or operationalize the decision described in this ADR. It does not need to list the pull request that introduced the ADR itself.

Pending. The first expected implementer is `github-terraform-framework`, which will adopt the Diátaxis layout for its initial PAT and AWS IAM documentation set, with `DESIGN.md` deferred for separate refactor.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) — establishes the ADR convention itself. ADR-0001 governs `docs/decision-records/{org,template,repo}/`; this ADR governs the rest of `docs/` (everywhere else).

## Compliance Notes

This ADR establishes a documentation organization convention, not a deployed security control. The table below indicates where evidence produced under this convention may help during reviews; it is illustrative rather than exhaustive, and is not a claim that a repository is compliant merely because Diátaxis is adopted.

| Framework              | Control / Practice ID                                          | Potential Evidence Contribution                                                                                                          |
| ---------------------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| NIST SP 800-53 Rev. 5  | SA-5 (System Documentation)                                    | A consistently structured `docs/` tree supports the system-documentation requirement by making operational, reference, and conceptual material findable. |
| NIST SP 800-53 Rev. 5  | AT-2 (Literacy Training and Awareness)                         | `docs/tutorials/` and `docs/how-to/` material supports onboarding and operational literacy.                                              |
| NIST SP 800-218 (SSDF) | PO.3.2 (Document the security policies of the SDLC)            | A standardized `docs/` location for security-relevant procedural and reference material reduces the assembly cost of evidence packages. |
| ISO/IEC 27001:2022     | A.5.37 (Documented operating procedures)                       | `docs/how-to/` and operational composite documents under `docs/reference/` provide a predictable location for documented procedures.    |

Subsequent repository-level ADRs that scope this convention to specific compliance contexts should keep only the rows that genuinely apply to their decision.
