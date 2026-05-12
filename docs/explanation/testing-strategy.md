# Testing Strategy

## What The Tests Cover

This template repo's `ci.yaml` exercises the framework pattern and support tooling:

| Layer | Job or target | What it proves |
| --- | --- | --- |
| Packer framework | `python tools/verify.py verify` | `fmt`, `init`, `validate`, `inspect`, source-aware OPA, docs checks, and integration all pass. |
| Workflow YAML | `actionlint` | Workflow files parse and follow GitHub Actions semantics. |
| Workflow security | `zizmor` in `security.yaml` | Workflow code avoids known dangerous Actions patterns. |
| YAML data | `yamllint` | Workflow YAML is valid and consistently shaped. |
| Python tools | `ruff` | CI helper scripts lint clean. |
| Template manifest | `manifest-check` | The template-tier scaffold manifest loads and every source path exists. |
| Markdown | `markdownlint` | Documentation lints clean. |
| Documentation layout | `docs-layout` | Markdown stays inside the Diataxis and ADR directory structure. |
| Packer integration | `python tools/verify.py integration` | A real credential-free Packer build renders install content and writes build evidence. |

Derivative frameworks exercise this template by retaining the same `make` and `tools/verify.py` interface while replacing provider-specific source blocks, examples, and image publication paths.

## What The Tests Do Not Cover

- Real provider credentials and external services; this reference framework uses Packer's `null` source only.
- Guest OS boot behavior; no VM is created by the reference builder.
- ISO authenticity, artifact signing, and template publication; those belong to derivative frameworks.
- Repository ruleset enforcement, branch protection, and required status checks; those live in GitHub settings.

Provider-specific frameworks should add fixture builds, contract tests, and threat-model addenda around this baseline. A Proxmox framework, for example, should validate Proxmox token handling, ISO media selection, VM hardware defaults, and publication behavior in its own repo-tier tests.
