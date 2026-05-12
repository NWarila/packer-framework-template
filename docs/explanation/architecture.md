# Architecture

`packer-framework-template` separates repo-quality scaffolding from provider-specific image-building details.

The Packer layer has four jobs:

1. Declare exact Packer and plugin pins in `packer/packer.pkr.hcl`.
2. Accept image definitions through `packer/variables.pkr.hcl`.
3. Normalize and render those definitions in `packer/locals.pkr.hcl`.
4. Produce credential-free build evidence through `packer/builds.pkr.hcl`.

Real frameworks replace the `null` source with a provider source such as Proxmox, VMware, AWS, or Azure. They should keep the same contract boundaries: variables describe images, locals normalize data, source blocks map normalized data to the builder, and build blocks own provisioning/post-processing order.
