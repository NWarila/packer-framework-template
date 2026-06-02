# ADR-0004: Use Renovate for Dependency Updates with Per-Template Baselines

| Field            | Value                                                                    |
| ---------------- | ------------------------------------------------------------------------ |
| ID               | ADR-0004                                                                 |
| Scope            | Org baseline                                                             |
| Status           | Accepted                                                                 |
| Decision-subject | Dependency-update tooling and Renovate baseline inheritance for `NWarila`. |
| Date accepted    | 2026-05-05                                                               |
| Date             | 2026-06-02                                                               |
| Last reviewed    | 2026-06-02                                                               |
| Authors          | Nick Warila (@NWarila)                                                   |
| Decision-makers  | Nick Warila (sole portfolio maintainer)                                  |
| Consulted        | Renovate preset documentation and current template/consumer configs.     |
| Informed         | Maintainers of adopting repositories under `NWarila`.                    |
| Reversibility    | Medium                                                                   |
| Review-by        | 2026-11-29                                                               |

## TL;DR

All `NWarila/*` repositories track dependency updates via [Renovate](https://docs.renovatebot.com/). Each **type-template** in the portfolio (e.g. `NWarila/terraform-runner-template`, `NWarila/terraform-framework-template`, `NWarila/packer-framework-template`, `NWarila/packer-runner-template`, `NWarila/ansible-framework-template`, `NWarila/python-template`) owns a complete, self-contained `.github/renovate.json5` that is the canonical Renovate baseline for every consumer of that template. Consumers' local `.github/renovate.json5` extends only their type-template's explicit preset file (e.g. `extends: ["github>NWarila/terraform-runner-template//.github/renovate.json5"]`) and adds only the overrides genuinely specific to that consumer. The explicit path is required because Renovate resolves bare `github>owner/repo` presets to `default.json`, while these type-template baselines intentionally live at `.github/renovate.json5` so the template repository itself uses the same file Renovate evaluates. There is **no** org-level _shared_ `renovate.json5` for consumers to extend — consumers extend their type-template's baseline, never the org repo. `NWarila/.github` does carry its own `.github/renovate.json5`, but it governs only that repo's own dependencies (the `github-actions` pins in its reusable workflows) and is not a baseline any consumer extends. Renovate replaces Dependabot at the org level because Dependabot does not update Terraform's `required_version` field and has incomplete coverage of pinned tool versions in adjacent tooling. The per-template-baseline pattern keeps each stack's Renovate policy self-contained, lets stacks evolve their settings independently, and aligns with the three-tier ADR model from [ADR-0001](0001-use-architecture-decision-records.md): stack-level concerns live at the template tier, not the org tier.

## Context and Problem Statement

Repositories under the `NWarila` namespace track several version-pin surfaces that need automated updates:

- **GitHub Actions** referenced by full commit SHA in workflow files, per the org's SHA-pin policy.
- **Terraform** version constraints — `required_version` on the `terraform` block, and provider versions in `required_providers`.
- **Tool versions** in adjacent tooling such as `.tool-versions` (asdf), devcontainer feature inputs, the `terraform_version:` literal in `hashicorp/setup-terraform` workflow steps, Dockerfile `FROM` lines, and pre-commit `rev:` references.
- **Other ecosystems** as repos add language-specific tooling (npm, pip, etc.).

Dependabot supports the GitHub Actions case well. It does **not** support Terraform's `required_version` field — Dependabot's Terraform updater scans `required_providers` but ignores the constraint on Terraform itself. Dependabot also has limited and inconsistent handling of pinned tool versions in adjacent tooling. As repositories grow to include any of those, Dependabot leaves silent drift. Adopting Dependabot for every new repository accepts that gap by default, which is misaligned with the org's secure-by-default posture.

Renovate offers native managers for every one of those surfaces (`terraform`, `terraform-version`, `github-actions`, `pre-commit`, `asdf`, `dockerfile`, `devcontainer`, `npm`, `pip`, etc.) plus a `regex` manager for arbitrary version literals. It also rewrites the trailing tag comment on SHA-pinned Actions bumps (`# v6` → `# v6.1.0`), preserving the human-readability convention enforced in the org's Actions SHA-pin policy.

A second concern beyond manager coverage is configuration drift. If every repository hand-rolls its Renovate config, settings diverge across repos and stacks lose uniform behavior. Renovate's `extends` mechanism solves this: a single source of truth at the type-template tier is inherited by every consumer of that template, with per-repo overrides limited to repo-specific concerns. Different stacks (Terraform, Packer, Python, etc.) have legitimately different Renovate needs — `terraform.rangeStrategy`, `pip` constraints, `dockerfile` rebases — so each type-template owns the settings appropriate to its stack and stays out of the others' way.

The previous per-repo `.github/dependabot.yml` files covered only `github-actions`, at varying schedules. That coverage no longer matches the org's actual update surface, and the cadence drift produces avoidable PR churn.

## Decision Drivers

The following forces shaped this decision:

1. **Coverage of Terraform `required_version` and adjacent tooling.** Dependabot does not handle these; Renovate does. As repositories grow to pin Terraform CLI versions and other tool versions in adjacent tooling, the gap widens.
2. **SHA-pin retention on GitHub Actions.** The org's SHA-pin policy requires every `uses:` entry to be a 40-character commit SHA with a tag comment. The dependency-update tool must preserve this format on every bump.
3. **Conventional Commit emission.** Update PRs should emit Conventional Commit prefixes that release-please (where configured) categorises.
4. **Cross-repo consistency.** Common settings must be uniform across repos. Per-repo configs that drift are a maintenance liability.
5. **DRY within a stack (Inheritance over duplication).** Hand-copying the same Terraform settings into every Terraform consumer is error-prone. A type-template baseline that every consumer of that template inherits reduces maintenance to one place per stack. This aligns with the "Inheritance over duplication" principle in [ADR-0001](0001-use-architecture-decision-records.md).
6. **Stack independence.** Different stacks have legitimately different Renovate needs. A Terraform-specific change should not require touching the Packer template or vice versa. The configuration model must let stacks evolve independently.
7. **Reasonable PR cadence.** Daily PR creation produces noise; weekly cadence aligns with most repository review windows.

## Considered Options

1. **Stay on Dependabot org-wide.** Continue with per-repo `.github/dependabot.yml`, accepting the `required_version` gap and per-repo cadence drift.
2. **Adopt Renovate per-repo with no shared baseline at all.** Each repo maintains its own `.github/renovate.json5` from scratch.
3. **Adopt Renovate with a single shared org baseline.** All settings live in `NWarila/.github/.github/renovate.json5`; every consuming repo extends it directly.
4. **Adopt Renovate with self-contained type-template baselines.** Each type-template (Terraform, Packer, Python, etc.) owns a complete `renovate.json5`. Consumers extend their type-template only. No org-level Renovate config.
5. **Adopt Renovate with an org→template→consumer extends chain.** Truly universal settings at the org tier; stack-specific at the template tier; consumer-specific at the repo tier; consumers extend the template, which transitively extends the org.
6. **Mix Dependabot for legacy repos and Renovate for new repos.** Run both tools depending on repo age.
7. **Hand-roll a scheduled GitHub Actions workflow that opens update PRs.** Custom maintenance pipeline.

## Decision Outcome

Chosen option: **Option 4, Renovate with self-contained type-template baselines.**

Each **type-template** in the portfolio owns a complete, self-contained `.github/renovate.json5` that is the single source of truth for its stack. Consumers of that template extend only the template; there is no org-level `renovate.json5` and consumers do not extend more than one config.

The Terraform-runner template's baseline (`NWarila/terraform-runner-template/.github/renovate.json5`) is the canonical pattern. Other type-templates (`NWarila/terraform-framework-template`, `NWarila/packer-framework-template`, `NWarila/packer-runner-template`, `NWarila/ansible-framework-template`, `NWarila/python-template`, etc.) carry their own baselines tailored to their stack as they are brought online.

Each type-template baseline configures, at minimum:

- `extends: ["config:recommended"]` as the inherited Renovate baseline.
- `schedule: ["before 6am on monday"]` (weekly), the portfolio cadence.
- `semanticCommits: "enabled"` so PRs use Conventional Commit prefixes.
- `:dependencyDashboard` so each consumer gets a single tracking issue rather than a flood of standalone PRs.
- `prConcurrentLimit: 5` to cap noise during update bursts.
- A `packageRules` entry that maps `github-actions` updates to `ci(deps): ...` Conventional Commit prefixes with `pinDigests: true` to preserve SHA-pin format.
- Stack-specific settings — for Terraform: `terraform.rangeStrategy: "pin"` per [ADR-0005](0005-pin-terraform-and-provider-versions-exactly.md); `enabledManagers: ["github-actions", "terraform", "pip_requirements", "custom.regex"]`; the `customManagers` regex for `# renovate:` annotations in workflow comments.

Each adopting consumer carries a minimal `.github/renovate.json5` that:

- Inherits the template baseline via `extends: ["github>NWarila/<type-template>//.github/renovate.json5"]`.
- Adds only the overrides that are genuinely repo-specific (e.g. a single repo's release schedule, a single repo's automerge policy). Stack-wide overrides MUST be made in the type-template, not duplicated in every consumer.

The `.github/dependabot.yml` file MUST NOT exist in any adopting repository. Repositories that previously contained one MUST remove it as part of their Renovate migration PR.

Renovate enablement requires the Renovate GitHub App to be installed against each repository or against the entire org. Installation is a one-time operation outside the repo's git history and is the maintainer's responsibility.

`NWarila/.github` carries a `.github/renovate.json5` that governs **only its own** dependencies — the `github-actions` pins in its reusable workflows — so the org repo's own supply chain stays current. This is **not** an org-level baseline: no consumer extends it, and there remains no _shared_ org Renovate config. The org tier holds ADRs and policies that apply to every repo regardless of stack; a truly universal Renovate setting (if one ever genuinely arose that applied to Terraform AND Packer AND Python AND PowerShell consumers identically) would still be added to each type-template independently rather than centralised.

## Pros and Cons of the Options

### Option 1: Stay on Dependabot org-wide

- **Good, because** Dependabot is GitHub-native; no third-party app installation required.
- **Good, because** existing single-ecosystem configurations are already working for GitHub Actions in the repos that have them.
- **Bad, because** Dependabot cannot update Terraform's `required_version` field. Repositories with pinned Terraform versions accumulate untracked drift.
- **Bad, because** Dependabot's coverage of pinned tool versions in adjacent tooling is incomplete and inconsistent.
- **Bad, because** Dependabot's per-repo configuration provides no shared baseline; common settings drift across repos.

### Option 2: Adopt Renovate per-repo with no shared baseline at all

- **Good, because** every repo's behavior is fully self-contained and visible in one file.
- **Good, because** there is no implicit dependency on an external config repo at evaluation time.
- **Bad, because** common settings (schedule, semantic-commit prefixes, SHA-pin retention) drift across repos as new repos are bootstrapped from older templates.
- **Bad, because** changing a stack-wide setting (e.g., shifting the cadence from weekly to bi-weekly) requires a coordinated PR across every repo.
- **Bad, because** it duplicates ~80 lines of identical config into every repository, contradicting the org's "Inheritance over duplication" principle.

### Option 3: Adopt Renovate with a single shared org baseline

- **Good, because** truly universal settings live in exactly one place.
- **Good, because** changing such a setting takes one PR.
- **Bad, because** different stacks have legitimately different needs (`terraform.rangeStrategy`, `pip` constraints, `dockerfile` rebases). An org-level baseline either serves the lowest common denominator or ends up encoding stack-specific defaults that are wrong for some stacks.
- **Bad, because** an outage or breaking change in the shared baseline propagates to every consuming repo at once, regardless of stack. A Terraform-specific tweak should not be able to break Packer consumers.
- **Bad, because** it conflicts with the three-tier ADR model (org / template / repo): stack-specific concerns live at the template tier, and Renovate config carries the same character.

### Option 4: Adopt Renovate with self-contained type-template baselines (chosen)

- **Good, because** Renovate covers every update surface the org has now or is likely to grow into.
- **Good, because** `pinDigests: true` (set per-template for github-actions) preserves SHA-pin format on Action bumps and rewrites trailing tag comments in place.
- **Good, because** `semanticCommits` emits Conventional Commit prefixes that release-please categorises without per-PR rewriting.
- **Good, because** each type-template's baseline is self-contained and stack-appropriate. A Terraform-specific tweak only affects Terraform consumers; a Packer-specific tweak only affects Packer consumers.
- **Good, because** consumers remain free to override repo-specific concerns without re-declaring the entire config.
- **Good, because** the dependency-dashboard issue surfaces pending updates without flooding the PR list.
- **Good, because** the configuration model directly mirrors the three-tier ADR model: stack-level concerns live at the template tier where they belong.
- **Neutral, because** Renovate requires the GitHub App to be installed once per repository (or once per org).
- **Neutral, because** truly universal settings (cadence, dependency-dashboard, prConcurrentLimit) end up duplicated across each type-template's baseline. In practice these settings rarely change and the duplication is small (~10 lines per template); the trade-off is worth the stack independence.
- **Bad, because** the Renovate GitHub App is a third-party dependency in the supply chain (managed by Mend); operational burden of compromise is real.
- **Bad, because** the dependency-dashboard issue is opinionated; if not curated it can clutter the issue tracker.

### Option 5: Org→template→consumer extends chain

- **Good, because** truly universal settings live at the org tier and stack-specific at the template tier, eliminating the Option 4 duplication.
- **Good, because** the inheritance chain matches Renovate's idiomatic pattern (`extends` is transitive).
- **Bad, because** it adds a third config file to reason about per consumer (org + template + consumer's own).
- **Bad, because** an org-level Renovate config blurs the line between "org tier = universal policy" and "stack-specific config", which the three-tier ADR model carefully separates. ADRs at the org tier apply to every repo regardless of stack; Renovate config historically does not.
- **Bad, because** propagation behavior across two levels of inheritance is harder to debug when a single consumer behaves unexpectedly.
- **Bad, because** the duplication-cost in Option 4 is a small one (~10 lines per template) and Option 5's reduction is not worth the additional architectural surface area.

### Option 6: Mix Dependabot and Renovate

- **Good, because** legacy repos avoid the migration cost.
- **Bad, because** the org loses uniform dependency-update behavior. New contributors must learn which repo uses which tool.
- **Bad, because** the `required_version` coverage gap remains for any repo still on Dependabot, partially defeating the value of switching at all.
- **Bad, because** mixed-tool environments accumulate inconsistencies (different cadences, different commit-message formats) that erode the value of having either tool.

### Option 7: Hand-roll a scheduled GitHub Actions workflow

- **Good, because** it provides full control over update logic, schedule, and PR template.
- **Bad, because** it imposes disproportionate maintenance burden for a personal-account org.
- **Bad, because** features like release-notes fetching, semver diffing, and dependency-graph awareness would all be reinvented.
- **Bad, because** a hand-rolled workflow is a single point of failure with no community support.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) conventions.

1. **Tool-presence check.** Every adopting repository MUST contain `.github/renovate.json5`. A `.github/dependabot.yml` file MUST NOT exist; a CI script or `pre-commit` hook MAY assert its absence.
2. **Inheritance check.** Every adopting consumer's `.github/renovate.json5` MUST include exactly one `github>NWarila/<type-template>//.github/renovate.json5` entry in its `extends` array, identifying the type-template the consumer derives from and the exact preset file Renovate should load. Bare `github>NWarila/<type-template>` preset references are not compliant unless the template deliberately publishes a `default.json` preset; the current type-template baselines do not. A consumer that does not derive from a type-template (e.g. the type-template repos themselves, or a one-off repo with no template lineage) MUST document its exception in a repo-specific superseding ADR.
3. **SHA-pin retention check.** Every type-template's `.github/renovate.json5` MUST configure `pinDigests: true` for the `github-actions` manager (typically via a `packageRules` entry). A reviewer SHOULD reject a PR to a type-template baseline that removes or disables this setting without a superseding ADR.
4. **Schedule check.** Every type-template's `.github/renovate.json5` MUST schedule weekly or less-frequent runs. Daily or more-frequent schedules would produce avoidable PR churn across every consumer of that template.
5. **Override discipline.** Repository-local overrides MUST be limited to repo-specific concerns. Settings that should apply to every consumer of a particular type-template MUST be added to that type-template's `renovate.json5` rather than copy-pasted into every consumer. There is no org-level Renovate baseline; settings that would otherwise be "truly universal" are duplicated across each type-template independently to preserve stack independence (see Option 4 §"Neutral").
6. **No org-level Renovate baseline.** `NWarila/.github/.github/renovate.json5` MUST NOT be referenced via `extends` by any consumer; there MUST be no _shared_ org-level Renovate baseline that consumers extend. The org repo's own `.github/renovate.json5` is permitted and governs **only** that repo's own dependencies (the `github-actions` pins in its reusable workflows); it is not a baseline any consumer extends. A maintainer who is tempted to centralise a setting "because it applies to every template" SHOULD instead add it to each template's baseline; the duplication cost is small and the stack independence is worth more.
7. **Editorial rule.** A change of dependency-update tool (back to Dependabot, or to a third option) is itself an architectural decision and MUST be recorded as a superseding ADR. Adoption or removal of a type-template's Renovate baseline is a template-tier decision and MUST be recorded as an ADR in that type-template's own `docs/decision-records/template/` directory.
8. **Minimum-release-age + strict-timestamp check.** Every type-template's `.github/renovate.json5` MUST set `minimumReleaseAge: "7 days"` and `internalChecksFilter: "strict"`. The 7-day quarantine window blocks the common compromised-package pattern where a malicious release is published and then yanked within hours or days; consumers that only consider releases at least seven days old never observe the yanked window. The `"strict"` filter mode is required because Renovate's default behavior (`"none"`) silently allows updates whose timestamps it cannot resolve, which would defeat the quarantine for any datasource that omits timestamp metadata. Strict mode treats unresolvable timestamps as failing the age check, which is the conservative choice for a supply-chain control. A template-tier baseline that omits either setting, or sets `minimumReleaseAge` below seven days, requires a superseding ADR documenting the relaxation and its rationale. A CVE-driven immediate-bump carve-out via `vulnerabilityAlerts.minimumReleaseAge: "0 days"` is permitted at the type-template tier provided the carve-out is recorded as a separate Confirmation item or a follow-up ADR in that template's `docs/decision-records/template/`.

Enforcement tooling is recommended but not mandatory at acceptance time. A repository MAY add CI scripts that verify (1)–(3); template adoption MAY be tracked via the drift-gate workflow that mirrors ADRs from the appropriate sources.

## Consequences

### Positive

- Terraform `required_version` updates are tracked automatically across the org; the Dependabot-shaped gap is closed.
- Action SHAs stay current with their tag comments rewritten in place across every repo, preserving the SHA-pin convention without manual intervention.
- Conventional Commit prefixes flow into release-please without per-PR rewriting.
- Each stack's settings live in exactly one place — its type-template — and cannot affect other stacks. Changing Terraform-specific behavior takes one PR to `NWarila/terraform-runner-template` and reaches every Terraform consumer; Packer and Python are untouched.
- New consumers of a template bootstrap with a ~6-line `renovate.json5` that inherits the template behavior automatically.
- Future managers (pre-commit, devcontainer features, mkdocs Python deps, Docker base images) can be enabled by editing the relevant type-template's baseline rather than every consuming repo.

### Negative

- One additional GitHub App must be installed against the org (or per-repo).
- Renovate's dependency-dashboard issue is opinionated and clutters the issue tracker if not curated.
- Each type-template's baseline is now a load-bearing artifact for its stack: an outage or breaking change in `NWarila/<type-template>/.github/renovate.json5` propagates to every consumer of that template on the next Renovate run. Mitigation: type-template baselines are reviewed in PR like any other template-tier change.
- Truly universal settings (cadence, prConcurrentLimit, semantic-commits, dependency-dashboard) end up duplicated across each type-template's baseline. In practice these settings rarely change; the duplication is small and the stack independence is worth more.
- Release-notes fetching adds latency to PR creation (negligible in practice).

### Neutral

- The `github>` extends syntax creates a runtime dependency on `NWarila/<type-template>` being reachable when Renovate evaluates a consuming repo. In practice this is reliable; if it becomes unreliable, consumers MAY temporarily inline the template baseline.
- This ADR scopes the decision to the `NWarila` organization. The functionally-identical `nwarila-platform` organization carries its own ADR-0004 documenting the same per-template-baseline pattern with `nwarila-platform/*` scoping; the two ADRs are maintained in parallel per the portfolio's org-separation practice. Cross-org consumers (e.g., an `nwarila-platform/*` runner consuming `NWarila/terraform-runner-template` via `extends: ["github>NWarila/terraform-runner-template//.github/renovate.json5"]`) inherit the type-template's behavior regardless of which org's `.github` is read for community-health policy.
- Repo-specific overrides remain permitted; this ADR is not a uniformity-at-all-costs mandate. The only constraint is that overrides MUST be repo-specific concerns. Stack-wide concerns belong in the type-template tier per ADR-0001.

## Assumptions

This decision rests on the following assumptions. If any becomes false, this ADR should be revisited:

1. The Renovate GitHub App remains free for personal-account organizations and continues to be actively maintained.
2. Renovate continues to support GitHub-hosted presets with explicit file paths, including `.json5` preset files.
3. The Renovate config schema remains compatible with the configuration shape used here.
4. The org continues to use Conventional Commits + release-please for repos that publish releases. A switch to a different release tool would require adjusting `semanticCommitType` overrides in the shared baseline.

## Supersedes

None — `.github/dependabot.yml` files in `NWarila/*` repos were single-ecosystem configurations with no prior ADR documenting their adoption. This ADR replaces that pattern as a new decision rather than as a formal supersession.

## Superseded by

None (current).

## Implementing PRs

Pending. Each type-template's `.github/renovate.json5` is the source of truth for its stack and is a precondition rather than an "implementing PR" of this ADR (the Terraform-runner template's baseline already exists; other type-templates' baselines will be authored or reviewed as those templates come online). Consumer migration PRs that switch from a copy-pasted Renovate config to a thin `extends: ["github>NWarila/<type-template>//.github/renovate.json5"]` will be listed here.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) — establishes the format and three-tier scope structure of decision records. The per-template-baseline pattern in this ADR mirrors that three-tier model: stack-level concerns live at the template tier.
- [ADR-0003](0003-use-deny-all-gitignore-strategy.md) — establishes the deny-all `.gitignore` strategy. Renovate config files are explicitly allowlisted in adopting repositories per ADR-0003.
- [ADR-0005](0005-pin-terraform-and-provider-versions-exactly.md) — pins Terraform and provider versions exactly across the org. Each Terraform-shape type-template's `renovate.json5` sets `terraform.rangeStrategy: "pin"` per that ADR. Per-template baselines mean each stack records its own analogous decisions in its own ADRs where applicable.

## Compliance Notes

This ADR preserves the SHA-pin policy (encoded in each type-template's baseline as `github-actions.pinDigests: true`). It does not modify branch-protection or PR-review requirements: every Renovate PR is subject to the same `main`-branch protections as a human-authored PR, including required status checks. Future ADRs that adopt additional managers (e.g., `pre-commit`, `pip`, `docker`) inherit this ADR's defaults and need only document scope-specific divergence in repo-local config.

| Framework              | Control / Practice ID                                                | Potential Evidence Contribution                                                                                                |
| ---------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| NIST SP 800-53 Rev. 5  | SI-2 (Flaw Remediation)                                              | Renovate's automated update PRs contribute to the timely application of patches and security fixes across the org.            |
| NIST SP 800-53 Rev. 5  | CM-3 (Configuration Change Control)                                  | The per-template-baseline pattern records stack-wide dependency-management policy in source control with PR review history.    |
| NIST SP 800-218 (SSDF) | PW.4 (Reuse Existing, Well-Secured Software When Feasible)           | Tracking dependency updates with SHA-pin retention preserves the supply-chain integrity posture for reused software.           |

## Changelog

| Date       | Change                                    | Reason                                      | Author/Role                       | Body-diff? |
| ---------- | ----------------------------------------- | ------------------------------------------- | --------------------------------- | ---------- |
| 2026-06-02 | Refreshed living metadata and clarified explicit Renovate preset-path compliance. | Re-review against current Renovate preset documentation and live template/consumer configs. | Portfolio maintainer / governance | Yes        |
