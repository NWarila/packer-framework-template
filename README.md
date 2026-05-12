# packer-framework-template

Reference template for building Packer framework repositories: repos that own a reusable image-building contract, validation tooling, release evidence, and downstream integration pattern while consumer repos bring their own image data, installer templates, and provisioning content.

This template is intentionally credential-free. It uses Packer's `null` builder to prove the framework contract without touching a hypervisor, cloud account, ISO store, or secret. Real frameworks, such as `nwarila-platform/proxmox-packer-framework`, replace the source block and provider-specific variables while keeping the same repo-quality surface.

## Prerequisites

Install the same external tools CI uses before running the full local gates:

- Packer 1.15.0
- OPA 1.10.0
- Python 3.12+

## Quickstart

```sh
make help
make setup
python tools/verify.py ci
python tools/verify.py integration
```

`python tools/verify.py ci` runs Packer formatting, init, validate, inspect, Python tooling, YAML checks, OPA policy, docs layout, ADR schema, and manifest checks. `python tools/verify.py integration` executes a real credential-free Packer build that renders installer content and writes build evidence under `packer/artifacts/` and `packer/manifests/`.

## Packer Framework Shape

| File | Role |
| --- | --- |
| [`packer/packer.pkr.hcl`](packer/packer.pkr.hcl) | Packer CLI and plugin version pins. |
| [`packer/variables.pkr.hcl`](packer/variables.pkr.hcl) | Consumer-facing image contract. |
| [`packer/data.pkr.hcl`](packer/data.pkr.hcl) | Build metadata data sources. |
| [`packer/locals.pkr.hcl`](packer/locals.pkr.hcl) | Normalization, defaults, and template rendering. |
| [`packer/source.pkr.hcl`](packer/source.pkr.hcl) | Credential-free reference builder. Real frameworks replace this. |
| [`packer/builds.pkr.hcl`](packer/builds.pkr.hcl) | Build orchestration and release evidence output. |
| [`examples/`](examples/) | Linux and Windows example consumer var files/templates. |

## What This Is, And What It Isn't

| | This repo | A real framework |
| --- | --- | --- |
| Demonstrates the Packer framework pattern | Yes | Yes |
| Builds a real VM image | No, by design | Yes |
| Requires Proxmox, AWS, VMware, or cloud credentials | No | Usually |
| Suitable as a derivative repo template | Yes | N/A |

The reference build writes rendered installer input and a manifest. It does not publish an image artifact. That is deliberate: every moving part is about the framework contract, not provider-specific behavior.

## Normalized Repo Interface

| Command | Purpose |
| --- | --- |
| `make lint` | Packer fmt/init/validate/inspect plus Python and workflow YAML checks. |
| `make policy` | OPA policy tests plus policy evaluation against this repo. |
| `make docs-check` | Diataxis and ADR documentation layout checks. |
| `python tools/verify.py ci` | Repo-local quality gate. |
| `python tools/verify.py integration` | Credential-free Packer build using the Linux example. |
| `python tools/verify.py verify` | Full local verification: `ci` plus `integration`. |

To exercise the reference build directly:

```sh
packer init packer
packer validate -var-file=examples/linux/reference-linux.pkrvars.hcl packer
packer build -force -var-file=examples/linux/reference-linux.pkrvars.hcl packer
```

## Deriving A Real Framework

For a real Packer framework derived from this template, edit these first:

1. `README.md` and repo-specific docs.
2. `packer/source.pkr.hcl` and provider-specific variables.
3. `examples/` for the supported guest OS families.
4. `docs/decision-records/repo/` for local decisions.
5. Optional release and deploy workflows, only if the repo publishes versioned releases or artifacts.

The mirroring rules live in [`docs/reference/mirroring.md`](docs/reference/mirroring.md).

## License

MIT - see [LICENSE](LICENSE).
