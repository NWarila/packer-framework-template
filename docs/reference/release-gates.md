# Release Gates

Release candidates must pass:

- `python tools/verify.py ci`
- `python tools/verify.py integration`
- `python tools/verify.py workflow-helper-tests`
- `python tools/verify.py opa-artifact`
- `python tools/verify.py plugin-install-check`
- `python tools/check_packer_plugin_provenance.py --upstream` in release evidence
- security workflow
- release evidence workflow when publishing a versioned release

Push-triggered release-please is opt-in. Set the repository variable
`RELEASE_PLEASE_ON_PUSH=true` only after the repo is allowed to let GitHub
Actions create pull requests.

Framework-derived repositories should pin this template by commit SHA when mirroring reusable workflows or scaffold files.
The optional framework-build reusable is `.github/workflows/reusable-packer-framework-build.yaml`; call it by commit SHA and pass a 40-character `framework_ref` that matches that pin. Runner repositories own scheduling and promotion, but release evidence is still type-aware: call `.github/workflows/reusable-release-evidence.yaml` with `repo_type: runner` so the release captures runner inventory and the pinned framework SHA.
