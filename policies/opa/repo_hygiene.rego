# repo_hygiene - repository hygiene policy for Packer-framework repos.
#
# Encodes repository-level invariants visible from source files: workflow
# `uses:` SHA-pinning, privileged-trigger boundaries, exact Packer
# required_version pins, and exact `=` operator on plugin versions.
# Generated build/manifest policy belongs in package packer_artifact.
#
# Rules trace to:
#   - template-tier ADR-template/0001 in this Packer template ("Pin Packer
#     and Plugin Versions Exactly") for exact Packer/plugin pins.
#   - org ADR-0004 "SHA-pin retention check" for workflow-level SHA pins.
#
# Input shape (assembled by tools/build_opa_input.py):
#   {
#     "workflows": {
#       "<filename>": [
#         {"line": <int>, "uses": "<ref>"},
#         ...
#       ]
#     },
#     "files": { "<path>": "<contents>" }  # includes workflow files
#   }

package repo_hygiene

import rego.v1

# region ------ [ Regex constants ] -------------------------------------------------------- #

sha_re := `^[0-9a-f]{40}$`
exact_packer_required_version_re := `^\s*required_version\s*=\s*"=\s*[0-9]+\.[0-9]+\.[0-9]+"\s*$`
plugin_version_line_re := `^\s*version\s*=\s*"[^"]+"\s*$`
exact_plugin_version_line_re := `^\s*version\s*=\s*"=\s*[0-9]+\.[0-9]+\.[0-9]+"\s*$`
# Lightweight HCL shape check for simple required_plugins blocks. The Python
# provenance checker remains the authoritative parser for complex cases.
required_plugin_source_first_re := `([A-Za-z0-9_-]+)\s*=\s*\{[^}]*source\s*=\s*"([^"]+)"[^}]*version\s*=\s*"=\s*([0-9]+\.[0-9]+\.[0-9]+)"[^}]*\}`
required_plugin_version_first_re := `([A-Za-z0-9_-]+)\s*=\s*\{[^}]*version\s*=\s*"=\s*([0-9]+\.[0-9]+\.[0-9]+)"[^}]*source\s*=\s*"([^"]+)"[^}]*\}`

unsafe_pr_target_ref_fragments := {
	"uses: actions/checkout@",
	"github.event.pull_request.head",
	"github.event.pull_request.title",
	"github.event.pull_request.body",
	"github.event.pull_request.commits_url",
	"github.event.pull_request.diff_url",
	"github.event.pull_request.patch_url",
	"github.head_ref",
	"gh pr checkout",
	"gh pr diff",
	"gh pr view",
	"git checkout",
	"git fetch",
	"git switch",
}

pull_request_target_allowed_workflows := {
	".github/workflows/auto-merge.yaml",
}

auto_merge_reusable := ".github/workflows/reusable-auto-merge.yaml"

# endregion --- [ Regex constants ] -------------------------------------------------------- #

# region ------ [ Workflow uses: pinning predicates ] -------------------------------------- #

is_local_ref(ref) if startswith(ref, "./")

is_docker_digest(ref) if {
	startswith(ref, "docker://")
	contains(ref, "@sha256:")
}

is_sha_pinned(ref) if {
	not is_local_ref(ref)
	not startswith(ref, "docker://")
	contains(ref, "@")
	parts := split(ref, "@")
	count(parts) == 2
	regex.match(sha_re, parts[1])
}

is_acceptable(ref) if is_sha_pinned(ref)
is_acceptable(ref) if is_local_ref(ref)
is_acceptable(ref) if is_docker_digest(ref)

# endregion --- [ Workflow uses: pinning predicates ] -------------------------------------- #

# region ------ [ Helpers ] ---------------------------------------------------------------- #

uncommented_lines(path) := lines if {
	content := input.files[path]
	lines := [trim_space(line) |
		line := split(content, "\n")[_]
		trim_space(line) != ""
		not startswith(trim_space(line), "#")
		not startswith(trim_space(line), "//")
	]
}

uncommented_line_records(path) := records if {
	content := input.files[path]
	raw_lines := split(content, "\n")
	records := [{"line": idx + 1, "text": text} |
		some idx
		raw := raw_lines[idx]
		text := trim_space(raw)
		text != ""
		not startswith(text, "#")
		not startswith(text, "//")
	]
}

workflow_file(path) if startswith(path, ".github/workflows/")

has_pull_request_target_trigger(path) if {
	workflow_file(path)
	record := uncommented_line_records(path)[_]
	regex.match(`^pull_request_target\s*:`, record.text)
}

protected_pull_request_target_workflow(path) if has_pull_request_target_trigger(path)

protected_pull_request_target_workflow(path) if {
	path == auto_merge_reusable
	_ := input.files[path]
}

has_packer_config if {
	_ := input.files["packer/packer.pkr.hcl"]
}

has_plugin_provenance if {
	_ := input.files["packer/plugin-provenance.json"]
}

required_plugin_entries contains entry if {
	content := input.files["packer/packer.pkr.hcl"]
	matches := regex.find_all_string_submatch_n(required_plugin_source_first_re, content, -1)
	match := matches[_]
	entry := {
		"name": match[1],
		"source": match[2],
		"version": match[3],
	}
}

required_plugin_entries contains entry if {
	content := input.files["packer/packer.pkr.hcl"]
	matches := regex.find_all_string_submatch_n(required_plugin_version_first_re, content, -1)
	match := matches[_]
	entry := {
		"name": match[1],
		"source": match[3],
		"version": match[2],
	}
}

plugin_provenance_entries contains entry if {
	raw := input.files["packer/plugin-provenance.json"]
	parsed := json.unmarshal(raw)
	plugin := object.get(parsed, "plugins", [])[_]
	entry := {
		"name": object.get(plugin, "name", ""),
		"source": object.get(plugin, "source", ""),
		"version": object.get(plugin, "version", ""),
	}
}

plugin_provenance_covers(required) if {
	provenance := plugin_provenance_entries[_]
	provenance.name == required.name
	provenance.source == required.source
	provenance.version == required.version
}

has_exact_packer_required_version if {
	line := uncommented_lines("packer/packer.pkr.hcl")[_]
	regex.match(exact_packer_required_version_re, line)
}

# endregion --- [ Helpers ] ---------------------------------------------------------------- #

# region ------ [ Deny rules: workflow uses: pinning ] ------------------------------------- #

deny contains msg if {
	some workflow, _ in input.workflows
	use := input.workflows[workflow][_]
	not is_acceptable(use.uses)
	msg := sprintf(
		"%s:%d - `uses: %s` is not SHA-pinned; replace `@<tag>` with `@<40-char-sha>`",
		[workflow, use.line, use.uses],
	)
}

# endregion --- [ Deny rules: workflow uses: pinning ] ------------------------------------- #

# region ------ [ Deny rules: pull_request_target guard ] ---------------------------------- #

deny contains msg if {
	some path
	_ := input.files[path]
	has_pull_request_target_trigger(path)
	not pull_request_target_allowed_workflows[path]
	msg := sprintf("%s must not use pull_request_target; only auto-merge.yaml is allowed to run in that context", [path])
}

deny contains msg if {
	some path
	_ := input.files[path]
	protected_pull_request_target_workflow(path)
	record := uncommented_line_records(path)[_]
	line := lower(record.text)
	fragment := unsafe_pr_target_ref_fragments[_]
	contains(line, fragment)
	msg := sprintf(
		"%s:%d - pull_request_target auto-merge guard forbids PR-controlled content reads: %s",
		[path, record.line, fragment],
	)
}

# endregion --- [ Deny rules: pull_request_target guard ] ---------------------------------- #

# region ------ [ Deny rules: packer/packer.pkr.hcl content ] ------------------------------ #

deny contains msg if {
	has_packer_config
	not has_exact_packer_required_version
	msg := "packer/packer.pkr.hcl must pin required_version with `= X.Y.Z` (template-tier ADR-template/0001)"
}

deny contains msg if {
	has_packer_config
	not has_plugin_provenance
	msg := "packer/plugin-provenance.json must track checksum provenance for required Packer plugins"
}

deny contains msg if {
	has_packer_config
	has_plugin_provenance
	required := required_plugin_entries[_]
	not plugin_provenance_covers(required)
	msg := sprintf("packer/plugin-provenance.json must include %s %s v%s", [required.name, required.source, required.version])
}

deny contains msg if {
	has_packer_config
	line := uncommented_lines("packer/packer.pkr.hcl")[_]
	contains(line, "~>")
	msg := "packer/packer.pkr.hcl must not use `~>`; Packer and plugin versions require exact `=` pins (template-tier ADR-template/0001)"
}

deny contains msg if {
	has_packer_config
	line := uncommented_lines("packer/packer.pkr.hcl")[_]
	regex.match(plugin_version_line_re, line)
	not regex.match(exact_plugin_version_line_re, line)
	msg := sprintf("packer/packer.pkr.hcl plugin version must use exact `= X.Y.Z` pin: %s", [line])
}

# endregion --- [ Deny rules: packer/packer.pkr.hcl content ] ------------------------------ #
