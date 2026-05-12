# Contributing

Thanks for your interest in contributing. This guide applies to all repositories under [NWarila](https://github.com/NWarila) unless a repository has its own `CONTRIBUTING.md`.

## How to contribute

### Reporting bugs

Open an issue using the **Bug Report** template. Include steps to reproduce, expected behavior, and actual behavior.

### Suggesting features

Open an issue using the **Feature Request** template. Describe the problem you're trying to solve and any alternatives you've considered.

### Reporting documentation issues

Open an issue using the **Documentation** template with the page or section that needs improvement and your suggested change.

### Asking questions

Use [Discussions](https://github.com/NWarila/.github/discussions) for questions, ideas, and general conversation. Issues are for actionable work.

### Reporting security vulnerabilities

**Do not file public issues for security vulnerabilities.** See [SECURITY.md](SECURITY.md) for private reporting instructions.

## Submitting changes

1. Fork the repository and create a branch from the default branch.
2. Make your changes in focused, well-described commits.
3. Test your changes.
4. Open a pull request using the provided template.
5. Respond to review feedback.

### What makes a good pull request

- Focused on a single change or closely related set of changes
- Includes a clear description of what changed and why
- Links to a related issue when one exists
- Includes testing evidence appropriate to the change

### Local pre-commit prerequisites

This repository's `.pre-commit-config.yaml` uses pinned upstream hooks for
Python, YAML, workflow, shell, and Markdown linting. `pre-commit run
--all-files` installs those hook environments automatically.

A few hooks intentionally remain `language: system` because they validate this
Packer framework with local project tools rather than generic lint packages:

- `packer`
- `opa`
- `python`

## Code of conduct

All contributors are expected to follow the project's code of conduct. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## Repository-specific overrides

Individual repositories may have their own `CONTRIBUTING.md` with different or additional guidelines. When present, the repository-specific version takes precedence over this default.
