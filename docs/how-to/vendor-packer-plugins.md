# Vendor Packer Plugins

Use this posture when a derivative framework cannot depend on live third-party
plugin release downloads during CI or release evidence.

## Steps

1. Keep exact plugin pins in `packer/packer.pkr.hcl`.
2. Mirror the plugin release ZIP and SHA256SUMS file into an internal artifact
   store.
3. Keep `packer/plugin-provenance.json` in sync with the mirrored checksum
   table.
4. Extract the platform plugin binary from the mirrored ZIP.
5. Install that local binary into Packer's normal plugin directory:

   ```sh
   packer plugins install --path ./vendor/packer-plugin-git_v0.6.5_x5.0_linux_amd64 github.com/ethanmdavidson/git
   ```

6. Run the local provenance check:

   ```sh
   python tools/check_packer_plugin_provenance.py --installed
   ```

`packer plugins install --path` installs a local binary without downloading the
plugin from the public registry. Do not pass a version constraint with `--path`;
Packer derives the version from the plugin binary metadata and filename.

By default, `tools/check_packer_plugin_provenance.py --installed` checks the
same plugin root Packer uses for the current platform:

| Platform | Default plugin root |
| --- | --- |
| Linux/macOS | `$HOME/.config/packer/plugins` |
| Windows | `%APPDATA%\packer.d\plugins` |

Pass `--plugin-root` when CI installs plugins into an isolated cache or vendor
directory.

Release evidence should still run `tools/check_packer_plugin_provenance.py`.
Public-network release jobs can add `--upstream` to detect retag drift against
the committed upstream lock. Air-gapped jobs should instead compare the internal
mirror's SHA256SUMS file to `packer/plugin-provenance.json` before installing.
