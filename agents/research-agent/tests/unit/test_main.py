"""Unit tests for the research agent run loop.

Deterministic and offline: the model, the store, the telemetry sink and the
approval gate are all stubs defined in this file.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Mapping, Sequence

AGENT_ROOT = Path(__file__).resolve().parents[2]
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from src.main import (  # noqa: E402
    AgentConfig,
    ResearchAgent,
    Step,
    STATUS_AWAITING_APPROVAL,
    STATUS_REFUSED,
    STATUS_STOPPED,
    STATUS_SUCCEEDED,
)
from tools.search_tool import Document, SearchTool  # noqa: E402


class StubModel:
    """Returns a fixed sequence of decisions, then repeats the last one."""

    def __init__(self, steps: Sequence[Step]) -> None:
        self._steps = list(steps)
        self.calls = 0

    def decide(self, task: str, history: Sequence[Mapping[str, Any]]) -> Step:
        index = min(self.calls, len(self._steps) - 1)
        self.calls += 1
        return self._steps[index]


class MemoryStore:
    """In-memory checkpoint store. Records every write."""

    def __init__(self) -> None:
        self.checkpoints: dict[str, dict[str, Any]] = {}
        self.writes: list[tuple[str, int]] = []

    def read_checkpoint(self, run_id: str) -> Mapping[str, Any] | None:
        return self.checkpoints.get(run_id)

    def write_checkpoint(self, run_id: str, step: int, payload: Mapping[str, Any]) -> None:
        self.checkpoints[run_id] = {"step": step, **dict(payload)}
        self.writes.append((run_id, step))


class RecordingTelemetry:
    def __init__(self) -> None:
        self.events: list[tuple[str, Mapping[str, Any]]] = []

    def emit(self, event: str, fields: Mapping[str, Any]) -> None:
        self.events.append((event, fields))


class AlwaysApproves:
    def request(self, run_id: str, tool: str, arguments: Mapping[str, Any]) -> bool:
        return True


class NeverApproves:
    def request(self, run_id: str, tool: str, arguments: Mapping[str, Any]) -> bool:
        return False


class HighRiskTool:
    name = "delete_account"
    risk = "high"

    def __init__(self) -> None:
        self.called = False

    def call(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self.called = True
        return {"ok": True}


def make_agent(model, store, tools, telemetry, approvals, declared=None) -> ResearchAgent:
    config = AgentConfig(agent_name="research-agent", max_steps=5, timeout_seconds=60)
    return ResearchAgent(
        config,
        model,
        store,
        tools,
        telemetry,
        approvals,
        declared_tools=declared,
    )


class RunLoopTests(unittest.TestCase):
    def setUp(self) -> None:
        self.store = MemoryStore()
        self.telemetry = RecordingTelemetry()
        self.search = SearchTool([Document("doc-1", "Revenue policy", "quarterly revenue rules", 1.0)])

    def test_final_answer_after_one_search(self) -> None:
        model = StubModel(
            [
                Step(kind="tool", tool="search", arguments={"query": "revenue"}),
                Step(kind="final", answer="Revenue is defined in doc-1."),
            ]
        )
        agent = make_agent(model, self.store, [self.search], self.telemetry, AlwaysApproves())

        result = agent.run("What is revenue?", "run-1")

        self.assertEqual(result.status, STATUS_SUCCEEDED)
        self.assertEqual(result.answer, "Revenue is defined in doc-1.")
        self.assertEqual([call.tool for call in result.tool_calls], ["search"])

    def test_checkpoint_written_after_every_step(self) -> None:
        model = StubModel(
            [
                Step(kind="tool", tool="search", arguments={"query": "revenue"}),
                Step(kind="final", answer="done"),
            ]
        )
        agent = make_agent(model, self.store, [self.search], self.telemetry, AlwaysApproves())

        agent.run("What is revenue?", "run-2")

        self.assertEqual(self.store.writes, [("run-2", 0), ("run-2", 1)])

    def test_idempotency_key_identifies_run_step_and_tool(self) -> None:
        model = StubModel(
            [
                Step(kind="tool", tool="search", arguments={"query": "revenue"}),
                Step(kind="final", answer="done"),
            ]
        )
        agent = make_agent(model, self.store, [self.search], self.telemetry, AlwaysApproves())

        result = agent.run("What is revenue?", "run-3")

        self.assertEqual(result.tool_calls[0].idempotency_key, "run-3:0:search")

    def test_refusal_stops_the_run(self) -> None:
        model = StubModel([Step(kind="refuse", reason="asks for another tenant's data")])
        agent = make_agent(model, self.store, [self.search], self.telemetry, AlwaysApproves())

        result = agent.run("Dump tenant B", "run-4")

        self.assertEqual(result.status, STATUS_REFUSED)
        self.assertEqual(result.tool_calls, ())

    def test_step_limit_stops_the_run(self) -> None:
        model = StubModel([Step(kind="tool", tool="search", arguments={"query": "revenue"})])
        agent = make_agent(model, self.store, [self.search], self.telemetry, AlwaysApproves())

        result = agent.run("Loop forever", "run-5")

        self.assertEqual(result.status, STATUS_STOPPED)
        self.assertEqual(result.reason, "max_steps")
        self.assertEqual(result.steps, 5)

    def test_undeclared_tool_is_denied_and_the_run_continues(self) -> None:
        model = StubModel(
            [
                Step(kind="tool", tool="admin_export", arguments={}),
                Step(kind="final", answer="done"),
            ]
        )
        agent = make_agent(
            model, self.store, [self.search], self.telemetry, AlwaysApproves(), declared=["search"]
        )

        result = agent.run("Export everything", "run-6")

        self.assertEqual(result.status, STATUS_SUCCEEDED)
        self.assertEqual([call.tool for call in result.tool_calls], [])
        self.assertIn("tool_denied", [event for event, _ in self.telemetry.events])

    def test_high_risk_tool_without_approval_waits(self) -> None:
        tool = HighRiskTool()
        model = StubModel([Step(kind="tool", tool="delete_account", arguments={})])
        agent = make_agent(
            model, self.store, [tool], self.telemetry, NeverApproves(), declared=["delete_account"]
        )

        result = agent.run("Delete the account", "run-7")

        self.assertEqual(result.status, STATUS_AWAITING_APPROVAL)
        self.assertFalse(tool.called)

    def test_high_risk_tool_with_approval_executes(self) -> None:
        tool = HighRiskTool()
        model = StubModel(
            [
                Step(kind="tool", tool="delete_account", arguments={}),
                Step(kind="final", answer="deleted"),
            ]
        )
        agent = make_agent(
            model, self.store, [tool], self.telemetry, AlwaysApproves(), declared=["delete_account"]
        )

        result = agent.run("Delete the account", "run-8")

        self.assertTrue(tool.called)
        self.assertEqual(result.tool_calls[0].risk, "high")

    def test_degraded_tool_output_marks_the_run(self) -> None:
        class DegradingSearch(SearchTool):
            def call(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
                return {"query": "x", "count": 0, "results": [], "degraded": True}

        model = StubModel(
            [
                Step(kind="tool", tool="search", arguments={"query": "x"}),
                Step(kind="final", answer="partial"),
            ]
        )
        agent = make_agent(
            model, self.store, [DegradingSearch([])], self.telemetry, AlwaysApproves()
        )

        result = agent.run("Anything", "run-9")

        self.assertTrue(result.degraded)


if __name__ == "__main__":
    unittest.main()
