# Architecture

`packer-framework-template` is the reference Packer framework template. It separates repo-quality scaffolding from provider-specific image-building details so real frameworks can replace only the builder implementation while keeping the same validation, security, release, and documentation posture. It is not a runner template; runner repositories own scheduling, promotion, environment approvals, and provider-specific publication.

## Template Boundary

The template owns:

- A complete credential-free Packer framework under [`packer/`](../../packer/) that demonstrates the image contract without touching a hypervisor, cloud account, ISO library, or artifact registry.
- Linux and Windows example inputs under [`examples/`](../../examples/) that exercise the install-template contract for both cloud-init and Autounattend-style content.
- Universal reusable workflows for CodeQL, Scorecard, IaC/security scanning, Packer framework build validation, release-please, release evidence, and trusted-bot auto-merge.
- A template-tier `baseline-manifest.json` that tells derivative frameworks which repo-hygiene files should stay byte-identical.
- Framework-template ADRs under [`docs/decision-records/template/`](../decision-records/template/) that explain shared Packer framework decisions.
- The normalized verification entrypoint, [`tools/verify.py`](../../tools/verify.py), used by local developers and CI.

It does not own a real image target. Real frameworks, such as `nwarila-platform/proxmox-packer-framework`, own hypervisor-specific sources, secrets, ISO provenance, artifact publication, and provider-specific tests.

## Packer Layer

The Packer layer has four jobs:

1. Declare exact Packer and plugin pins in `packer/packer.pkr.hcl`.
2. Accept image definitions through `packer/variables.pkr.hcl`.
3. Normalize and render those definitions in `packer/locals.pkr.hcl`.
4. Produce credential-free build evidence through `packer/builds.pkr.hcl`.

The reference source uses Packer's built-in `file` builder to turn the rendered installer template into a concrete local artifact. That keeps the template credential-free while proving rendered content is consumed by a builder, not only written by a shell step. Derivative frameworks replace that source with Proxmox, VMware, AWS, Azure, or another builder and keep the surrounding shape: variables describe images, locals normalize data, source blocks map normalized data to a builder, and build blocks own provisioning/post-processing order.

## Inputs And Outputs

Derivative frameworks should preserve these commands:

- `python tools/verify.py ci` checks formatting, Packer init/validate/inspect, Python linting, YAML linting, OPA policy, docs layout, ADR indexing, and manifest health.
- `python tools/verify.py integration` runs a real `packer build` using the reference Linux var file and writes local build evidence.
- `python tools/verify.py verify` runs both layers.

The reference build writes generated evidence under `packer/artifacts/` and `packer/manifests/`. Those files are intentionally ignored except for `.gitkeep` placeholders. Real frameworks can replace the output destinations or post-processors, but they should keep the idea that a build produces reviewable evidence without committing runtime artifacts.

Framework-derived repositories can call `.github/workflows/reusable-packer-framework-build.yaml` by SHA to run this framework contract with caller-supplied input files. The reusable validates `framework_ref` and `input_ref` before checkout, checks out the pinned framework plus an optional input repository, applies a destination-allowlisted overlay, validates ordered var-file paths, runs Packer init/validate/inspect, and optionally builds/uploads generated evidence. It does not define runner repository layout or promotion policy.

Runner overlays may land only under `packer/repos/` and `packer/fixtures/runtime/`. Both directories have committed README files because they are protocol boundaries, not framework-owned data stores. The full runner-to-framework wire contract is documented in [`docs/reference/runner-protocol.md`](../reference/runner-protocol.md). Treat that protocol as the handoff point between this framework template and the upcoming runner template.

CI exercises the reference framework on Linux and keeps a Windows matrix entry for path-sensitive behavior. Linux runs the full verification surface; Windows runs Packer init, installed-plugin provenance checks, and Python tests so platform-specific path logic stays covered.

## External Dependencies

- [`NWarila/.github`](https://github.com/NWarila/.github) provides org-baseline ADR masters mirrored under `docs/decision-records/org/`.
- Packer, OPA, Ruff, yamllint, actionlint, markdownlint, CodeQL, Trivy, Gitleaks, zizmor, and Scorecard form the validation and security toolchain.
- Renovate owns reviewed updates for Packer, Packer plugins, GitHub Actions, OPA, and Python lint tooling.
