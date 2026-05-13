#!/usr/bin/env bash
set -euo pipefail

die() {
  echo "::error::$*" >&2
  exit 1
}

var_files="${1:-}"
input_prefix="${2:-../../input}"

if [[ -z "${var_files}" ]]; then
  exit 0
fi

while IFS= read -r var_file; do
  [[ -z "${var_file}" ]] && continue
  if [[ "${var_file}" == *$'\r'* ]]; then
    die "var_file entries must use LF line endings"
  fi
  if [[ "${var_file}" == /* ]]; then
    die "var_file must be relative to the input checkout: ${var_file}"
  fi
  if [[ "${var_file}" == "." || "${var_file}" == ".." || "${var_file}" == ../* || "${var_file}" == */../* || "${var_file}" == */.. ]]; then
    die "var_file must not contain path traversal: ${var_file}"
  fi

  printf '%s\n' "-var-file" "${input_prefix%/}/${var_file}"
done <<< "${var_files}"
