# ADR-repo/0001: Use the Credential-Free File Builder for Reference Validation

| Field          | Value                                   |
| -------------- | --------------------------------------- |
| Status         | Accepted                                |
| Date           | 2026-06-02                              |
| Authors        | Nick Warila (@NWarila)                  |
| Decision-maker | Nick Warila (sole portfolio maintainer) |
| Consulted      | Template ADR-0002 (keep reference framework credential-free). |
| Informed       | Derivative Packer frameworks, CI pipeline. |
| Reversibility  | Low                                     |
| Review-by      | N/A (Accepted)                          |

## TL;DR

This repository's `packer/source.pkr.hcl` uses Packer's built-in `file` builder
rather than a real provider source. The file builder is the only reasonable
choice for a public template that must run in untrusted CI without secrets.

## Context and Problem Statement

A template repository that demonstrates a Packer framework pattern must be
runnable by any contributor, in public CI, and by automated tooling without
owning Proxmox, VMware, AWS, or any other provider credential. At the same time,
the reference build must exercise Packer itself — not a shell script that only
mimics Packer — so the framework contract is actually tested.

The question is: which Packer source block satisfies both constraints?

## Decision Drivers

1. Public CI must not require any secrets to complete the integration job.
2. The reference build must invoke Packer and produce reviewable evidence.
3. The source block must be replaceable with a real provider block by a
   framework derivative without changing the surrounding variables, locals,
   builds, or repo-quality surface.
4. The pattern must remain demonstrable without owning or paying for
   infrastructure.

## Considered Options

1. Packer `file` builder that reads the rendered installer template and writes
   it as a local artifact.
2. Packer `null` builder (no real build step, just provisioners).
3. Docker builder with a public base image.
4. Real provider source (Proxmox, VMware, AWS).

## Decision Outcome

Chosen option: **Option 1, Packer `file` builder.**

The `file` builder reads the installer template rendered in `packer/locals.pkr.hcl`
and writes it to `packer/artifacts/`. This proves that rendered installer content
flows through Packer's full source-build lifecycle, not just through a shell step,
without any infrastructure dependency.

## Pros and Cons of the Options

### Option 1: `file` builder

- Good, because it runs without credentials.
- Good, because Packer parses, validates, and executes the full build graph.
- Good, because rendered installer content is consumed by the builder, making
  the rendering step testable end-to-end.
- Bad, because it does not test provider-specific image creation.
- Bad, because the `file` builder is not available as an external plugin and
  has narrower HCL surface than a real provider.

### Option 2: `null` builder

- Good, because it runs without credentials.
- Bad, because no artifact is produced; the rendering pipeline is not verified
  by Packer itself.
- Bad, because the build graph is trivially hollow.

### Option 3: Docker builder

- Good, because it can produce a real image layer.
- Bad, because it requires Docker to be available in CI runners.
- Bad, because it shifts provider coupling from Proxmox/cloud to container
  infrastructure, which is irrelevant for the template's VM-image focus.

### Option 4: Real provider source

- Good, because it tests actual image creation.
- Bad, because it requires secrets, infrastructure, and an ISO store.
- Bad, because it cannot run in public CI or be demonstrated without setup.

## Confirmation

1. `packer/source.pkr.hcl` contains only a `source "file"` block.
2. `python tools/verify.py integration` completes without provider credentials.
3. `packer/artifacts/` and `packer/manifests/` receive generated evidence.
4. OPA policy in `policies/opa/packer_artifact.rego` validates the produced
   manifest schema.

## Consequences

### Positive

- The template is safe to open-source and run in public CI.
- Contributors can validate the full Packer pipeline locally before requesting
  access to a provider.

### Negative

- Provider-specific source behavior must be tested in derivative frameworks.
- The `file` builder surface is narrower than a real provider, so some
  provider-specific locals may not be exercised at template level.

### Neutral

- Derivative frameworks replace only `packer/source.pkr.hcl` and the matching
  `required_plugins` entry; everything else is inherited.

## Assumptions

1. Derivative frameworks add provider-specific integration tests.
2. The `file` builder remains available as a Packer built-in.

## Supersedes

None.

## Superseded by

None (current).

## Implementing PRs

- Initial framework template: credential-free `file` source and local evidence.
- Adversarial review: replaced `null` source with `file` source so rendered
  installer content is consumed by Packer.

## Related ADRs

- [Template ADR-0002](../template/0002-keep-reference-framework-credential-free.md)
- [Org ADR-0003](../org/0003-use-deny-all-gitignore-strategy.md)

## Compliance Notes

None.
