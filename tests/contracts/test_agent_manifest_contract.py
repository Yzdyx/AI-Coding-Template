"""Contract tests for the agent manifest.

Every `agents/<name>/agent.yaml` is a contract: the runtime, the platform module
and the evaluation harness all read it. These tests load the real files and
assert the contract holds.

The YAML subset parser is inline on purpose: the test suite must run with the
standard library alone, on a clean checkout, with no dependency install.
"""

from __future__ import annotations

import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTS_DIR = REPO_ROOT / "agents"

REQUIRED_KEYS = ("name", "version", "owner", "description", "model", "tools", "limits")
SCALAR_INT = re.compile(r"^-?\d+$")
SCALAR_FLOAT = re.compile(r"^-?\d+\.\d+$")
NAME_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
OWNER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
VERSION_PATTERN = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def parse_scalar(raw: str):
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
    """Parse the manifest subset: nested mappings and `- item` scalar lists."""
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if "\t" in raw:
            raise ValueError("tab characters are not allowed in a manifest")
        if raw.strip().startswith("#"):
            continue
        stripped = raw.split("#", 1)[0].rstrip() if "#" in raw else raw.rstrip()
        if stripped.strip() == "":
            continue
        lines.append((len(stripped) - len(stripped.lstrip(" ")), stripped.strip()))

    def parse_block(index: int, indent: int):
        if index < len(lines) and lines[index][1].startswith("- "):
            items = []
            while index < len(lines) and lines[index][0] == indent and lines[index][1].startswith("- "):
                items.append(parse_scalar(lines[index][1][2:]))
                index += 1
            return items, index

        mapping: dict[str, object] = {}
        while index < len(lines) and lines[index][0] == indent:
            key, _, value = lines[index][1].partition(":")
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


def load_manifests() -> dict[str, dict]:
    manifests: dict[str, dict] = {}
    for agent_dir in sorted(p for p in AGENTS_DIR.iterdir() if p.is_dir()):
        manifest_path = agent_dir / "agent.yaml"
        if manifest_path.is_file():
            manifests[agent_dir.name] = parse_simple_yaml(manifest_path.read_text(encoding="utf-8"))
    return manifests


MANIFESTS = load_manifests()


class ManifestPresenceTests(unittest.TestCase):
    def test_at_least_one_agent_is_present(self) -> None:
        self.assertGreaterEqual(len(MANIFESTS), 1, "no agents/<name>/agent.yaml was found")

    def test_every_agent_directory_has_a_manifest(self) -> None:
        for agent_dir in sorted(p for p in AGENTS_DIR.iterdir() if p.is_dir()):
            with self.subTest(agent=agent_dir.name):
                self.assertTrue(
                    (agent_dir / "agent.yaml").is_file(), f"{agent_dir.name} has no agent.yaml"
                )


class ManifestShapeTests(unittest.TestCase):
    def test_required_keys_are_present(self) -> None:
        for name, manifest in MANIFESTS.items():
            for key in REQUIRED_KEYS:
                with self.subTest(agent=name, key=key):
                    self.assertIn(key, manifest)

    def test_name_equals_directory_name(self) -> None:
        for name, manifest in MANIFESTS.items():
            with self.subTest(agent=name):
                self.assertEqual(manifest["name"], name)

    def test_name_version_and_owner_match_their_pattern(self) -> None:
        for name, manifest in MANIFESTS.items():
            with self.subTest(agent=name):
                self.assertRegex(str(manifest["name"]), NAME_PATTERN)
                self.assertRegex(str(manifest["version"]), VERSION_PATTERN)
                self.assertRegex(str(manifest["owner"]), OWNER_PATTERN)

    def test_owner_appears_in_codeowners(self) -> None:
        codeowners = (REPO_ROOT / "CODEOWNERS").read_text(encoding="utf-8")
        owners = {
            token.lstrip("@")
            for line in codeowners.splitlines()
            if line.strip() and not line.strip().startswith("#")
            for token in line.split()[1:]
        }
        for name, manifest in MANIFESTS.items():
            with self.subTest(agent=name):
                self.assertIn(manifest["owner"], owners)


class ManifestConsistencyTests(unittest.TestCase):
    def test_limits_are_within_the_schema_bounds(self) -> None:
        for name, manifest in MANIFESTS.items():
            limits = manifest["limits"]
            with self.subTest(agent=name):
                self.assertIsInstance(limits["max_steps"], int)
                self.assertGreaterEqual(limits["max_steps"], 1)
                self.assertLessEqual(limits["max_steps"], 500)
                self.assertIsInstance(limits["timeout_seconds"], int)
                self.assertGreaterEqual(limits["timeout_seconds"], 1)

    def test_model_block_is_complete(self) -> None:
        for name, manifest in MANIFESTS.items():
            model = manifest["model"]
            with self.subTest(agent=name):
                self.assertIn("provider", model)
                self.assertIn("name", model)
                self.assertIsInstance(model["temperature"], float)
                self.assertGreaterEqual(model["temperature"], 0)
                self.assertLessEqual(model["temperature"], 2)

    def test_every_tool_resolves_to_a_contract_or_a_local_implementation(self) -> None:
        for name, manifest in MANIFESTS.items():
            tools_dir = AGENTS_DIR / name / "tools"
            local = {p.stem.replace("-", "_") for p in tools_dir.glob("*.py")} if tools_dir.is_dir() else set()
            for tool in manifest["tools"]:
                with self.subTest(agent=name, tool=tool):
                    contract = REPO_ROOT / "schemas" / "tool-contracts" / f"{tool}.schema.json"
                    implemented = any(
                        stem == tool or stem == f"{tool}_tool" or stem.startswith(f"{tool}_")
                        for stem in local
                    )
                    self.assertTrue(
                        contract.is_file() or implemented,
                        f"{tool} has no contract and no local implementation",
                    )

    def test_every_declared_test_path_exists(self) -> None:
        for name, manifest in MANIFESTS.items():
            for entry in manifest.get("tests") or []:
                with self.subTest(agent=name, path=entry):
                    self.assertTrue(
                        (AGENTS_DIR / name / entry).exists(),
                        f"agents/{name}/{entry} does not exist",
                    )

    def test_every_declared_test_path_is_reachable_from_the_manifest(self) -> None:
        # A manifest that lists no test path cannot be verified by the release gate.
        for name, manifest in MANIFESTS.items():
            with self.subTest(agent=name):
                self.assertTrue(manifest.get("tests"), f"{name} declares no tests")


if __name__ == "__main__":
    unittest.main()
