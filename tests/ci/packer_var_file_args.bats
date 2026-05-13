#!/usr/bin/env bats

setup() {
  repo_root="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
  script="${repo_root}/tools/ci/packer_var_file_args.sh"
}

@test "emits no arguments when var_file is empty" {
  run bash "${script}" ""

  [ "$status" -eq 0 ]
  [ -z "$output" ]
}

@test "emits var-file argument relative to input checkout" {
  run bash "${script}" "repos/public/reference.pkrvars.hcl"

  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "-var-file" ]
  [ "${lines[1]}" = "../../input/repos/public/reference.pkrvars.hcl" ]
}

@test "emits multiple var-file arguments in order" {
  run bash "${script}" $'repos/public/base.pkrvars.hcl\nrepos/public/prod.pkrvars.hcl'

  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "-var-file" ]
  [ "${lines[1]}" = "../../input/repos/public/base.pkrvars.hcl" ]
  [ "${lines[2]}" = "-var-file" ]
  [ "${lines[3]}" = "../../input/repos/public/prod.pkrvars.hcl" ]
}

@test "supports custom input prefix for callers and tests" {
  run bash "${script}" "inputs/reference.pkrvars.hcl" "../input"

  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "-var-file" ]
  [ "${lines[1]}" = "../input/inputs/reference.pkrvars.hcl" ]
}

@test "rejects absolute paths" {
  run bash "${script}" "/tmp/reference.pkrvars.hcl"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"var_file must be relative to the input checkout"* ]]
}

@test "rejects path traversal" {
  run bash "${script}" "../secrets.pkrvars.hcl"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"var_file must not contain path traversal"* ]]
}
