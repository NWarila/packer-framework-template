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

Derivative frameworks may supersede template-tier decisions with repo-tier ADRs, but they should treat any supersession as an explicit design choice rather than incidental drift.
