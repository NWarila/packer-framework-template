#!/usr/bin/env bash
set -euo pipefail

input_ref="${1:-}"
allow_floating="${2:-false}"

case "${allow_floating}" in
  true|false) ;;
  *)
    echo "::error::allow_floating_input_ref must be true or false, got '${allow_floating}'" >&2
    exit 1
    ;;
esac

if [[ "${allow_floating}" == "true" ]]; then
  if [[ -z "${input_ref}" ]]; then
    echo "::error::input_ref must not be empty when floating refs are allowed" >&2
    exit 1
  fi
  exit 0
fi

if [[ ! "${input_ref}" =~ ^[0-9a-f]{40}$ ]]; then
  echo "::error::input_ref must be a 40-character SHA, got '${input_ref}'" >&2
  exit 1
fi
