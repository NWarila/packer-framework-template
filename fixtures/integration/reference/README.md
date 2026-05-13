# Reference Integration Case

The `reference-linux`, `reference-windows`, and `reference-multi` cases in
`tools/ci/config.toml` are credential-free Packer integration fixtures.

They prove that:

- the selected image is resolved from `var.images`;
- rendered installer content is consumed by the `file` builder;
- sidecar evidence is written to `packer/artifacts/<image-key>/`;
- Packer manifests are written to `packer/manifests/`;
- `builder-contract.json` exposes the ISO-builder wiring contract that real
  derivative frameworks replace with provider-specific sources.
