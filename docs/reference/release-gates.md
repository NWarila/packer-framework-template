# Release Gates

Release candidates must pass:

- `python tools/verify.py ci`
- `python tools/verify.py integration`
- security workflow
- release evidence workflow when publishing a versioned release

Push-triggered release-please is opt-in. Set the repository variable
`RELEASE_PLEASE_ON_PUSH=true` only after the repo is allowed to let GitHub
Actions create pull requests.

Consumers should pin this template by commit SHA when mirroring reusable workflows or scaffold files.
