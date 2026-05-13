#!/usr/bin/env bats

setup() {
  repo_root="$(cd "${BATS_TEST_DIRNAME}/../.." && pwd)"
  script="${repo_root}/tools/ci/check_workflow_run_inputs.py"
  tmp_root="${BATS_TEST_TMPDIR:-$(mktemp -d)}"
}

@test "allows input expressions bound through env" {
  workflow="${tmp_root}/safe.yaml"
  cat > "${workflow}" <<'YAML'
name: safe
jobs:
  test:
    steps:
      - env:
          FRAMEWORK_REF: ${{ inputs.framework_ref }}
        run: |
          echo "${FRAMEWORK_REF}"
YAML

  run python "${script}" "${workflow}"

  [ "$status" -eq 0 ]
  [[ "${output}" == *"workflow run blocks do not interpolate inputs directly"* ]]
}

@test "rejects input expressions in block run scripts" {
  workflow="${tmp_root}/unsafe-block.yaml"
  cat > "${workflow}" <<'YAML'
name: unsafe
jobs:
  test:
    steps:
      - run: |
          if [[ "${{ inputs.framework_ref }}" =~ ^[0-9a-f]{40}$ ]]; then
            echo ok
          fi
YAML

  run python "${script}" "${workflow}"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"workflow run-block input interpolation is not allowed"* ]]
  [[ "${output}" == *'${{ inputs.framework_ref }}'* ]]
}

@test "rejects input expressions in inline run commands" {
  workflow="${tmp_root}/unsafe-inline.yaml"
  cat > "${workflow}" <<'YAML'
name: unsafe
jobs:
  test:
    steps:
      - run: echo "${{ inputs.framework_ref }}"
YAML

  run python "${script}" "${workflow}"

  [ "$status" -ne 0 ]
  [[ "${output}" == *"unsafe-inline.yaml:5"* ]]
}
