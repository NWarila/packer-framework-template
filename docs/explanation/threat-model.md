# Threat Model

This document is a STRIDE-style threat model for `NWarila/packer-framework-template` and, by extension, the Packer framework pattern this template demonstrates. It exists to make the security posture of derivative image frameworks legible: a real framework building real VM images inherits the same trust boundaries and adds whatever its hypervisor, cloud, ISO, and artifact registry introduce.

## Scope

What this document covers:

- The template repository's own threats: supply chain, CI compromise, contributor account compromise, and dependency drift.
- Threats inherent to the Packer framework pattern: image-build credential leakage, unreviewed plugin changes, installer-template tampering, and evidence/artifact confusion.
- Threats derivative frameworks should account for when they replace the credential-free `file` source with Proxmox, cloud, VMware, or another real builder.
- The framework boundary. This repository validates framework behavior; runner orchestration, environment promotion, and image publication workflows belong to runner or provider-specific repositories.

What this document does not cover:

- Threats specific to a real hypervisor or cloud API. Derivative frameworks own those addenda.
- Guest OS hardening posture. This template validates the framework contract, not a CIS or STIG profile.
- Operational runbooks. Incident response procedures live in each derivative framework's `docs/how-to/`, not here.

## Trust Boundaries

1. **Author to Repository.** Authors commit Packer HCL, workflows, policies, and docs. Trust depends on GitHub account security, review discipline, and branch protection.
2. **Repository to CI runner.** CI checks out the repo onto GitHub-hosted runners. Trust depends on GitHub runner-image integrity and Actions permissions.
3. **CI runner to Packer release/plugin sources.** `packer init` downloads pinned plugins and CI installs the pinned Packer binary. Trust depends on upstream release integrity and exact pins.
4. **Packer framework to installer templates.** Framework input templates are rendered into image build input. Trust depends on review of those templates and strict separation between framework-owned normalization and caller-supplied content.
5. **Packer framework to provider APIs.** The reference framework does not cross this boundary. Derivative frameworks do when they talk to Proxmox, AWS, VMware, Azure, or another image target.
6. **Build output to artifact readers.** The reference only writes local evidence. Real frameworks may publish templates, AMIs, images, checksums, SBOMs, or attestations.

## Threats By Category

### Spoofing

- **Compromised commit on the template repo.** An attacker with author access commits malicious workflow YAML or Packer HCL. Mitigation: branch protection, code-owner review, SHA-pinned Actions, and OPA policy enforcement.
- **Spoofed GitHub Action dependency.** A workflow uses a tag or branch that later moves. Mitigation: `repo_hygiene.rego` requires full 40-character SHA pins, local reusable workflows, or digest-pinned Docker actions.
- **Spoofed Packer plugin release.** A malicious plugin version is accepted silently. Mitigation: `packer/packer.pkr.hcl` pins plugin versions exactly, OPA rejects ranges, `packer/plugin-provenance.json` commits the upstream release checksum table, release evidence compares live upstream SHA256SUMS against that lock, and `tools/check_packer_plugin_provenance.py` verifies required plugin provenance plus installed binary sidecars after `packer init`. The reference `github.com/ethanmdavidson/git` plugin is third-party; derivative frameworks that cannot accept that supply-chain posture should vendor plugins or install from an internal mirror using [`docs/how-to/vendor-packer-plugins.md`](../how-to/vendor-packer-plugins.md).

### Tampering

- **Installer-template tampering.** A framework input change weakens a cloud-init, Kickstart, Autounattend, or preseed template. Mitigation: the template keeps installer templates under reviewable source control, renders them into build evidence, and evaluates generated artifacts with `packer_artifact.rego`.
- **Build evidence mutation.** Generated manifests or rendered installer files could be mistaken for source truth. Mitigation: generated evidence under `packer/artifacts/` and `packer/manifests/` is ignored by default; source HCL and example templates are the reviewed inputs.
- **Floating runner inventory refs.** A runner caller that uses a branch or tag for `input_ref` can silently change inventory data between review and execution. Mitigation: `.github/workflows/reusable-packer-framework-build.yaml` validates `framework_ref` and resolved `input_ref` before checkout, `tools/ci/validate_input_ref.sh` rejects non-SHA `input_ref` values by default, and `tests/ci/validate_input_ref.bats` covers tags, short SHAs, uppercase SHAs, and the explicit opt-out path. `framework_ref` validation is unconditional; `input_ref` has the deliberate `allow_floating_input_ref: true` escape hatch for exceptional callers, and the workflow emits a warning when that escape hatch is used.
- **Workflow tampering through privileged PR events.** `pull_request_target` could execute PR-controlled content with a write token. Mitigation: only `auto-merge.yaml` may use `pull_request_target`, and OPA rejects unsafe PR-content reads in that path.

### Repudiation

- **An author denies a release-affecting change.** Mitigation: Git history, PR review, workflow runs, and release-please-generated changelog entries provide durable attribution.
- **A framework operator denies which inputs built an image.** Mitigation: the reference build writes `build-context.json`, `builder-contract.json`, and a Packer manifest. Real frameworks should preserve image key, source commit, input file, builder, and artifact identifiers in release evidence.

### Information Disclosure

- **Packer variables leak provider credentials.** A real image build may use hypervisor API tokens, SSH keys, WinRM passwords, or cloud credentials. Mitigation: the reference uses no real credentials and demonstrates sensitive-variable handling. Derivative frameworks must keep secrets in GitHub secrets/OIDC and avoid echoing derived values.
- **Workflow logs reveal rendered installer secrets.** Installer templates can embed bootstrap users, tokens, or passwords. Mitigation: the reference templates contain no usable secrets, `secret_seed` is fingerprinted rather than written raw, and `packer_artifact.rego` rejects obvious rendered credential and private-key markers.
- **Public repo accidentally tracks generated artifacts.** Generated images, manifests, or local caches can contain sensitive metadata. Mitigation: default-deny `.gitignore` tracks only allowlisted files and keeps generated evidence untracked by default.

### Denial Of Service

- **Packer/plugin release source unavailable.** CI fails during installation or `packer init`. Mitigation: exact pins make the failure explicit. Air-gapped frameworks can document a mirror strategy in repo-tier ADRs.
- **Provider API unavailable.** Derivative frameworks fail real builds when Proxmox/cloud APIs are down. Mitigation: outside this template; real frameworks should document retry and recovery posture.
- **Long-running image builds exhaust CI minutes.** Real image builds can be expensive. Mitigation: this template's reference build is fast; real frameworks should separate cheap validation from trusted publish builds.

### Elevation Of Privilege

- **Over-scoped provider credentials.** A Packer API token can create, modify, or delete more infrastructure than the image build needs. Mitigation: derivative frameworks should scope tokens or OIDC roles to least privilege and document them in repo-tier threat models.
- **Workflow token over-permission.** A job that only validates Packer should not write contents or releases. Mitigation: workflows default to `contents: read`; write permissions are isolated to release and auto-merge surfaces.
- **Caller-supplied content becomes framework code.** Reusable framework builds may need input overlays, but those overlays must not alter workflow or framework implementation files. Mitigation: `tools/ci/apply_overlay.sh` only allows destinations under `packer/repos/` or `packer/fixtures/runtime/`, and `tests/ci/apply_overlay.bats` covers traversal and disallowed-destination cases.

## What A Derivative Framework Adds

A real Packer framework inherits this threat model and adds, at minimum:

- Provider-specific credential handling and least-privilege permissions.
- ISO/media provenance and checksum policy.
- Guest OS hardening assumptions and bootstrap-secret handling.
- Artifact publication, signing, retention, and rollback behavior.
- Incident response for compromised images and revoked build credentials.
