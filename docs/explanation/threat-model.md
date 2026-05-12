# Threat Model

The template assumes two primary risk areas:

- Supply-chain drift in GitHub Actions, Packer, plugins, Python tooling, and policy tools.
- Credential leakage from image-building workflows.

Controls:

- GitHub Actions must be pinned to full commit SHAs.
- Packer and plugin versions must use exact pins.
- The reference framework uses no real infrastructure credentials.
- Secret scanning and CodeQL reusable workflows are part of the default repo surface.
- Sensitive Packer variables demonstrate redaction without storing usable secrets.

Real image frameworks should extend this model with provider-specific risks such as hypervisor API tokens, ISO provenance, artifact signing, and image publication permissions.
