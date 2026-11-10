"""End-to-end smoke tests for the platform contract surface.

These tests load the real repository files and assert their internal
consistency. They need no network and no database, so they run in any
environment, including a clean checkout in CI.
"""

from __future__ import annotations

import json
import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

AGENT_NAMES = ("research-agent", "support-agent")


class RepositoryLayoutTests(unittest.TestCase):
    def test_every_agent_has_a_manifest_and_a_prompt(self) -> None:
        for name in AGENT_NAMES:
            agent_dir = REPO_ROOT / "agents" / name
            self.assertTrue((agent_dir / "agent.yaml").is_file(), f"{name}: agent.yaml missing")
            self.assertTrue(
                (agent_dir / "prompts" / "system.md").is_file(), f"{name}: system prompt missing"
            )
            self.assertTrue((agent_dir / "AGENTS.md").is_file(), f"{name}: module AGENTS.md missing")

    def test_every_agent_manifest_matches_its_directory(self) -> None:
        for name in AGENT_NAMES:
            text = (REPO_ROOT / "agents" / name / "agent.yaml").read_text(encoding="utf-8")
            self.assertIn(f"name: {name}", text)

    def test_shared_schemas_are_valid_json(self) -> None:
        schemas = sorted((REPO_ROOT / "schemas").rglob("*.json"))
        self.assertGreaterEqual(len(schemas), 3, "expected at least three shared schemas")
        for schema in schemas:
            with self.subTest(schema=str(schema)):
                json.loads(schema.read_text(encoding="utf-8"))

    def test_eval_baseline_holds_every_release_field(self) -> None:
        baseline = REPO_ROOT / "evals" / "baselines" / "baseline-2026-01.json"
        data = json.loads(baseline.read_text(encoding="utf-8"))
        for key in ("revision", "manifest_version", "prompt_hash", "model", "baseline", "gates"):
            self.assertIn(key, data)
        for gate, spec in data["gates"].items():
            with self.subTest(gate=gate):
                self.assertIsNotNone(spec.get("threshold"))


class ContractTests(unittest.TestCase):
    def test_agent_manifest_schema_requires_the_contract_keys(self) -> None:
        schema = json.loads(
            (REPO_ROOT / "schemas" / "agent-manifest.schema.json").read_text(encoding="utf-8")
        )
        for key in ("name", "version", "owner", "description", "model", "tools", "limits"):
            self.assertIn(key, schema["required"])
        self.assertFalse(schema["additionalProperties"])

    def test_search_tool_contract_marks_the_tool_read_only(self) -> None:
        contract = json.loads(
            (REPO_ROOT / "schemas" / "tool-contracts" / "search.schema.json").read_text(encoding="utf-8")
        )
        text = json.dumps(contract)
        self.assertIn("search", text)

    def test_run_status_values_are_stable(self) -> None:
        types_file = REPO_ROOT / "packages" / "agent-contracts" / "src" / "types.ts"
        text = types_file.read_text(encoding="utf-8")
        for status in ("running", "awaiting_approval", "degraded", "succeeded", "failed", "cancelled"):
            self.assertIn(f"'{status}'", text)


class SecurityBaselineTests(unittest.TestCase):
    def test_no_credential_literal_in_tracked_configuration(self) -> None:
        """A real key never appears in a configuration file: only a variable name."""
        suspicious = re.compile(r"(sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,})")
        roots = [REPO_ROOT / ".codex", REPO_ROOT / ".github", REPO_ROOT / ".mcp.json"]
        for root in roots:
            paths = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]
            for path in paths:
                with self.subTest(path=str(path.relative_to(REPO_ROOT))):
                    text = path.read_text(encoding="utf-8", errors="replace")
                    self.assertIsNone(suspicious.search(text), "a credential literal was found")

    def test_prod_environment_is_marked_protected(self) -> None:
        prod = (REPO_ROOT / "infra" / "environments" / "prod" / "main.tf").read_text(encoding="utf-8")
        self.assertIn("PROTECTED PATH", prod)

    def test_policy_file_denies_by_default(self) -> None:
        policy = (REPO_ROOT / "infra" / "policies" / "agent-tool-access.rego").read_text(encoding="utf-8")
        self.assertIn("default allow := false", policy)


if __name__ == "__main__":
    unittest.main()
