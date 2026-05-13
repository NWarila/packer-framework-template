package repo_hygiene_test

import data.repo_hygiene
import rego.v1

git_plugin_provenance := `{
  "version": "1",
  "plugins": [
    {
      "name": "git",
      "source": "github.com/ethanmdavidson/git",
      "version": "0.6.5",
      "checksums": {}
    }
  ]
}`

# region ------ [ Workflow uses: pinning ] ------------------------------------------------- #

test_sha_pinned_action_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {"ci.yml": [{"line": 12, "uses": "actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd"}]},
		"files": {"packer/plugin-provenance.json": `{}`, "packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
}`},
	}
}

test_tag_pinned_action_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {"ci.yml": [{"line": 7, "uses": "actions/checkout@v6"}]},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
}`},
	}
	count(denials) >= 1
}

test_malformed_sha_action_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {"ci.yml": [{"line": 7, "uses": "actions/checkout@xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}]},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
}`},
	}
	count(denials) >= 1
}

test_main_branch_action_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {"ci.yml": [{"line": 3, "uses": "actions/checkout@main"}]},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
}`},
	}
	count(denials) >= 1
}

test_local_ref_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {"ci.yml": [{"line": 5, "uses": "./.github/actions/setup"}]},
		"files": {"packer/plugin-provenance.json": `{}`, "packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
}`},
	}
}

test_docker_digest_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {"ci.yml": [{"line": 9, "uses": "docker://ghcr.io/example/tool:v1.0.0@sha256:abc123"}]},
		"files": {"packer/plugin-provenance.json": `{}`, "packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
}`},
	}
}

test_docker_without_digest_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {"ci.yml": [{"line": 4, "uses": "docker://ghcr.io/example/tool:v1.0.0"}]},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
}`},
	}
	count(denials) >= 1
}

# endregion --- [ Workflow uses: pinning ] ------------------------------------------------- #

# region ------ [ pull_request_target guard ] ---------------------------------------------- #

test_pull_request_target_checkout_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {".github/workflows/auto-merge.yaml": `on:
  pull_request_target:
    types: [opened]
jobs:
  dangerous:
    steps:
      - uses: actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd`},
	}
	count(denials) >= 1
}

test_release_workflow_pull_request_target_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {".github/workflows/release.yaml": `on:
  pull_request_target:
  workflow_dispatch:`},
	}
	count(denials) >= 1
}

test_pr_validation_pull_request_target_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {".github/workflows/pr-validation.yaml": `on:
  pull_request_target:
jobs: {}`},
	}
	count(denials) >= 1
}

test_release_workflow_release_trigger_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {},
		"files": {".github/workflows/release.yaml": `on:
  push:
    branches: [main]
  release:
    types: [published]
  workflow_dispatch:`},
	}
}

test_auto_merge_reusable_pr_head_ref_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {".github/workflows/reusable-auto-merge.yaml": `jobs:
  enable-auto-merge:
    steps:
      - run: echo "${{ github.event.pull_request.head.sha }}"`},
	}
	count(denials) >= 1
}

test_auto_merge_reusable_payload_metadata_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {},
		"files": {".github/workflows/reusable-auto-merge.yaml": `jobs:
  enable-auto-merge:
    steps:
      - env:
          PR_AUTHOR: ${{ github.event.pull_request.user.login }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: |
          declare -a trusted_authors=("renovate[bot]" "dependabot[bot]")
          gh pr merge "${PR_NUMBER}" --repo "${{ github.repository }}" --auto --squash`},
	}
}

# endregion --- [ pull_request_target guard ] ---------------------------------------------- #

# region ------ [ packer/packer.pkr.hcl required_version pinning ] ------------------------- #

test_missing_packer_config_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {},
		"files": {},
	}
}

test_missing_required_version_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"packer/packer.pkr.hcl": `packer { }`},
	}
	count(denials) >= 1
}

test_missing_plugin_provenance_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
  required_plugins {
    git = {
      source  = "github.com/ethanmdavidson/git"
      version = "= 0.6.5"
    }
  }
}`},
	}
	count(denials) >= 1
}

test_required_version_comment_spoof_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"packer/packer.pkr.hcl": `packer {
  # required_version = "= 1.15.0"
  required_version = ">= 1.15.0"
}`},
	}
	count(denials) >= 1
}

test_pessimistic_operator_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "~> 1.15"
}`},
	}
	count(denials) >= 1
}

# endregion --- [ packer/packer.pkr.hcl required_version pinning ] ------------------------- #

# region ------ [ Plugin version pinning ] ------------------------------------------------- #

test_exact_plugin_pin_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {},
		"files": {
			"packer/plugin-provenance.json": git_plugin_provenance,
			"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
  required_plugins {
    git = {
      source  = "github.com/ethanmdavidson/git"
      version = "= 0.6.5"
    }
  }
}`},
	}
}

test_plugin_pin_version_before_source_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {},
		"files": {
			"packer/plugin-provenance.json": git_plugin_provenance,
			"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
  required_plugins {
    git = {
      version = "= 0.6.5"
      source  = "github.com/ethanmdavidson/git"
    }
  }
}`},
	}
}

test_plugin_missing_from_provenance_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {
			"packer/plugin-provenance.json": `{"version":"1","plugins":[]}`,
			"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
  required_plugins {
    git = {
      source  = "github.com/ethanmdavidson/git"
      version = "= 0.6.5"
    }
  }
}`},
	}
	count(denials) >= 1
}

test_plugin_range_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
  required_plugins {
    git = {
      source  = "github.com/ethanmdavidson/git"
      version = ">= 0.6.0"
    }
  }
}`},
	}
	count(denials) >= 1
}

test_provider_unprefixed_version_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "= 1.15.0"
  required_plugins {
    git = {
      source  = "github.com/ethanmdavidson/git"
      version = "0.6.5"
    }
  }
}`},
	}
	count(denials) >= 1
}

# endregion --- [ Plugin version pinning ] ------------------------------------------------- #
