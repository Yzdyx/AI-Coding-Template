#!/usr/bin/env python3
"""Validate every agents/<name>/agent.yaml against the manifest schema.

The schema is read from schemas/agent-manifest.schema.json and validated with a
small validator that supports the keywords that schema uses. No third-party
dependency is required.

Rules:
  MAN-001  agent.yaml does not parse as the supported YAML subset.
  MAN-002  agent.yaml violates the manifest schema.
  MAN-003  name does not match its directory name.
  MAN-004  owner does not appear in CODEOWNERS.
  MAN-005  a declared tool contract file is missing under schemas/tool-contracts/.

Exit codes: 0 clean, 1 findings, 2 the script could not run.
"""

from __future__ import annotations

import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".venv", "__pycache__", "dist"}

SCALAR_INT = re.compile(r"^-?\d+$")
SCALAR_FLOAT = re.compile(r"^-?\d+\.\d+$")


def parse_scalar(raw: str):
    """Convert a YAML scalar to a Python value."""
    text = raw.strip()
    if text == "":
        return None
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        return text[1:-1]
    if text in ("true", "false"):
        return text == "true"
    if text in ("null", "~"):
        return None
    if SCALAR_INT.match(text):
        return int(text)
    if SCALAR_FLOAT.match(text):
        return float(text)
    return text


def parse_simple_yaml(text: str):
    """Parse the YAML subset used by agent.yaml: maps, nested maps and lists.

    Comments and blank lines are ignored. Tabs are rejected because they make
    the indentation ambiguous.
    """
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if "\t" in raw:
            raise ValueError("tab characters are not allowed in the manifest")
        stripped = raw.split("#", 1)[0].rstrip() if not raw.strip().startswith("#") else ""
        if stripped.strip() == "":
            continue
        indent = len(stripped) - len(stripped.lstrip(" "))
        lines.append((indent, stripped.strip()))

    def parse_block(index: int, indent: int):
        if index >= len(lines):
            return {}, index
        if lines[index][1].startswith("- "):
            items = []
            while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
                items.append(parse_scalar(lines[index][1][2:]))
                index += 1
            return items, index

        mapping: dict[str, object] = {}
        while index < len(lines) and lines[index][0] == indent:
            key_text = lines[index][1]
            if ":" not in key_text:
                raise ValueError(f"expected 'key: value', received {key_text!r}")
            key, _, value = key_text.partition(":")
            key = key.strip()
            value = value.strip()
            index += 1
            if value == "":
                if index < len(lines) and lines[index][0] > indent:
                    nested, index = parse_block(index, lines[index][0])
                    mapping[key] = nested
                else:
                    mapping[key] = None
            else:
                mapping[key] = parse_scalar(value)
        return mapping, index

    if not lines:
        raise ValueError("the manifest is empty")
    document, _ = parse_block(0, lines[0][0])
    return document


def validate(value, schema: dict, path: str, errors: list[str]) -> None:
    """Validate a value against the supported subset of JSON Schema."""
    expected_type = schema.get("type")
    type_ok = {
        "object": isinstance(value, dict),
        "array": isinstance(value, list),
        "string": isinstance(value, str),
        "number": isinstance(value, (int, float)) and not isinstance(value, bool),
        "integer": isinstance(value, int) and not isinstance(value, bool),
        "boolean": isinstance(value, bool),
    }.get(expected_type, True)

    if not type_ok:
        errors.append(f"{path}: expected {expected_type}, received {type(value).__name__}")
        return

    if isinstance(value, str):
        pattern = schema.get("pattern")
        if pattern and re.fullmatch(pattern, value) is None:
            errors.append(f"{path}: {value!r} does not match {pattern}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: shorter than {schema['minLength']} characters")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: longer than {schema['maxLength']} characters")

    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: below the minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: above the maximum {schema['maximum']}")

    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(f"{path}: more than {schema['maxItems']} items")
        if schema.get("uniqueItems") and len(value) != len({json.dumps(item, sort_keys=True) for item in value}):
            errors.append(f"{path}: duplicate items")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for position, item in enumerate(value):
                validate(item, item_schema, f"{path}[{position}]", errors)

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: required key {key!r} is missing")
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: unknown key {key!r}")
        for key, sub_schema in properties.items():
            if key in value and isinstance(sub_schema, dict):
                validate(value[key], sub_schema, f"{path}.{key}", errors)


def find_manifests(root: str) -> list[str]:
    found: list[str] = []
    agents_dir = os.path.join(root, "agents")
    if not os.path.isdir(agents_dir):
        return found
    for name in sorted(os.listdir(agents_dir)):
        candidate = os.path.join(agents_dir, name, "agent.yaml")
        if os.path.isfile(candidate):
            found.append(f"agents/{name}/agent.yaml")
    return found


def read_codeowners_owners(root: str) -> set[str]:
    path = os.path.join(root, "CODEOWNERS")
    owners: set[str] = set()
    if not os.path.isfile(path):
        return owners
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.split("#", 1)[0].strip()
            if line == "":
                continue
            for token in line.split()[1:]:
                owners.add(token.lstrip("@"))
    return owners


def main(argv: list[str]) -> int:
    root = os.path.abspath(argv[1] if len(argv) > 1 else ".")
    schema_path = os.path.join(root, "schemas", "agent-manifest.schema.json")
    if not os.path.isfile(schema_path):
        print(f"check-agent-manifests: schema not found: {schema_path}", file=sys.stderr)
        return 2

    with open(schema_path, encoding="utf-8") as handle:
        schema = json.load(handle)

    manifests = find_manifests(root)
    if not manifests:
        print("check-agent-manifests: no agents/*/agent.yaml found", file=sys.stderr)
        return 2

    owners = read_codeowners_owners(root)
    findings: list[tuple[str, int, str, str]] = []

    for rel in manifests:
        with open(os.path.join(root, rel), encoding="utf-8") as handle:
            text = handle.read()
        try:
            document = parse_simple_yaml(text)
        except ValueError as error:
            findings.append((rel, 0, "MAN-001", str(error)))
            continue

        errors: list[str] = []
        validate(document, schema, "agent", errors)
        for message in errors:
            findings.append((rel, 0, "MAN-002", message))

        # find_manifests() normalises the path to forward slashes.
        directory_name = rel.split("/")[1]
        if document.get("name") != directory_name:
            findings.append(
                (rel, 0, "MAN-003", f"name {document.get('name')!r} != directory {directory_name!r}")
            )

        owner = document.get("owner")
        if isinstance(owner, str) and owner not in owners:
            findings.append((rel, 0, "MAN-004", f"owner {owner!r} does not appear in CODEOWNERS"))

        # A declared tool resolves either to a shared contract under
        # schemas/tool-contracts/ or to an implementation under the agent's own
        # tools/ directory. See schemas/agent-manifest.schema.json.
        tools_dir = os.path.join(root, "agents", directory_name, "tools")
        local_tools: list[str] = []
        if os.path.isdir(tools_dir):
            local_tools = [
                name.rsplit(".", 1)[0].replace("-", "_") for name in os.listdir(tools_dir)
            ]
        for tool in document.get("tools") or []:
            if not isinstance(tool, str):
                continue
            contract = os.path.join(root, "schemas", "tool-contracts", f"{tool}.schema.json")
            if os.path.isfile(contract):
                continue
            implemented = any(
                name == tool or name == f"{tool}_tool" or name.startswith(f"{tool}_")
                for name in local_tools
            )
            if not implemented:
                findings.append(
                    (
                        rel,
                        0,
                        "MAN-005",
                        f"no contract at schemas/tool-contracts/{tool}.schema.json and no local implementation in agents/{directory_name}/tools/",
                    )
                )

    findings.sort()
    for rel, number, code, message in findings:
        print(f"{rel}:{number}  {code}  {message}")

    print(f"manifests={len(manifests)} violations={len(findings)} affected_files={len({f[0] for f in findings})}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
