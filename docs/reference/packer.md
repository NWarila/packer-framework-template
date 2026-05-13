# Packer Reference

The reference framework validates one selected image definition from `var.images`.

<!-- BEGIN_PACKER_DOCS -->
## Inputs

| Name | Description | Type | Default | Sensitive |
| --- | --- | --- | --- | --- |
| `images` | Image definitions keyed by stable image id. The reference framework builds one selected image from this map. | `map(object(...))` | `see source default` | `false` |
| `selected_image` | Optional image key from var.images. Empty selects the first key in lexical order. | `string` | `""` | `false` |
| `artifact_root` | Repo-rooted directory under packer/ where rendered installer artifacts are written. | `string` | `"artifacts"` | `false` |
| `manifest_dir` | Repo-rooted directory under packer/ where Packer manifest JSON files are written. | `string` | `"manifests"` | `false` |
| `build_context` | Non-secret run metadata merged into the generated manifest. | `map(string)` | `see source default` | `false` |
| `secret_seed` | Sensitive placeholder used to demonstrate Packer sensitive-variable handling without requiring real credentials. | `string` | `"reference-only"` | `true` |

## Generated Evidence

| Path | Purpose |
| --- | --- |
| `packer/artifacts/<image-key>/<output_file>` | Rendered installer input for the selected image. |
| `packer/artifacts/<image-key>/build-context.json` | Non-secret build metadata and secret seed fingerprint. |
| `packer/artifacts/<image-key>/builder-contract.json` | Builder wiring contract for real ISO sources. |
| `packer/manifests/<image-key>.json` | Packer manifest with framework custom data. |
<!-- END_PACKER_DOCS -->

Common commands:

```sh
packer init packer
python tools/check_packer_plugin_provenance.py --installed
python tools/check_packer_plugin_provenance.py --upstream
packer fmt -check -recursive packer examples
packer validate -var-file examples/linux/reference-linux.pkrvars.hcl packer
packer build -force -var-file examples/linux/reference-linux.pkrvars.hcl packer
```

The integration build writes:

- `packer/artifacts/<image-key>/<output_file>`
- `packer/artifacts/<image-key>/build-context.json`
- `packer/artifacts/<image-key>/builder-contract.json`
- `packer/manifests/<image-key>.json`

These files are generated evidence and are ignored by the default-deny `.gitignore` except for `.gitkeep` placeholders.
