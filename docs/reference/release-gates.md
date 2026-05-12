# Release Gates

Release candidates must pass:

- `python tools/verify.py ci`
- `python tools/verify.py integration`
- security workflow
- release evidence workflow when publishing a versioned release

Consumers should pin this template by commit SHA when mirroring reusable workflows or scaffold files.
