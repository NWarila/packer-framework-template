# packer_artifact - build-aware policy for generated Packer evidence.
#
# This package consumes normalized release/build evidence assembled by
# tools/build_packer_artifact_input.py:
#
#   {
#     "manifests": [
#       {"path": "packer/manifests/reference-linux.json", "builds": [...]}
#     ],
#     "rendered_templates": [
#       {"path": "packer/artifacts/reference-linux/user-data", "content": "..."}
#     ]
#   }
#
# The rules complement repo_hygiene. Static source policy can prove exact pins
# and workflow boundaries; this package checks generated manifests and
# rendered installer content for obvious unsafe patterns.

package packer_artifact

import rego.v1

# region ------ [ Constants ] -------------------------------------------------------------- #

required_custom_data := [
	"image_key",
	"os_family",
	"os_name",
	"os_version",
	"architecture",
	"owner",
	"secret_seed_id",
]

credential_markers := [
	"api_key:",
	"client_secret:",
	"password:",
	"secret:",
	"token:",
]

private_key_markers := [
	"-----begin openssh private key-----",
	"-----begin rsa private key-----",
	"-----begin ec private key-----",
]

world_writable_write_file_modes := {"0666", "0777"}

sensitive_world_readable_write_file_modes := {"0644", "0664"}

# endregion --- [ Constants ] -------------------------------------------------------------- #

# region ------ [ Helpers ] ---------------------------------------------------------------- #

builds(manifest) := result if {
	result := object.get(manifest, "builds", [])
}

custom_data(build) := result if {
	result := object.get(build, "custom_data", {})
}

missing_custom_data(build) := missing if {
	custom := custom_data(build)
	missing := {key |
		key := required_custom_data[_]
		object.get(custom, key, "") == ""
	}
}

disk_size_gb(custom) := size if {
	raw := object.get(custom, "disk_size_gb", 0)
	is_number(raw)
	size := raw
}

disk_size_gb(custom) := size if {
	raw := object.get(custom, "disk_size_gb", "")
	is_string(raw)
	regex.match(`^[0-9]+$`, raw)
	size := to_number(raw)
}

template_content(template) := lower(object.get(template, "content", ""))

write_file_entry(content) := entry if {
	startswith(content, "#cloud-config")
	config := yaml.unmarshal(content)
	entries := object.get(config, "write_files", [])
	entry := entries[_]
}

cloud_config_users(content) := users if {
	startswith(content, "#cloud-config")
	config := yaml.unmarshal(content)
	users := object.get(config, "users", [])
}

permission_mode(raw) := mode if {
	stripped := trim(sprintf("%v", [raw]), `"'`)
	regex.match(`^[0-9]{3}$`, stripped)
	mode := sprintf("0%s", [stripped])
}

permission_mode(raw) := mode if {
	stripped := trim(sprintf("%v", [raw]), `"'`)
	regex.match(`^[0-9]{4}$`, stripped)
	mode := stripped
}

world_writable_mode_in_content(content) if {
	regex.match(`(?m)^\s*permissions:\s*['"]?0?(666|777)['"]?\s*$`, content)
}

sensitive_write_file_path(path) if {
	lower_path := lower(path)
	regex.match(`(^|.*/)([^/]*\.(key|pem)|.*-secrets\.ya?ml|.*credentials.*)$`, lower_path)
}

sensitive_write_file_path(path) if {
	contains(lower(path), "/secrets/")
}

manifest_image_key(build) := image_key if {
	image_key := object.get(custom_data(build), "image_key", "")
	image_key != ""
}

builder_contract_for(image_key) := contract if {
	template := input.rendered_templates[_]
	template.path == sprintf("packer/artifacts/%s/builder-contract.json", [image_key])
	contract := json.unmarshal(object.get(template, "content", "{}"))
}

valid_builder_contract(image_key) if {
	contract := builder_contract_for(image_key)
	object.get(contract, "image_key", "") == image_key
	object.get(contract, "http_directory", "") != ""
	cd_files := object.get(contract, "cd_files", [])
	is_array(cd_files)
	count(cd_files) > 0
}

rendered_installer_for(image_key) if {
	template := input.rendered_templates[_]
	startswith(template.path, sprintf("packer/artifacts/%s/", [image_key]))
	not endswith(template.path, "/builder-contract.json")
}

# endregion --- [ Helpers ] ---------------------------------------------------------------- #

# region ------ [ Deny rules: manifest structure ] ---------------------------------------- #

deny contains msg if {
	count(input.manifests) == 0
	msg := "Packer artifact policy requires at least one generated manifest"
}

deny contains msg if {
	manifest := input.manifests[_]
	count(builds(manifest)) == 0
	msg := sprintf("%s must contain at least one build", [manifest.path])
}

deny contains msg if {
	manifest := input.manifests[_]
	build := builds(manifest)[_]
	missing := missing_custom_data(build)
	count(missing) > 0
	msg := sprintf("%s build custom_data missing required keys: %v", [manifest.path, sort(missing)])
}

deny contains msg if {
	manifest := input.manifests[_]
	build := builds(manifest)[_]
	custom := custom_data(build)
	secret_seed_id := object.get(custom, "secret_seed_id", "")
	not regex.match(`^[0-9a-f]{16}$`, secret_seed_id)
	msg := sprintf("%s must expose secret_seed_id only as a 16-character hex fingerprint", [manifest.path])
}

deny contains msg if {
	manifest := input.manifests[_]
	build := builds(manifest)[_]
	image_key := manifest_image_key(build)
	not valid_builder_contract(image_key)
	msg := sprintf("%s image %s must have a valid builder-contract.json with http_directory and cd_files", [manifest.path, image_key])
}

deny contains msg if {
	manifest := input.manifests[_]
	build := builds(manifest)[_]
	image_key := manifest_image_key(build)
	not rendered_installer_for(image_key)
	msg := sprintf("%s image %s must have a rendered installer artifact", [manifest.path, image_key])
}

# endregion --- [ Deny rules: manifest structure ] ---------------------------------------- #

# region ------ [ Deny rules: unsafe generated build data ] -------------------------------- #

deny contains msg if {
	manifest := input.manifests[_]
	build := builds(manifest)[_]
	custom := custom_data(build)
	disk_size_gb(custom) > 50
	msg := sprintf("%s build disk_size_gb must not exceed 50 in the reference framework", [manifest.path])
}

deny contains msg if {
	manifest := input.manifests[_]
	build := builds(manifest)[_]
	custom := custom_data(build)
	lower(object.get(custom, "post_processor_signed", "true")) == "false"
	msg := sprintf("%s build must not declare unsigned post-processors", [manifest.path])
}

deny contains msg if {
	manifest := input.manifests[_]
	build := builds(manifest)[_]
	custom := custom_data(build)
	lower(object.get(custom, "unsigned_post_processor", "false")) == "true"
	msg := sprintf("%s build must not declare unsigned post-processors", [manifest.path])
}

# endregion --- [ Deny rules: unsafe generated build data ] -------------------------------- #

# region ------ [ Deny rules: rendered installer content ] --------------------------------- #

deny contains msg if {
	template := input.rendered_templates[_]
	content := template_content(template)
	marker := private_key_markers[_]
	contains(content, marker)
	msg := sprintf("%s must not embed private keys", [template.path])
}

deny contains msg if {
	template := input.rendered_templates[_]
	content := template_content(template)
	contains(content, "ssh-rsa aaa")
	msg := sprintf("%s must not embed legacy ssh-rsa authorized keys", [template.path])
}

deny contains msg if {
	template := input.rendered_templates[_]
	content := template_content(template)
	contains(content, "lock_passwd: false")
	msg := sprintf("%s cloud-init users must keep lock_passwd: true", [template.path])
}

deny contains msg if {
	template := input.rendered_templates[_]
	content := template_content(template)
	users := cloud_config_users(content)
	user := users[_]
	is_object(user)
	object.get(user, "lock_passwd", false) != true
	msg := sprintf("%s cloud-init users must set lock_passwd: true", [template.path])
}

deny contains msg if {
	template := input.rendered_templates[_]
	content := template_content(template)
	users := cloud_config_users(content)
	user := users[_]
	is_string(user)
	user != "default"
	msg := sprintf("%s cloud-init users must use dict form (string user %q cannot set lock_passwd)", [template.path, user])
}

deny contains msg if {
	template := input.rendered_templates[_]
	content := template_content(template)
	world_writable_mode_in_content(content)
	msg := sprintf("%s cloud-init write_files must not be world-writable", [template.path])
}

deny contains msg if {
	template := input.rendered_templates[_]
	content := template_content(template)
	entry := write_file_entry(content)
	mode := permission_mode(object.get(entry, "permissions", ""))
	sensitive_world_readable_write_file_modes[mode]
	path := object.get(entry, "path", "")
	sensitive_write_file_path(path)
	msg := sprintf("%s cloud-init write_files must not make sensitive path %s world-readable", [template.path, path])
}

deny contains msg if {
	template := input.rendered_templates[_]
	content := template_content(template)
	marker := credential_markers[_]
	contains(content, marker)
	not contains(content, "reference-only")
	not contains(content, "replace_with")
	not contains(content, "change_me")
	msg := sprintf("%s must not embed apparent credentials: %s", [template.path, marker])
}

# endregion --- [ Deny rules: rendered installer content ] --------------------------------- #
