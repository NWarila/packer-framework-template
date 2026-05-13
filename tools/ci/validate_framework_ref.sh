#!/usr/bin/env bash
set -euo pipefail

framework_ref="${1:-}"

if [[ ! "${framework_ref}" =~ ^[0-9a-f]{40}$ ]]; then
  echo "::error::framework_ref must be a 40-character SHA, got '${framework_ref}'" >&2
  exit 1
fi
