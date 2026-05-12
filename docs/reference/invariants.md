# Invariants

- GitHub Actions `uses:` references are pinned to full commit SHAs or local paths.
- Packer `required_version` is pinned with `= X.Y.Z`.
- Packer plugin versions are pinned with `= X.Y.Z`.
- The reference build remains credential-free.
- Generated artifacts and manifests are not tracked.
- ADRs live under `docs/decision-records/{org,template,repo}/`.
