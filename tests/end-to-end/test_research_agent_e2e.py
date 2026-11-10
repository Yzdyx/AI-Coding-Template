"""End-to-end test of the research agent, offline.

The full run loop is exercised against a stubbed model provider, an in-memory
checkpoint store and a recording telemetry sink. The test asserts the three
properties the platform depends on:

  1. a checkpoint is written after every step, so a run is resumable;
  2. every tool call carries a deterministic idempotency key, so a replay cannot
     repeat the side effect;
  3. a resumed run continues from its checkpoint and does not repeat a completed
     tool call.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_ROOT = REPO_ROOT / "agents" / "research-agent"
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from src.main import (  # noqa: E402
    AgentConfig,
    ResearchAgent,
    Step,
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
    """Checkpoint store that records every write, in order."""

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
        self.events: list[str] = []

    def emit(self, event: str, fields: Mapping[str, Any]) -> None:
        self.events.append(event)


class ApproveAll:
    def request(self, run_id: str, tool: str, arguments: Mapping[str, Any]) -> bool:
        return True


DOCUMENTS = [
    Document("kb-revenue", "Revenue recognition", "quarterly revenue recognition rules", 1.0),
    Document("kb-onboarding", "Supplier onboarding", "steps to onboard a supplier", 1.0),
]


def build_agent(steps: Sequence[Step], store: MemoryStore, telemetry: RecordingTelemetry) -> ResearchAgent:
    return ResearchAgent(
        AgentConfig(agent_name="research-agent", max_steps=8, timeout_seconds=120),
        StubModel(steps),
        store,
        [SearchTool(DOCUMENTS)],
        telemetry,
        ApproveAll(),
    )


class ResearchAgentEndToEndTests(unittest.TestCase):
    def test_full_run_writes_a_checkpoint_per_step_and_returns_an_answer(self) -> None:
        store = MemoryStore()
        telemetry = RecordingTelemetry()
        agent = build_agent(
            [
                Step(kind="tool", tool="search", arguments={"query": "revenue recognition"}),
                Step(kind="tool", tool="search", arguments={"query": "supplier onboarding"}),
                Step(kind="final", answer="Revenue follows kb-revenue. Onboarding follows kb-onboarding."),
            ],
            store,
            telemetry,
        )

        result = agent.run("Summarise revenue and onboarding.", "run-e2e-1")

        self.assertEqual(result.status, STATUS_SUCCEEDED)
        self.assertIn("kb-revenue", result.answer)
        self.assertEqual(len(result.tool_calls), 2)
        self.assertEqual(store.writes, [("run-e2e-1", 0), ("run-e2e-1", 1), ("run-e2e-1", 2)])
        self.assertEqual(
            telemetry.events,
            ["run_started", "tool_called", "tool_called", "run_finished"],
        )

    def test_every_tool_call_carries_a_deterministic_idempotency_key(self) -> None:
        store = MemoryStore()
        agent = build_agent(
            [
                Step(kind="tool", tool="search", arguments={"query": "revenue"}),
                Step(kind="final", answer="done"),
            ],
            store,
            RecordingTelemetry(),
        )

        result = agent.run("What is revenue?", "run-e2e-2")

        keys = [call.idempotency_key for call in result.tool_calls]
        self.assertEqual(keys, ["run-e2e-2:0:search"])

    def test_resumed_run_continues_from_its_checkpoint(self) -> None:
        store = MemoryStore()
        # A previous attempt completed step 0 and crashed before step 1.
        store.checkpoints["run-e2e-3"] = {
            "step": 0,
            "history": [{"step": 0, "tool": "search", "output": {"count": 1}}],
        }
        agent = build_agent(
            [Step(kind="final", answer="resumed after a crash")],
            store,
            RecordingTelemetry(),
        )

        result = agent.run("Continue the task.", "run-e2e-3")

        self.assertEqual(result.status, STATUS_SUCCEEDED)
        self.assertEqual(result.steps, 2)
        self.assertEqual(result.tool_calls, (), "a resumed run must not repeat a completed tool call")
        self.assertEqual(store.writes, [("run-e2e-3", 1)])

    def test_the_search_tool_returns_citable_documents(self) -> None:
        store = MemoryStore()
        agent = build_agent(
            [
                Step(kind="tool", tool="search", arguments={"query": "supplier onboarding"}),
                Step(kind="final", answer="See kb-onboarding."),
            ],
            store,
            RecordingTelemetry(),
        )

        result = agent.run("How does onboarding work?", "run-e2e-4")

        output = result.tool_calls[0].output
        self.assertEqual(output["count"], 1)
        self.assertEqual(output["results"][0]["document_id"], "kb-onboarding")


if __name__ == "__main__":
    unittest.main()
