# Mirroring

Derivative Packer framework repositories should mirror baseline files from this template when they want byte-identical repo hygiene, security, documentation, and release behavior.

`baseline-manifest.json` lists the files that are intended to remain byte-identical. Repo-specific implementation files under `packer/` and `examples/` are not byte-identical baseline files; they are the supported customization points.
