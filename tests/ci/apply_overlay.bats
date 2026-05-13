#!/usr/bin/env bats

setup() {
  repo_root="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
  script="${repo_root}/tools/ci/apply_overlay.sh"
  tmp_root="${BATS_TEST_TMPDIR:-$(mktemp -d)}"
  workspace="${tmp_root}/workspace"
  input="${workspace}/input"
  framework="${workspace}/framework"
  mkdir -p "${input}/repos/public" "${input}/files" "${framework}/packer"
  printf 'visible\n' > "${input}/repos/public/images.pkrvars.hcl"
  printf 'hidden\n' > "${input}/repos/public/.secret"
  printf 'single\n' > "${input}/files/one.txt"
}

@test "copies directory contents including dotfiles and skips comments" {
  run bash "${script}" "${input}" "${framework}" $'
    # copied into framework packer data
    repos/public/ => packer/repos/public/
  '

  [ "$status" -eq 0 ]
  [ -f "${framework}/packer/repos/public/images.pkrvars.hcl" ]
  [ -f "${framework}/packer/repos/public/.secret" ]
  [[ "${output}" == *"overlay: ${input}/repos/public/ -> ${framework}/packer/repos/public/"* ]]
}

@test "copies file sources into the destination directory" {
  run bash "${script}" "${input}" "${framework}" "files/one.txt=>packer/fixtures/runtime/"

  [ "$status" -eq 0 ]
  [ "$(cat "${framework}/packer/fixtures/runtime/one.txt")" = "single" ]
}

@test "rejects entries without separator" {
  run bash "${script}" "${input}" "${framework}" "repos/public/ packer/repos/public/"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"overlay entry missing '=>' separator"* ]]
}

@test "rejects missing sources" {
  run bash "${script}" "${input}" "${framework}" "repos/missing/=>packer/repos/missing/"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"overlay source missing"* ]]
}

@test "rejects symlinks in overlay sources" {
  ln -s /etc/passwd "${input}/repos/public/passwd-link"

  run bash "${script}" "${input}" "${framework}" "repos/public/=>packer/repos/public/"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"overlay source must not contain symlinks"* ]]
}

@test "rejects source path traversal" {
  run bash "${script}" "${input}" "${framework}" "../outside=>packer/repos/public/"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"overlay source must not contain path traversal"* ]]
}

@test "rejects destination path traversal" {
  run bash "${script}" "${input}" "${framework}" "repos/public/=>../outside"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"overlay destination must not contain path traversal"* ]]
}

@test "rejects workflow destinations" {
  run bash "${script}" "${input}" "${framework}" "repos/public/=>.github/workflows/"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"overlay destination must be under packer/repos/ or packer/fixtures/runtime/"* ]]
}

@test "rejects framework implementation destinations" {
  run bash "${script}" "${input}" "${framework}" "repos/public/=>packer/builds.pkr.hcl"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"overlay destination must be under packer/repos/ or packer/fixtures/runtime/"* ]]
}
