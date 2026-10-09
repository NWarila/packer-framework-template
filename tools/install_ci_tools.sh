#!/usr/bin/env bash
# Install pinned CI tools (actionlint, Packer, and OPA) on a Linux x86_64 runner.
#
# Each downloaded binary is verified against the checksum file published by
# the upstream release. This catches mirror/transport tampering while keeping
# the release source of trust explicit.

set -euo pipefail

require_var() {
  local name="$1"
  local value="${!name:-}"
  if [ -z "$value" ]; then
    echo "error: required env var $name is not set" >&2
    exit 2
  fi
}

verify_sha256() {
  local file="$1"
  local expected="$2"
  local actual
  actual="$(sha256sum "$file" | awk '{print $1}')"
  if [ "$actual" != "$expected" ]; then
    echo "error: sha256 mismatch for $file" >&2
    echo "  expected: $expected" >&2
    echo "  actual:   $actual" >&2
    exit 1
  fi
}

fetch_url() {
  local output="$1"
  local url="$2"

  curl --fail --silent --show-error --location \
    --retry 5 --retry-all-errors --retry-delay 2 --connect-timeout 20 \
    -o "$output" "$url"
}

install_packer() {
  local v="$PACKER_VERSION"
  local zip="packer_${v}_linux_amd64.zip"
  local sums="packer_${v}_SHA256SUMS"
  local base="https://releases.hashicorp.com/packer/${v}"

  fetch_url "${workdir}/${zip}" "${base}/${zip}"
  fetch_url "${workdir}/${sums}" "${base}/${sums}"

  local expected
  expected="$(awk -v f="${zip}" '$2 == f {print $1}' "${workdir}/${sums}")"
  if [ -z "$expected" ]; then
    echo "error: ${zip} not found in ${sums}" >&2
    exit 1
  fi

  verify_sha256 "${workdir}/${zip}" "$expected"
  unzip -q -o "${workdir}/${zip}" -d "${workdir}/packer"
  install -m 0755 "${workdir}/packer/packer" "${bindir}/packer"
  "${bindir}/packer" version
}

install_opa() {
  local v="$OPA_VERSION"
  local bin="opa_linux_amd64_static"
  local base="https://github.com/open-policy-agent/opa/releases/download/v${v}"

  fetch_url "${workdir}/${bin}" "${base}/${bin}"
  fetch_url "${workdir}/${bin}.sha256" "${base}/${bin}.sha256"

  local expected
  expected="$(awk '{print $1}' "${workdir}/${bin}.sha256")"
  if [ -z "$expected" ]; then
    echo "error: OPA sha256 file is empty" >&2
    exit 1
  fi

  verify_sha256 "${workdir}/${bin}" "$expected"
  install -m 0755 "${workdir}/${bin}" "${bindir}/opa"
  "${bindir}/opa" version
}

install_actionlint() {
  local v="$ACTIONLINT_VERSION"
  local tar="actionlint_${v}_linux_amd64.tar.gz"
  local sums="actionlint_${v}_checksums.txt"
  local base="https://github.com/rhysd/actionlint/releases/download/v${v}"

  fetch_url "${workdir}/${tar}" "${base}/${tar}"
  fetch_url "${workdir}/${sums}" "${base}/${sums}"

  local expected
  expected="$(awk -v f="${tar}" '$2 == f {print $1}' "${workdir}/${sums}")"
  if [ -z "$expected" ]; then
    echo "error: ${tar} not found in ${sums}" >&2
    exit 1
  fi

  verify_sha256 "${workdir}/${tar}" "$expected"
  mkdir -p "${workdir}/actionlint"
  tar -xzf "${workdir}/${tar}" -C "${workdir}/actionlint"
  install -m 0755 "${workdir}/actionlint/actionlint" "${bindir}/actionlint"
  "${bindir}/actionlint" -version
}

install_markdownlint_cli2() {
  local v="$MARKDOWNLINT_CLI2_VERSION"
  local prefix="${HOME}/.local/markdownlint-cli2"

  mkdir -p "$prefix"
  npm install --silent --no-audit --no-fund --prefix "$prefix" "markdownlint-cli2@${v}"
  ln -sf "${prefix}/node_modules/.bin/markdownlint-cli2" "${bindir}/markdownlint-cli2"
  "${bindir}/markdownlint-cli2" --version
}

require_var ACTIONLINT_VERSION
require_var MARKDOWNLINT_CLI2_VERSION
require_var PACKER_VERSION
require_var OPA_VERSION

bindir="${HOME}/.local/bin"
mkdir -p "$bindir"
if [ -n "${GITHUB_PATH:-}" ]; then
  echo "$bindir" >> "$GITHUB_PATH"
else
  export PATH="${bindir}:$PATH"
fi

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT

install_actionlint
install_markdownlint_cli2
install_packer
install_opa
