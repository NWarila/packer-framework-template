# Develop This Template

## Local Setup

1. Install Packer, OPA, and Python dependencies from the top-level README.
2. Run `make setup`.
3. Run `packer init packer` once to install the pinned Packer plugin.

## Change Workflow

1. Edit the Packer framework files under `packer/`.
2. Keep example consumer inputs in `examples/` aligned with the variable contract.
3. Update docs and ADRs when the framework contract changes.
4. Run `python tools/verify.py ci` for fast feedback.
5. Run `python tools/verify.py integration` when you need the credential-free build smoke test.
6. Run `python tools/verify.py verify` before opening a PR.

Generated files under `packer/artifacts/` and `packer/manifests/` are evidence from local runs. Do not commit them unless a future ADR deliberately changes that policy.
