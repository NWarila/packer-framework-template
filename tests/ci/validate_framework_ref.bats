#!/usr/bin/env bats

setup() {
  repo_root="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
  script="${repo_root}/tools/ci/validate_framework_ref.sh"
}

@test "accepts a lowercase 40-character commit SHA" {
  run bash "${script}" "03e544535d10a71645edca34257f0175d1f15960"

  [ "$status" -eq 0 ]
}

@test "rejects tags" {
  run bash "${script}" "v1.2.3"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"framework_ref must be a 40-character SHA"* ]]
}

@test "rejects short SHAs" {
  run bash "${script}" "03e5445"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"framework_ref must be a 40-character SHA"* ]]
}

@test "rejects uppercase SHAs to match workflow policy" {
  run bash "${script}" "03E544535D10A71645EDCA34257F0175D1F15960"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"framework_ref must be a 40-character SHA"* ]]
}
