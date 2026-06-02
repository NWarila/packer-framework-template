# Tutorial: Derive Your First Packer Framework

This tutorial walks you through creating a new Packer framework repository from
`packer-framework-template`. By the end you will have a credential-free framework
that validates cleanly under the same quality gate as the template, ready for a
real provider source block.

## Prerequisites

- Git and GitHub CLI (`gh`) installed.
- Packer 1.15.0, OPA 1.10.0, and Python 3.12+ installed locally.
- A GitHub organization or personal account where you can create repositories.

## Step 1: Create the Repository from the Template

On GitHub, click **Use this template** on `NWarila/packer-framework-template` and
name the new repository. For this tutorial, use `my-packer-framework`.

Alternatively, use the GitHub CLI:

```sh
gh repo create my-packer-framework \
  --template NWarila/packer-framework-template \
  --private \
  --clone
cd my-packer-framework
```

## Step 2: Install Local Tools

```sh
make setup
```

This installs Python dependencies, Packer plugins, and the other external tools
that CI uses. Inspect `tools/install_ci_tools.sh` if you need to adjust versions
for your platform.

## Step 3: Run the Baseline Verification

Before making any changes, confirm the template validates cleanly:

```sh
python tools/verify.py ci
```

All checks should pass. If they do not, see
[`docs/reference/quality-gates.md`](../reference/quality-gates.md).

## Step 4: Run the Reference Integration Build

The reference build proves that rendered installer content flows through Packer
without any provider credentials:

```sh
python tools/verify.py integration
```

Packer writes generated evidence under `packer/artifacts/` and
`packer/manifests/`. Those files are intentionally ignored; they are not
committed.

## Step 5: Update Repository Metadata

Edit these files for your framework:

- `README.md` — update the title, description, and provider notes.
- `docs/explanation/architecture.md` — describe your provider target.
- `docs/decision-records/repo/` — add at least one repo-tier ADR explaining
  your provider choice (see Step 7).

## Step 6: Replace the Source Block

Open `packer/source.pkr.hcl`. The template uses Packer's built-in `file` builder
as a credential-free stand-in. Replace it with your real provider source.

For a Proxmox example, the source block looks like:

```hcl
source "proxmox-iso" "linux" {
  proxmox_url              = var.proxmox_url
  username                 = var.proxmox_username
  token                    = var.proxmox_token
  node                     = var.proxmox_node
  iso_file                 = var.iso_file
  vm_name                  = local.image_name
  cores                    = 2
  memory                   = 2048
  # ... additional provider fields
}
```

Add the matching `required_plugins` entry in `packer/packer.pkr.hcl` and pin it
to an exact version. See
[Template ADR-0001](../decision-records/template/0001-pin-packer-and-plugin-versions-exactly.md)
for the pinning policy.

## Step 7: Add a Repo-Tier ADR

Add a decision record under `docs/decision-records/repo/` explaining your
provider choice. Name it `0001-use-<provider>-source.md`. Use the same table
header and section structure as the template-tier ADRs.

You also need to allowlist the new file in `.gitignore`:

```
!/docs/decision-records/repo/0001-use-<provider>-source.md
```

## Step 8: Update the Deny-All .gitignore

The `.gitignore` uses a deny-all strategy. Every file you add must have an
explicit allowlist entry. After adding files, run:

```sh
git status --short
```

Any file shown as `??` (untracked) that you intend to commit must have a
corresponding `!/<path>` line in `.gitignore`.

## Step 9: Validate Again

```sh
python tools/verify.py ci
```

The docs-layout and ADR-schema checks will confirm that your new tutorial and
ADR are in the right places and use the correct structure.

## Step 10: Push and Open a Pull Request

```sh
git add -p
git commit -m "feat: derive my-packer-framework from packer-framework-template"
git push -u origin main
gh pr create --fill
```

## What to Do Next

- Replace `examples/linux/reference-linux.pkrvars.hcl` with real OS image
  parameters.
- Add provider-specific variables to `packer/variables.pkr.hcl`.
- Follow the runner protocol in
  [`docs/reference/runner-protocol.md`](../reference/runner-protocol.md) when
  you create a runner repository that calls this framework.
