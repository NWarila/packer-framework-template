# Develop This Template

1. Install Packer, OPA, and Python dependencies from the top-level README.
2. Run `make setup`.
3. Edit the Packer framework files under `packer/`.
4. Keep example consumer inputs in `examples/` aligned with the variable contract.
5. Run `python tools/verify.py verify` before opening a PR.

Use `python tools/verify.py integration` when you only need the credential-free build smoke test.
