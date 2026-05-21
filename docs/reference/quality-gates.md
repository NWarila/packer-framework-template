# Quality Gates

Each automated check enforced by this repository plays one of four roles. The
role determines *when* the check runs and *what failure means*.

| Role | Meaning | When it runs |
| --- | --- | --- |
| **Blocking** | Required for PR merge to `main`. Failure blocks the PR. | `pull_request` / `merge_group` triggers in `ci.yaml`, `drift-gate.yaml`, `security.yaml` |
| **Scheduled** | Periodic posture telemetry. Runs on a cron; does **not** block PRs. | `schedule` trigger in `security.yaml` |
| **Release** | Runs at release-cut time. Failure blocks the release tag and prevents the evidence bundle from being attached. | `release.yaml` and the reusables it calls |
| **Advisory** | Surfaces signal without blocking. Reserved for steps whose *publishing channel* is best-effort, or where the gate is explicitly opt-in. | Specific steps marked `continue-on-error: true` (see below) |

## Gate inventory

| Gate | Source | Role | Notes |
| --- | --- | --- | --- |
| packer verify (`verify.py verify`) | `ci.yaml` job running `verify.py verify` | Blocking | Wraps `packer-syntax`, `packer init`, plugin-provenance (lockfile + installed), `packer-validate-safe`, `packer inspect`, lint, rendered-build and variable-validation tests, OPA (test + repo-hygiene + artifact), `workflow-helper-tests`, `privileged-workflows`, docs-diff, docs-layout, ADR schema, manifest, integration. |
| packer syntax (`verify.py packer-syntax`) | `verify.py` local/CI target | Blocking | Runs `packer fmt -check` plus `packer validate -syntax-only` without var files or datasource resolution. |
| packer validate-safe (`verify.py packer-validate-safe`) | `verify.py` local/CI target | Blocking | Runs OPA repo-hygiene before `packer validate`; unannotated `data` blocks in `packer/*.pkr.hcl` fail unless explicitly tagged `# datasource: ok-at-validate`. |
| workflow-helper-tests | `verify.py workflow-helper-tests` (in `ci` target) | Blocking | ShellCheck on `tools/ci/*.sh`, Python workflow-input checks, Bats coverage. |
| privileged-workflows | `verify.py privileged-workflows` (in `ci` target) | Blocking | `check_privileged_workflows.py` + fixture-driven test runner. Rejects `actions/checkout` and PR-controlled refs in any `pull_request_target` workflow, transitively through local reusables. |
| plugin-provenance | `verify.py plugin-provenance` and `verify.py plugin-install-check` | Blocking | Verifies the `*.pkr.hcl.lock.json` and the installed plugin binaries match the declared provenance. Prevents silent plugin drift. |
| rendered-build / variable-validation tests | `verify.py test` (`test_render_reference_build.py`, `test_packer_variable_validation.py`) | Blocking | Negative-path coverage: bad variable shapes must fail validation. |
| drift-gate | `drift-gate.yaml` | Blocking | Verifies the org-baseline overlay matches `NWarila/.github` at the pinned source ref. |
| Trivy IaC misconfig + secrets | `security.yaml` -> `reusable-iac-security.yaml` (PR path) | Blocking | Trivy scan exit status is the gate; SARIF upload is advisory. |
| Gitleaks | `security.yaml` -> `reusable-iac-security.yaml` | Blocking by default | Caller-configurable via `inputs.gitleaks_advisory`. |
| zizmor (Actions posture) | `security.yaml` -> `reusable-iac-security.yaml` | Blocking | Exit status is the gate; SARIF upload is advisory. |
| CodeQL | `security.yaml` -> `reusable-codeql.yaml` | Blocking | SARIF upload is advisory. |
| OpenSSF Scorecard | `security.yaml` -> `reusable-scorecard.yaml` | Scheduled / push / branch protection / manual; skipped on PR and merge queue | Posture telemetry; skipped on PR paths because Scorecard GraphQL is gated on private repos. |
| Release evidence + SBOM + attestations | `release.yaml` -> `reusable-release-evidence.yaml` | Release | Bundles rendered Packer config, plugin lockfile, SBOM. Includes attestations for bundle and SBOM provenance. |
| Auto-merge (trusted bots) | `auto-merge.yaml` -> `reusable-auto-merge.yaml` | Not a gate | Operates on `pull_request_target` with no PR checkout; must keep passing `privileged-workflows`. |

## What is intentionally **not** in PR CI

To keep PR blast-radius small and the runtime predictable, the following
are explicitly **out of scope** for the blocking PR path:

- **Full VM / cloud image builds.** Packer can target AMI, Azure image,
  GCP image, etc.; those need cloud credentials, take minutes-to-hours,
  and produce paid artifacts. They belong on a manual or scheduled path.
- **Unreviewed datasource-resolving `packer validate`.** Packer's
  datasources (e.g., `amazon-ami`) can hit live APIs and cost money. PR
  CI runs syntax-only validation first, then `packer-validate-safe`; any
  `data` block must be explicitly tagged `# datasource: ok-at-validate`
  before full validation can run. Live cloud datasource checks belong on
  scheduled or manual paths.

## When `continue-on-error: true` is allowed

The repository deliberately limits this flag to three narrow contexts.
Anywhere else, it would mask a gate's failure and should be removed.

1. **SARIF upload to GitHub Security** (`reusable-iac-security.yaml`,
   `reusable-codeql.yaml`, `reusable-scorecard.yaml`) -- the *scan* is the
   gate and runs without `continue-on-error`. The upload step is
   best-effort because publishing to the Security tab requires GitHub
   Advanced Security on private repos. CodeQL disables the built-in upload
   and uploads the generated SARIF in a separate advisory step; findings
   remain visible in the run log and as workflow artifacts.
2. **Scorecard analysis on private repos** (`reusable-scorecard.yaml`) --
   Scorecard's GraphQL queries fail with *Resource not accessible by
   integration* on private repositories.
3. **Gitleaks advisory mode** (`reusable-iac-security.yaml`) -- caller-
   parameterised via `inputs.gitleaks_advisory`.

## Adding a new gate

1. Decide its role from the taxonomy above.
2. If the gate is reproducible locally, wire it through `tools/verify.py`.
3. Add a row to the inventory table.
4. If blocking, ensure it appears in the repository's required status
   checks (branch protection on `main`).
5. Do not add `continue-on-error: true` outside the three contexts listed
   above without an explicit rationale in the workflow file.
