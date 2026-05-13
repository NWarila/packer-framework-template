# Packer Runner Protocol

Runner repositories call
`.github/workflows/reusable-packer-framework-build.yaml` to validate runner-owned
inventory against a SHA-pinned framework. The runner owns scheduling,
promotion, environment approval, and provider-specific publication. The
framework owns the reusable build contract, policy, rendering, and release
evidence shape.

## Required Inputs

Callers MUST pass `framework_ref` as a lowercase 40-character commit SHA for
`NWarila/packer-framework-template` or a derived framework repository. Floating
refs are rejected before checkout.

`input_repo` identifies the repository that supplies runner-owned input files.
When omitted, it defaults to the calling repository. `input_ref` identifies the
commit to read from `input_repo`; it defaults to `github.sha` and is also
required to be a lowercase 40-character SHA unless the caller explicitly sets
`allow_floating_input_ref: true`.

Floating `input_ref` is an emergency compatibility escape hatch, not the runner
default. Runner inventory is trusted input to the framework and should be pinned
with the same discipline as `framework_ref`.

## Pin Management

Runner repositories should let Renovate update `framework_ref` instead of
hand-bumping SHAs. The shared Renovate regex manager reads comments in workflow
YAML using the `git-refs` datasource. Put the annotation directly above the
input it manages:

```yaml
with:
  # renovate: depName=NWarila/packer-framework-template packageName=NWarila/packer-framework-template currentValue=main
  framework_ref: 0123456789abcdef0123456789abcdef01234567
```

Keep the reusable workflow `uses:` SHA and the body `framework_ref` under review
together. The exact Renovate policy comes from org ADR-0004 and the template's
`.github/renovate.json5` custom manager.

## Overlay Destinations

`overlay_paths` is a newline-separated list of
`<input-source>=><framework-destination>` entries. Sources are relative to the
input checkout. Destinations are relative to the framework checkout and are
allowlisted to:

- `packer/repos/`
- `packer/fixtures/runtime/`

Those are the only runner-owned landing zones. The allowlist prevents a runner
overlay from replacing framework code, Packer source files, policy, or workflow
definitions. `tools/ci/apply_overlay.sh` rejects absolute paths, `..` traversal,
destinations outside the allowlist, missing sources, and symlinks.

## Variable Files

`var_file` accepts one or more newline-separated paths relative to the input
checkout. `tools/ci/packer_var_file_args.sh` emits ordered Packer arguments:

```text
-var-file
../../input/packer/repos/public/base.pkrvars.hcl
-var-file
../../input/packer/repos/public/prod.pkrvars.hcl
```

The order is preserved, so later var files can intentionally override earlier
ones. Absolute paths and `..` traversal segments are rejected.

## Release Evidence

Runner repositories call
`.github/workflows/reusable-release-evidence.yaml` with `repo_type: runner`.
Runner-shaped release evidence snapshots `packer/repos/`, records
`packer/fixtures/runtime/` inventory if present, and captures the pinned
`framework_ref` from the calling workflow. Runner evidence does not install or
run Packer.

Framework repositories use `repo_type: framework`, which runs Packer evidence
gates, plugin provenance, artifact OPA policy, docs layout, and reference
snapshots. Runner-template repositories use `repo_type: template` until they are
forked into real runner repositories.

## Build Status Output

The reusable build exposes `build_status`:

- `validated`: Packer init, validate, and inspect ran, but `build` was false.
- `built`: Packer build also ran.

## Example

```yaml
jobs:
  validate-runner-inventory:
    uses: NWarila/packer-framework-template/.github/workflows/reusable-packer-framework-build.yaml@0123456789abcdef0123456789abcdef01234567
    with:
      framework_ref: 0123456789abcdef0123456789abcdef01234567
      input_repo: NWarila/packer-runner-template
      input_ref: fedcba9876543210fedcba9876543210fedcba98
      overlay_paths: |
        packer/repos/public/=>packer/repos/public/
        packer/fixtures/runtime/=>packer/fixtures/runtime/
      var_file: |
        packer/repos/public/base.pkrvars.hcl
        packer/repos/public/prod.pkrvars.hcl
      build: false
      upload_artifacts: false
```
