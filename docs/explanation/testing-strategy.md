# Testing Strategy

## What The Tests Cover

This template repo's `ci.yaml` exercises the framework pattern and support tooling:

| Layer | Job or target | What it checks |
| --- | --- | --- |
| Packer framework | `python tools/verify.py verify` | `fmt`, `init`, plugin provenance, installed plugin sidecar checks, `validate`, `inspect`, renderer tests, source-aware OPA, artifact-aware OPA, generated-doc drift, docs checks, and integration all pass. |
| Packer Windows surface | `packer-ci` on `windows-latest` | Packer init, installed-plugin provenance checks, `validate`, and Python tests exercise Windows path handling, template rendering, and `%APPDATA%\packer.d\plugins` discovery. |
| Workflow helpers | `python tools/verify.py workflow-helper-tests` | ShellCheck, run-block input binding checks, and Bats tests pass for reusable framework-workflow helper scripts, including `validate_framework_ref.sh`, `validate_input_ref.sh`, overlay handling, and var-file argument generation. |
| Workflow YAML | `actionlint` | Workflow files parse and follow GitHub Actions semantics. |
| Workflow security | `zizmor` in `security.yaml` | Workflow code avoids known dangerous Actions patterns. |
| YAML data | `yamllint` | Workflow YAML is valid and consistently shaped. |
| Python tools | `ruff` | CI helper scripts lint clean. |
| Template manifest | `manifest-check` | The template-tier scaffold manifest loads and every source path exists. |
| Markdown | `markdownlint` | Documentation lints clean. |
| Documentation layout | `docs-layout` | Markdown stays inside the Diataxis and ADR directory structure. |
| Packer integration | `python tools/verify.py integration --case <name>` | A real credential-free Packer build renders install content, writes build evidence, and asserts manifest/build-context/builder-contract shape. |
| Release evidence | `.github/workflows/reusable-release-evidence.yaml` | Framework releases record Packer fmt/init/validate/inspect, plugin provenance, docs layout, and `python tools/verify.py opa-artifact`; runner/template releases snapshot runner inventory and framework pins without running Packer. |

Derivative frameworks exercise this template by retaining the same `make` and `tools/verify.py` interface while replacing provider-specific source blocks, examples, and image publication paths.

## What The Tests Do Not Cover

- Real provider credentials and external services; this reference framework uses Packer's credential-free `file` builder only.
- Guest OS boot behavior; no VM is created by the reference builder, though `builder-contract.json` documents the ISO-builder wiring contract.
- ISO authenticity, artifact signing, and template publication; those belong to derivative frameworks.
- Repository ruleset enforcement, branch protection, and required status checks; those live in GitHub settings.

Provider-specific frameworks should add fixture builds, contract tests, and threat-model addenda around this baseline. A Proxmox framework, for example, should validate Proxmox token handling, ISO media selection, VM hardware defaults, and publication behavior in its own repo-tier tests.
