# ADR-0005: Pin Terraform and Provider Versions Exactly

| Field          | Value                                    |
| -------------- | ---------------------------------------- |
| Status         | Accepted                                 |
| Date           | 2026-05-05                               |
| Authors        | Nick Warila (@NWarila)                   |
| Decision-maker | Nick Warila (sole portfolio maintainer)  |
| Consulted      | None.                                    |
| Informed       | None.                                    |
| Reversibility  | Medium                                   |
| Review-by      | N/A (Accepted)                           |

## TL;DR

Every repository under `NWarila` that contains Terraform configuration pins both the Terraform CLI version (via `terraform { required_version = "= X.Y.Z" }`) and every provider version in `required_providers` to an exact version using the `=` operator. Range constraints (`>=`, `~>`, etc.) are not used. Renovate keeps these exact pins current via `rangeStrategy: "pin"` configured in each Terraform-shape type-template baseline. Consumers of repos that publish Terraform modules MUST run the exact pinned Terraform CLI version; consumers running anything else hit `terraform init` failure immediately rather than discovering compatibility issues partway through `apply`.

## Context and Problem Statement

Terraform's `required_version` constraint on the `terraform { }` block is enforced by the CLI: every consumer of a configuration (root or child module) must satisfy the constraint, or `terraform init` aborts. The constraint uses the [HashiCorp version-constraint syntax](https://developer.hashicorp.com/terraform/language/expressions/version-constraints) and supports several operators:

- `= X.Y.Z` — exact pin; only this version satisfies the constraint
- `>= X.Y` — minimum; any newer version satisfies
- `~> X.Y` — pessimistic; permits patch updates within X.Y
- Combinations like `>= 1.9, < 2.0` for explicit ranges

The same operators apply to provider version constraints in `required_providers`.

Two camps exist in the wider Terraform community:

1. **Range constraints** (`>=`, `~>`). The argument is multi-module satisfiability: if a root module pulls in three child modules from independent authors, range constraints let all three coexist as long as one CLI version satisfies their union. This matters when consuming modules from authors you do not control.

2. **Exact pins** (`=`). The argument is reproducibility and security: every consumer runs the exact CLI version the author tested with; behavior is deterministic; supply-chain integrity is stronger.

The `NWarila` portfolio sits squarely in the second context. Modules in this org are consumed almost exclusively by other repositories in the same org. The maintainer controls every published module and every consumer. Multi-module satisfiability across third-party authors is not a real concern here. What matters is:

- Reproducibility: every consumer runs the exact Terraform CLI version we tested with
- Security: known-good versions; no surprise behavior changes from a consumer using a newer CLI
- Supply-chain consistency: the SHA-pin policy on GitHub Actions extends naturally to exact-pinning Terraform versions
- Predictable failure modes: `terraform init` fails fast on version mismatch, not partway through `apply`

The previous default ([ADR-0004](0004-use-renovate-for-dependency-updates.md) §Decision Outcome) suggested `rangeStrategy: "bump"` for child modules and `"pin"` for root modules. That distinction is suitable for the wider community but is unnecessarily permissive for this org's consumption model.

## Decision Drivers

The following forces shaped this decision:

1. **Reproducibility.** Every consumer should run the exact Terraform CLI and provider versions the author tested with. Version drift is a known source of "works on my machine" incidents.
2. **Security and supply-chain consistency.** Exact pins on Terraform and providers match the SHA-pin posture on GitHub Actions. The org's overall stance is "if it can be pinned exactly, pin it exactly."
3. **Failure-mode visibility.** `terraform init` aborting with "required Terraform version is X, you have Y" is unambiguous. Compatibility issues that surface partway through `terraform plan` or `terraform apply` are harder to diagnose and may leave partial state behind.
4. **Cross-module composability within the org.** Because the maintainer controls every module, exact-pinning all of them to the same Terraform version is straightforward; multi-module satisfiability concerns do not apply.
5. **Tested-and-proven posture.** Publishing a module that says "should work with Terraform >= 1.9" makes a claim the maintainer has not actually verified. Pinning `= 1.9.8` says only what has been tested.
6. **Renovate fitness.** Renovate's `rangeStrategy: "pin"` operates correctly on exact-pinned versions: it bumps the exact version on each update, requiring an explicit author-controlled PR for each change.

## Considered Options

1. **Exact pins for both Terraform and providers.** `terraform { required_version = "= X.Y.Z" }` and `required_providers` entries with `version = "= X.Y.Z"`. Renovate uses `rangeStrategy: "pin"`.
2. **Range constraints with pessimistic operator (`~>`).** Permits patch-level updates without re-running tests.
3. **Range constraints with minimum (`>=`).** Permits any newer version.
4. **Hybrid: exact-pin Terraform CLI, range-pin providers.** Lock the runtime, allow provider drift.
5. **No constraint at all.** Omit `required_version` and `required_providers` constraints; let consumers choose.

## Decision Outcome

Chosen option: **Option 1, exact pins for both Terraform and providers.**

In every repository that adopts this baseline:

- The `terraform { }` block in `versions.tf` MUST set `required_version = "= X.Y.Z"` using a single exact version. Range operators (`>=`, `~>`, etc.) MUST NOT be used.
- Every `required_providers` entry MUST set `version = "= X.Y.Z"` using a single exact version.
- Every Terraform-shape type-template Renovate baseline sets `terraform.rangeStrategy: "pin"` for Terraform manager updates. Consumers inherit this via `extends: ["github>NWarila/<type-template>"]` per [ADR-0004](0004-use-renovate-for-dependency-updates.md). Repo-local Renovate configs MUST NOT override this to `"bump"`, `"replace"`, or `"widen"` without a superseding repo-level ADR.
- The README's "Provider Requirements" or equivalent table MUST display the exact pinned versions and explain that consumers must run that exact CLI version.
- When a repository updates either the Terraform CLI or a provider version, the update MUST be tested against the pinned version before merging the Renovate PR. A `terraform test` suite that runs on every PR satisfies this requirement.

This refines the rangeStrategy guidance in [ADR-0004](0004-use-renovate-for-dependency-updates.md) §Decision Outcome by making the Terraform stack's answer unambiguous: **always pin exactly**. ADR-0004's decision to use Renovate with per-template baselines remains in force.

## Pros and Cons of the Options

### Option 1: Exact pins for both Terraform and providers (chosen)

- **Good, because** every consumer runs the exact CLI and provider version the author tested with; reproducibility is total.
- **Good, because** failure modes are predictable: `terraform init` fails fast on mismatch with a clear message.
- **Good, because** supply-chain posture is consistent with the org's SHA-pin policy on GitHub Actions.
- **Good, because** Renovate's `rangeStrategy: "pin"` operates cleanly on exact pins; each version bump is an explicit, reviewable PR.
- **Good, because** authors cannot accidentally publish a "should work with anything ≥ X" claim they have not actually verified.
- **Bad, because** consumers must update their Terraform CLI when a module bumps. For consumers using `tfenv` or `asdf`, this is a one-line `.tool-versions` change. For consumers without per-project version management, it is more friction.
- **Bad, because** in a hypothetical future with cross-org module consumption, an exact-pinned dependency tree is harder to satisfy than a range-pinned one. Mitigation: this is not a concern in the current org's consumption model.
- **Neutral, because** it imposes more discipline on the maintainer (every Renovate PR requires testing against the new exact version) but the discipline matches the org's overall posture.

### Option 2: Pessimistic operator (`~> X.Y`)

- **Good, because** it permits patch-level CLI/provider updates without per-update testing or PRs.
- **Good, because** it is the most common pattern in the wider Terraform community.
- **Bad, because** consumers may run a slightly different version from the author's tested version; subtle behavior differences slip through.
- **Bad, because** it weakens the reproducibility argument — "tested with 1.9.8, deployed with 1.9.12" is not the same as "tested and deployed with 1.9.8".
- **Bad, because** Renovate's behavior for `~>` versions is to bump the floor, not pin to the exact version, leaving the same drift surface.

### Option 3: Minimum constraint (`>= X.Y`)

- **Good, because** it is the most permissive option for consumers; any newer CLI works.
- **Bad, because** it makes a claim the author has not verified ("should work with anything ≥ X"). Future Terraform versions may break this assumption silently.
- **Bad, because** it provides no upper-bound protection; a consumer running a future Terraform major version might break in unpredictable ways with no constraint to catch it.

### Option 4: Hybrid — exact CLI, range providers

- **Good, because** it locks the runtime (the most volatile component) while permitting provider patches.
- **Bad, because** it introduces inconsistency: why pin some things and not others? The org's stance is "pin everything that can be pinned."
- **Bad, because** providers are equally susceptible to surprise behavior changes; locking the CLI but not the provider gives a false sense of reproducibility.

### Option 5: No constraint

- **Good, because** it imposes nothing on consumers.
- **Bad, because** it abandons the reproducibility and supply-chain arguments entirely.
- **Bad, because** Terraform itself recommends including `required_version` and `required_providers` for any non-trivial configuration; omitting them is a documentation deficit, not a permissive choice.

## Confirmation

Adherence to this ADR is confirmed by the following mechanisms. The wording `MUST`, `SHOULD`, and `MAY` follows [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) conventions.

1. **Constraint operator check.** Every `required_version` and `required_providers[].version` value MUST use the `=` exact operator. A CI script or `tflint` rule MAY assert this; the regex `^=\s*[0-9]+\.[0-9]+\.[0-9]+$` is sufficient for the exact-pin shape.
2. **Renovate rangeStrategy check.** Every Terraform-shape type-template baseline MUST set `terraform.rangeStrategy: "pin"` for Terraform manager updates. Repo-local overrides MAY narrow this for a specific manager but MUST NOT widen it without a superseding repo-level ADR. A CI script MAY assert this.
3. **README documentation.** Repositories that publish Terraform modules MUST document the exact pinned Terraform CLI version and provider versions in the README's prerequisites or provider requirements section, with an explicit statement that consumers must run those exact versions.
4. **Test-before-bump rule.** A Renovate PR that bumps the Terraform CLI version or a pinned provider version SHOULD NOT be merged without the maintainer running the test suite against the new version. A CI workflow that runs `terraform test` on every PR satisfies this requirement automatically.
5. **Editorial rule.** A relaxation of the exact-pin policy (e.g., adopting `~>` for a specific repo) is an architectural decision and MUST be recorded as a repository-level superseding ADR.

## Consequences

### Positive

- Reproducibility: every consumer runs the exact CLI and provider version the author tested with.
- Failure modes are predictable and fail-fast.
- Supply-chain posture is consistent across SHA-pinned Actions, exact-pinned Terraform, and exact-pinned providers.
- Each version update is an explicit, reviewable, testable Renovate PR rather than silent drift.

### Negative

- Consumers must update their local Terraform CLI on every CLI version bump in a depended-on module. For consumers using `tfenv` or `asdf` this is trivial; for others it is more friction.
- The org now ships modules that have a hard external dependency on a specific Terraform version. Switching modules to a newer Terraform requires a coordinated bump across every consumer.
- Renovate generates more frequent PRs against the org as Terraform and providers release. The maintainer absorbs the review burden.

### Neutral

- The exact-pin policy applies only inside `NWarila`. Future external consumers (if any) inherit the strictness; if their context demands range constraints they fork or pin internally.
- Repositories that today have range constraints will be migrated to exact pins via the implementing PRs. The migration is a one-time editorial pass; ongoing maintenance is a single-line edit per Renovate PR.

## Assumptions

This decision rests on the following assumptions. If any becomes false, this ADR should be revisited:

1. The `NWarila` org continues to consume Terraform modules primarily from itself, not from third-party authors with conflicting version constraints.
2. Renovate's `rangeStrategy: "pin"` continues to behave as documented — converting ranges to exact pins on the next bump and bumping exact pins to newer exact versions thereafter.
3. Consumers of `NWarila` Terraform modules are willing to accept the discipline of running the exact pinned CLI version.

## Supersedes

None. This ADR refines [ADR-0004](0004-use-renovate-for-dependency-updates.md) §Decision Outcome's rangeStrategy guidance but does not supersede ADR-0004 in full; ADR-0004's choice of Renovate over Dependabot and the shared-baseline pattern remain in force.

## Superseded by

None (current).

## Implementing PRs

Pending. The first implementing PR ships in `terraform-proxmox-iso-manager-framework`, which migrates `terraform/versions.tf` from `required_version = ">= 1.9"` to `= 1.9.8` and from `version = ">= 0.98.1"` to `= 0.98.1`, simplifies `.github/renovate.json5` to inherit the org baseline (which now sets `terraform.rangeStrategy: "pin"`), and adds `terraform test` coverage to enforce the test-before-bump rule.

## Related ADRs

- [ADR-0001](0001-use-architecture-decision-records.md) — establishes the format and three-tier scope structure of decision records.
- [ADR-0004](0004-use-renovate-for-dependency-updates.md) — establishes Renovate as the org's dependency-update tool. ADR-0005 refines ADR-0004's rangeStrategy guidance to "always pin exactly".

## Compliance Notes

This ADR strengthens the supply-chain posture by ensuring that every Terraform configuration consumed in `NWarila` runs against a known, tested set of CLI and provider versions.

| Framework              | Control / Practice ID                                                | Potential Evidence Contribution                                                                                                |
| ---------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| NIST SP 800-53 Rev. 5  | CM-2 (Baseline Configuration)                                        | Exact-pinned Terraform and provider versions are part of the baseline configuration of every infrastructure deployment.       |
| NIST SP 800-53 Rev. 5  | SI-7 (Software, Firmware, and Information Integrity)                 | Exact pins reduce the surface for unintentional or malicious version changes between author-tested and consumer-deployed.     |
| NIST SP 800-218 (SSDF) | PS.2 (Provide a Mechanism for Verifying Software Release Integrity)  | Combined with SHA-pinned Actions, exact-pinned Terraform contributes to release-integrity verification across the toolchain.  |
