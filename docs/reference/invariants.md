# Invariants

These invariants are enforced by CI, OPA, docs checks, or repository convention.

| Invariant | Enforcement |
| --- | --- |
| GitHub Actions `uses:` references are pinned to full commit SHAs, local paths, or digest-pinned Docker refs. | `policies/opa/repo_hygiene.rego` |
| Packer `required_version` uses an exact `= X.Y.Z` pin. | `policies/opa/repo_hygiene.rego` |
| Packer plugin versions use exact `= X.Y.Z` pins. | `policies/opa/repo_hygiene.rego` |
| The reference build remains credential-free. | ADR-template/0002 plus `python tools/verify.py integration` |
| Generated artifacts and manifests are not tracked. | default-deny `.gitignore` |
| ADRs live under `docs/decision-records/{org,template,repo}/` and are indexed. | `tools/check_adr_schema.py` |
| Documentation stays in the Diataxis layout. | `tools/check_docs_layout.py` |
| Release evidence uses the same pinned Packer version as the framework. | `release.yaml` and `reusable-release-evidence.yaml` |
| This template publishes framework evidence only; runner evidence and promotion workflows are out of scope. | `docs/explanation/architecture.md` and `reusable-release-evidence.yaml` |

Derivative frameworks may supersede template-tier decisions with repo-tier ADRs, but they should treat any supersession as an explicit design choice rather than incidental drift.

## Template-Family Conventions

- Framework templates expose exactly one tool-specific reusable workflow using
  `reusable-<tool>-framework-<verb>.yaml`. The verb names the natural action
  for that tool family; this template uses `build` because Packer produces image
  build artifacts.
- Framework `verify.py ci` targets keep `workflow-helper-tests` and
  `privileged-workflows` explicit, and `docs-check` owns ADR schema validation.
  Tool-specific lint, test, and policy targets may differ by stack, but each
  difference must be listed in `docs/reference/quality-gates.md`.
- Runner templates and runner consumers do not copy the framework reusable
  naming pattern unless they own executable framework logic.
