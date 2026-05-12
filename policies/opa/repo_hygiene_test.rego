package repo_hygiene_test

import data.repo_hygiene
import rego.v1

test_sha_pinned_action_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {"ci.yml": [{"line": 12, "uses": "actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd"}]},
		"files": {"packer/packer.pkr.hcl": `packer {
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

test_local_ref_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
		"workflows": {"ci.yml": [{"line": 5, "uses": "./.github/actions/setup"}]},
		"files": {"packer/packer.pkr.hcl": `packer {
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

test_pessimistic_operator_denied if {
	denials := repo_hygiene.deny with input as {
		"workflows": {},
		"files": {"packer/packer.pkr.hcl": `packer {
  required_version = "~> 1.15"
}`},
	}
	count(denials) >= 1
}

test_exact_plugin_pin_allowed if {
	count(repo_hygiene.deny) == 0 with input as {
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
