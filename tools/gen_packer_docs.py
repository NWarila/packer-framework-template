#!/usr/bin/env python3
"""Generate stable reference docs for the Packer framework variables."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VARIABLES_FILE = ROOT / "packer" / "variables.pkr.hcl"
DOC_FILE = ROOT / "docs" / "reference" / "packer.md"
BEGIN = "<!-- BEGIN_PACKER_DOCS -->"
END = "<!-- END_PACKER_DOCS -->"
VARIABLE_RE = re.compile(r'variable\s+"(?P<name>[^"]+)"\s*\{')
ASSIGN_RE = re.compile(r"^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)$")


@dataclass(frozen=True)
class VariableDoc:
    name: str
    description: str
    type_expr: str
    default: str
    sensitive: bool


def brace_delta(value: str) -> int:
    in_string = False
    escaped = False
    delta = 0
    for char in value:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char in "({[":
            delta += 1
        elif char in ")}]":
            delta -= 1
    return delta


def find_matching_brace(text: str, open_index: int) -> int:
    depth = 0
    in_string = False
    escaped = False
    for index in range(open_index, len(text)):
        char = text[index]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unclosed variable block")


def variable_blocks(text: str) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for match in VARIABLE_RE.finditer(text):
        open_index = text.find("{", match.end() - 1)
        close_index = find_matching_brace(text, open_index)
        blocks.append((match.group("name"), text[open_index + 1 : close_index]))
    return blocks


def collect_assignment(block: str, key: str) -> str | None:
    lines = block.splitlines()
    for index, line in enumerate(lines):
        match = ASSIGN_RE.match(line)
        if match is None or match.group("key") != key:
            continue

        collected = [match.group("value").rstrip()]
        balance = brace_delta(match.group("value"))
        cursor = index + 1
        while balance > 0 and cursor < len(lines):
            next_line = lines[cursor].rstrip()
            collected.append(next_line)
            balance += brace_delta(next_line)
            cursor += 1
        return "\n".join(collected).strip()
    return None


def decode_string(value: str | None, default: str = "") -> str:
    if value is None:
        return default
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return bytes(value[1:-1], "utf-8").decode("unicode_escape")
    return value


def summarize_default(value: str | None) -> str:
    if value is None:
        return "n/a"
    single_line = " ".join(line.strip() for line in value.splitlines() if line.strip())
    if len(single_line) <= 48:
        return single_line
    return "see source default"


def normalize_type(value: str | None) -> str:
    if value is None:
        return "any"
    single_line = " ".join(line.strip() for line in value.splitlines() if line.strip())
    if len(single_line) <= 72:
        return single_line
    if single_line.startswith("map(object("):
        return "map(object(...))"
    return "complex"


def parse_variables(path: Path) -> list[VariableDoc]:
    text = path.read_text(encoding="utf-8")
    docs: list[VariableDoc] = []
    for name, block in variable_blocks(text):
        docs.append(
            VariableDoc(
                name=name,
                description=decode_string(collect_assignment(block, "description"), "n/a"),
                type_expr=normalize_type(collect_assignment(block, "type")),
                default=summarize_default(collect_assignment(block, "default")),
                sensitive=decode_string(collect_assignment(block, "sensitive"), "false") == "true",
            )
        )
    return docs


def table_cell(value: str) -> str:
    escaped = value.replace("|", "\\|")
    return f"`{escaped}`" if escaped in {"true", "false", "n/a"} else escaped


def render_docs(variables: list[VariableDoc]) -> str:
    lines = [
        BEGIN,
        "## Inputs",
        "",
        "| Name | Description | Type | Default | Sensitive |",
        "| --- | --- | --- | --- | --- |",
    ]
    for variable in variables:
        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{variable.name}`",
                    table_cell(variable.description),
                    f"`{table_cell(variable.type_expr).strip('`')}`",
                    f"`{table_cell(variable.default).strip('`')}`",
                    table_cell(str(variable.sensitive).lower()),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Generated Evidence",
            "",
            "| Path | Purpose |",
            "| --- | --- |",
            "| `packer/artifacts/<image-key>/<output_file>` | Rendered installer input for the selected image. |",
            "| `packer/artifacts/<image-key>/build-context.json` | Non-secret build metadata and secret seed fingerprint. |",
            "| `packer/artifacts/<image-key>/builder-contract.json` | Builder wiring contract for real ISO sources. |",
            "| `packer/manifests/<image-key>.json` | Packer manifest with framework custom data. |",
            END,
            "",
        ]
    )
    return "\n".join(lines)


def replace_marked_section(current: str, generated: str) -> str:
    if BEGIN not in current or END not in current:
        raise ValueError(f"{DOC_FILE} must contain {BEGIN} and {END} markers")
    before, rest = current.split(BEGIN, 1)
    _old, after = rest.split(END, 1)
    return before.rstrip() + "\n\n" + generated.rstrip() + after


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if docs are not current.")
    args = parser.parse_args()

    generated = render_docs(parse_variables(VARIABLES_FILE))
    current = DOC_FILE.read_text(encoding="utf-8")
    updated = replace_marked_section(current, generated)

    if args.check:
        if updated != current:
            print(f"{DOC_FILE.relative_to(ROOT)} is out of date; run tools/gen_packer_docs.py")
            return 1
        print("packer docs are up to date")
        return 0

    DOC_FILE.write_text(updated, encoding="utf-8", newline="\n")
    print(f"updated {DOC_FILE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
