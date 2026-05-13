#!/usr/bin/env python3
"""Validate Packer plugin pins against committed checksum provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKER_CONFIG = ROOT / "packer" / "packer.pkr.hcl"
PROVENANCE_FILE = ROOT / "packer" / "plugin-provenance.json"
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
PLUGIN_BLOCK_RE = re.compile(r"(?P<name>[A-Za-z0-9_-]+)\s*=\s*\{(?P<body>.*?)\n\s*\}", re.S)
ASSIGN_RE = re.compile(r'^\s*(?P<key>source|version)\s*=\s*"(?P<value>[^"]+)"\s*$', re.M)


def fail(message: str) -> None:
    raise SystemExit(f"plugin-provenance: {message}")


def parse_required_plugins(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    marker = "required_plugins"
    start = text.find(marker)
    if start == -1:
        return []
    open_brace = text.find("{", start)
    if open_brace == -1:
        fail("required_plugins block is missing an opening brace")

    depth = 0
    close_brace = -1
    for index in range(open_brace, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                close_brace = index
                break
    if close_brace == -1:
        fail("required_plugins block is not closed")

    body = text[open_brace + 1 : close_brace]
    plugins: list[dict[str, str]] = []
    for match in PLUGIN_BLOCK_RE.finditer(body):
        values = {item.group("key"): item.group("value") for item in ASSIGN_RE.finditer(match.group("body"))}
        if set(values) != {"source", "version"}:
            fail(f"required plugin {match.group('name')} must declare source and version")
        version = values["version"].strip()
        if not version.startswith("="):
            fail(f"required plugin {match.group('name')} must use an exact '= X.Y.Z' version")
        plugins.append(
            {
                "name": match.group("name"),
                "source": values["source"],
                "version": version.removeprefix("=").strip(),
            }
        )
    return plugins


def load_provenance(path: Path) -> list[dict[str, Any]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
    if not isinstance(raw, dict) or raw.get("version") != "1":
        fail("plugin-provenance.json must be an object with version '1'")
    plugins = raw.get("plugins")
    if not isinstance(plugins, list):
        fail("plugin-provenance.json must contain a plugins list")
    return plugins


def validate_checksum_table(entry: dict[str, Any]) -> None:
    checksums = entry.get("checksums")
    if not isinstance(checksums, dict) or not checksums:
        fail(f"{entry.get('source', '<unknown>')} must have non-empty checksums")
    for filename, checksum in checksums.items():
        if not isinstance(filename, str) or not filename.endswith(".zip"):
            fail(f"checksum filename must be a plugin zip: {filename!r}")
        if not isinstance(checksum, str) or not HEX64_RE.match(checksum):
            fail(f"checksum for {filename} must be a lowercase SHA256")


def parse_sha256sums(text: str) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) != 2:
            fail(f"upstream SHA256SUMS line is not '<sha256> <filename>': {line!r}")
        checksum, filename = parts
        filename = filename.removeprefix("*")
        if not HEX64_RE.match(checksum):
            fail(f"upstream checksum for {filename} must be a lowercase SHA256")
        checksums[filename] = checksum
    return checksums


def validate_upstream_checksums(entry: dict[str, Any]) -> None:
    url = entry["upstream_sha256sums_url"]
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            upstream = parse_sha256sums(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError) as exc:
        fail(f"could not fetch upstream checksums for {entry['source']}: {exc}")
    if upstream != entry["checksums"]:
        fail(f"{entry['source']} v{entry['version']} upstream checksums differ from lock")


def provenance_index(entries: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    index: dict[tuple[str, str, str], dict[str, Any]] = {}
    for entry in entries:
        for field in ("name", "source", "version", "upstream_sha256sums_url"):
            if not isinstance(entry.get(field), str) or not entry[field]:
                fail(f"plugin provenance entry missing {field}")
        validate_checksum_table(entry)
        key = (entry["name"], entry["source"], entry["version"])
        if key in index:
            fail(f"duplicate plugin provenance entry: {key}")
        index[key] = entry
    return index


def current_platform_asset(name: str, version: str) -> str:
    system = platform.system().lower()
    machine = platform.machine().lower()
    os_name = {"darwin": "darwin", "linux": "linux", "windows": "windows"}.get(system, system)
    arch = {
        "amd64": "amd64",
        "x86_64": "amd64",
        "aarch64": "arm64",
        "arm64": "arm64",
        "i386": "386",
        "i686": "386",
    }.get(machine, machine)
    return f"packer-plugin-{name}_v{version}_x5.0_{os_name}_{arch}.zip"


def default_plugin_root() -> Path:
    if platform.system().lower() == "windows":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            fail("APPDATA is not set; pass --plugin-root explicitly")
        return Path(appdata) / "packer.d" / "plugins"
    return Path.home() / ".config" / "packer" / "plugins"


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def installed_plugin_evidence(plugin_root: Path, entry: dict[str, Any]) -> dict[str, str]:
    plugin_dir = plugin_root / Path(*entry["source"].split("/"))
    pattern = f"packer-plugin-{entry['name']}_v{entry['version']}_*"
    candidates = sorted(
        path for path in plugin_dir.glob(pattern) if path.is_file() and not path.name.endswith("_SHA256SUM")
    )
    if not candidates:
        fail(f"installed plugin missing for {entry['source']} v{entry['version']} under {plugin_dir}")
    binary = candidates[0]
    sidecar = binary.with_name(f"{binary.name}_SHA256SUM")
    if not sidecar.is_file():
        fail(f"installed plugin checksum sidecar missing: {sidecar}")
    expected = sidecar.read_text(encoding="utf-8").strip().lower()
    if not HEX64_RE.match(expected):
        fail(f"installed plugin sidecar is not a SHA256: {sidecar}")
    actual = sha256_file(binary)
    if actual != expected:
        fail(f"installed plugin checksum mismatch for {binary}")
    return {
        "source": entry["source"],
        "version": entry["version"],
        "binary": str(binary),
        "binary_sha256": actual,
        "sidecar": str(sidecar),
    }


def write_evidence(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--installed", action="store_true", help="Verify installed plugin sidecars.")
    parser.add_argument(
        "--upstream",
        action="store_true",
        help="Fetch upstream SHA256SUMS files and compare them to the committed lock.",
    )
    parser.add_argument("--plugin-root", type=Path, default=None, help="Override Packer plugin root.")
    parser.add_argument("--evidence", type=Path, default=None, help="Write machine-readable evidence JSON.")
    args = parser.parse_args()

    required = parse_required_plugins(PACKER_CONFIG)
    index = provenance_index(load_provenance(PROVENANCE_FILE))
    evidence: dict[str, Any] = {
        "required_plugins": required,
        "installed_plugins": [],
        "upstream_checksums_checked": False,
    }

    for plugin in required:
        key = (plugin["name"], plugin["source"], plugin["version"])
        entry = index.get(key)
        if entry is None:
            fail(f"missing provenance for required plugin {plugin['source']} v{plugin['version']}")
        asset = current_platform_asset(plugin["name"], plugin["version"])
        if asset not in entry["checksums"]:
            fail(f"missing current-platform checksum for {asset}")
        if args.upstream:
            validate_upstream_checksums(entry)
            evidence["upstream_checksums_checked"] = True
        if args.installed:
            evidence["installed_plugins"].append(
                installed_plugin_evidence(args.plugin_root or default_plugin_root(), entry)
            )

    if args.evidence:
        write_evidence(args.evidence, evidence)
    print(f"plugin provenance validated for {len(required)} required plugin(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
