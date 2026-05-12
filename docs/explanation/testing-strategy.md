# Testing Strategy

The template uses layered checks:

- Packer formatting and validation catch HCL syntax and contract issues.
- `packer inspect` verifies the template can be introspected by tooling.
- OPA checks enforce source-level invariants such as SHA-pinned actions and exact Packer/plugin pins.
- Docs and ADR checks keep the template navigable and decision records indexed.
- The integration target runs a real `packer build` with the `null` source and writes build evidence without external credentials.

Provider-specific frameworks should add their own fixture builds and contract tests around this baseline.
