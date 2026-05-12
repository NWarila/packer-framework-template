# Packer Reference

The reference framework validates one selected image definition from `var.images`.

Common commands:

```sh
packer init packer
packer fmt -check -recursive packer examples
packer validate -var-file=examples/linux/reference-linux.pkrvars.hcl packer
packer build -force -var-file=examples/linux/reference-linux.pkrvars.hcl packer
```

The integration build writes:

- `packer/artifacts/<image-key>/<output_file>`
- `packer/artifacts/<image-key>/build-context.json`
- `packer/manifests/<image-key>.json`

These files are generated evidence and are ignored by the default-deny `.gitignore` except for `.gitkeep` placeholders.
