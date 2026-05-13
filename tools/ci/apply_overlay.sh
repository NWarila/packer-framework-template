#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: apply_overlay.sh <input-root> <framework-root> <overlay-paths>" >&2
}

die() {
  echo "::error::$*" >&2
  exit 1
}

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "${value}"
}

validate_relative_path() {
  local kind="$1"
  local value="$2"

  if [[ -z "${value}" ]]; then
    die "overlay ${kind} is empty"
  fi
  if [[ "${value}" == /* ]]; then
    die "overlay ${kind} must be relative: ${value}"
  fi
  if [[ "${value}" == "." || "${value}" == ".." || "${value}" == ../* || "${value}" == */../* || "${value}" == */.. ]]; then
    die "overlay ${kind} must not contain path traversal: ${value}"
  fi
}

allowed_destination() {
  local value="${1%/}"
  case "${value}" in
    packer/repos|packer/repos/*|packer/fixtures/runtime|packer/fixtures/runtime/*)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

reject_symlinks() {
  local path="$1"
  local first_link

  first_link="$(find "${path}" -type l -print -quit)"
  if [[ -n "${first_link}" ]]; then
    die "overlay source must not contain symlinks: ${first_link}"
  fi
}

if [[ "$#" -ne 3 ]]; then
  usage
  exit 2
fi

input_root="${1%/}"
framework_root="${2%/}"
overlay_paths="$3"

while IFS= read -r line; do
  entry="${line%%#*}"
  entry="$(trim "${entry}")"
  [[ -z "${entry}" ]] && continue

  if [[ "${entry}" != *"=>"* ]]; then
    die "overlay entry missing '=>' separator: ${entry}"
  fi

  src="$(trim "${entry%%=>*}")"
  dst="$(trim "${entry##*=>}")"
  validate_relative_path "source" "${src}"
  validate_relative_path "destination" "${dst}"
  if ! allowed_destination "${dst}"; then
    die "overlay destination must be under packer/repos/ or packer/fixtures/runtime/: ${dst}"
  fi

  src_path="${input_root}/${src}"
  dst_path="${framework_root}/${dst}"
  if [[ ! -e "${src_path}" && ! -L "${src_path}" ]]; then
    die "overlay source missing: ${src_path}"
  fi
  reject_symlinks "${src_path}"

  mkdir -p "${dst_path}"
  if [[ -d "${src_path}" ]]; then
    cp -a "${src_path}/." "${dst_path}/"
  else
    cp -a "${src_path}" "${dst_path}"
  fi
  echo "overlay: ${src_path} -> ${dst_path}"
done <<< "${overlay_paths}"
