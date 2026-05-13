# Release Gates

PRs to `main` on this template must pass:

- `actionlint` (workflow syntax)
- `workflow helper tests` (ShellCheck, workflow input binding checks, and Bats coverage for workflow helpers)
- `markdownlint` (docs)
- `packer verify` (`python tools/verify.py verify`, including Packer validation, plugin install checks, OPA policy tests, docs, manifest, and integration)
- `packer verify / windows path checks` (Windows path-sensitive Packer validation)
- `org-baseline / verify` (drift-gate against `NWarila/.github` at pinned source-ref)
- `Trivy (filesystem & secrets)`, `Gitleaks (secret scan)`, `zizmor (Actions security)` (security)
- `CodeQL` (`security.yaml`)
- `OpenSSF Scorecard` (`security.yaml`)

Release candidates must also pass release evidence, including
`python tools/check_packer_plugin_provenance.py --upstream`, before publishing
a versioned release.

Push-triggered release-please is opt-in. Set the repository variable
`RELEASE_PLEASE_ON_PUSH=true` only after the repo is allowed to let GitHub
Actions create pull requests.

Framework-derived repositories should pin this template by commit SHA when mirroring reusable workflows or scaffold files.
The optional framework-build reusable is `.github/workflows/reusable-packer-framework-build.yaml`; call it by commit SHA and pass a 40-character `framework_ref` that matches that pin. Runner repositories own scheduling and promotion, but release evidence is still type-aware: call `.github/workflows/reusable-release-evidence.yaml` with `repo_type: runner` so the release captures runner inventory and the pinned framework SHA.
