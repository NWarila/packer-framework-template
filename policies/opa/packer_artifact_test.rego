package packer_artifact_test

import data.packer_artifact
import rego.v1

safe_input := {
	"manifests": [
		{
			"path": "packer/manifests/reference-linux.json",
			"builds": [{
				"custom_data": {
					"image_key": "reference-linux",
					"os_family": "linux",
					"os_name": "reference-linux",
					"os_version": "0.1.0",
					"architecture": "x86_64",
					"owner": "platform",
					"secret_seed_id": "6d0f846348a85632",
				},
			}],
		},
	],
	"rendered_templates": [
		{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "#cloud-config\nusers:\n  - name: platform\n    lock_passwd: true\n",
		},
		{
			"path": "packer/artifacts/reference-linux/builder-contract.json",
			"content": `{"image_key":"reference-linux","http_directory":"packer/artifacts/reference-linux","cd_files":["packer/artifacts/reference-linux/user-data"]}`,
		},
	],
}

test_safe_artifacts_allowed if {
	count(packer_artifact.deny) == 0 with input as safe_input
}

test_manifest_required if {
	denials := packer_artifact.deny with input as {
		"manifests": [],
		"rendered_templates": [],
	}
	count(denials) >= 1
}

test_empty_builds_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": [{"path": "packer/manifests/empty.json", "builds": []}],
		"rendered_templates": [],
	}
	count(denials) >= 1
}

test_missing_manifest_custom_data_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": [{
			"path": "packer/manifests/bad.json",
			"builds": [{"custom_data": {"image_key": "bad"}}],
		}],
		"rendered_templates": [],
	}
	count(denials) >= 1
}

test_raw_secret_seed_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": [{
			"path": "packer/manifests/bad.json",
			"builds": [{
				"custom_data": {
					"image_key": "bad",
					"os_family": "linux",
					"os_name": "bad",
					"os_version": "0.1.0",
					"architecture": "x86_64",
					"owner": "platform",
					"secret_seed_id": "reference-only",
				},
			}],
		}],
		"rendered_templates": [],
	}
	count(denials) >= 1
}

test_non_fingerprint_secret_seed_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": [{
			"path": "packer/manifests/bad.json",
			"builds": [{
				"custom_data": {
					"image_key": "bad",
					"os_family": "linux",
					"os_name": "bad",
					"os_version": "0.1.0",
					"architecture": "x86_64",
					"owner": "platform",
					"secret_seed_id": "not-a-fingerprint",
				},
			}],
		}],
		"rendered_templates": [],
	}
	count(denials) >= 1
}

test_missing_builder_contract_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "#cloud-config\nusers:\n  - lock_passwd: true\n",
		}],
	}
	count(denials) >= 1
}

test_builder_contract_without_cd_files_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [
			{
				"path": "packer/artifacts/reference-linux/user-data",
				"content": "#cloud-config\nusers:\n  - lock_passwd: true\n",
			},
			{
				"path": "packer/artifacts/reference-linux/builder-contract.json",
				"content": `{"image_key":"reference-linux","http_directory":"packer/artifacts/reference-linux","cd_files":[]}`,
			},
		],
	}
	count(denials) >= 1
}

test_missing_rendered_installer_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/builder-contract.json",
			"content": `{"image_key":"reference-linux","http_directory":"packer/artifacts/reference-linux","cd_files":["packer/artifacts/reference-linux/user-data"]}`,
		}],
	}
	count(denials) >= 1
}

test_large_disk_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": [{
			"path": "packer/manifests/bad.json",
			"builds": [{
				"custom_data": {
					"image_key": "bad",
					"os_family": "linux",
					"os_name": "bad",
					"os_version": "0.1.0",
					"architecture": "x86_64",
					"owner": "platform",
					"secret_seed_id": "6d0f846348a85632",
					"disk_size_gb": "100",
				},
			}],
		}],
		"rendered_templates": [],
	}
	count(denials) >= 1
}

test_unsigned_post_processor_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": [{
			"path": "packer/manifests/bad.json",
			"builds": [{
				"custom_data": {
					"image_key": "bad",
					"os_family": "linux",
					"os_name": "bad",
					"os_version": "0.1.0",
					"architecture": "x86_64",
					"owner": "platform",
					"secret_seed_id": "6d0f846348a85632",
					"post_processor_signed": "false",
				},
			}],
		}],
		"rendered_templates": [],
	}
	count(denials) >= 1
}

test_private_key_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "-----BEGIN OPENSSH PRIVATE KEY-----\n",
		}],
	}
	count(denials) >= 1
}

test_lock_passwd_false_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "#cloud-config\nusers:\n  - lock_passwd: false\n",
		}],
	}
	count(denials) >= 1
}

test_missing_lock_passwd_true_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "#cloud-config\nusers:\n  - name: platform\n",
		}],
	}
	count(denials) >= 1
}

test_string_form_non_default_user_denied_with_dict_form_message if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [
			{
				"path": "packer/artifacts/reference-linux/user-data",
				"content": "#cloud-config\nusers:\n  - someone\n",
			},
			{
				"path": "packer/artifacts/reference-linux/builder-contract.json",
				"content": `{"image_key":"reference-linux","http_directory":"packer/artifacts/reference-linux","cd_files":["packer/artifacts/reference-linux/user-data"]}`,
			},
		],
	}
	msg := denials[_]
	msg == `packer/artifacts/reference-linux/user-data cloud-init users must use dict form (string user "someone" cannot set lock_passwd)`
}

test_cloud_init_without_users_allowed if {
	count(packer_artifact.deny) == 0 with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [
			{
				"path": "packer/artifacts/reference-linux/user-data",
				"content": "#cloud-config\npackage_update: true\nruncmd:\n  - systemctl enable docker\n",
			},
			{
				"path": "packer/artifacts/reference-linux/builder-contract.json",
				"content": `{"image_key":"reference-linux","http_directory":"packer/artifacts/reference-linux","cd_files":["packer/artifacts/reference-linux/user-data"]}`,
			},
		],
	}
}

test_cloud_init_with_users_missing_lock_passwd_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "#cloud-config\nusers:\n  - name: platform\n    shell: /bin/bash\n",
		}],
	}
	count(denials) >= 1
}

test_non_sensitive_world_readable_write_files_allowed if {
	count(packer_artifact.deny) == 0 with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [
			{
				"path": "packer/artifacts/reference-linux/user-data",
				"content": "#cloud-config\nusers:\n  - name: platform\n    lock_passwd: true\nwrite_files:\n  - path: /etc/hostname\n    permissions: \"0644\"\n",
			},
			{
				"path": "packer/artifacts/reference-linux/builder-contract.json",
				"content": `{"image_key":"reference-linux","http_directory":"packer/artifacts/reference-linux","cd_files":["packer/artifacts/reference-linux/user-data"]}`,
			},
		],
	}
}

test_sensitive_world_readable_write_files_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "#cloud-config\nusers:\n  - lock_passwd: true\nwrite_files:\n  - path: /etc/credentials.json\n    permissions: \"0644\"\n",
		}],
	}
	count(denials) >= 1
}

test_world_writable_write_files_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "#cloud-config\nusers:\n  - lock_passwd: true\nwrite_files:\n  - path: /tmp/x\n    permissions: \"0777\"\n",
		}],
	}
	count(denials) >= 1
}

test_embedded_token_denied if {
	denials := packer_artifact.deny with input as {
		"manifests": safe_input.manifests,
		"rendered_templates": [{
			"path": "packer/artifacts/reference-linux/user-data",
			"content": "#cloud-config\ntoken: ghp_bad\n",
		}],
	}
	count(denials) >= 1
}
