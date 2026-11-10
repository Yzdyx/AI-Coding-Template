"""Integration tests: the run loop with several tools and a real resume path.

No network and no clock dependency. The upstream is a stub whose latency is
expressed as a recorded flag rather than as a sleep.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Mapping, Sequence

AGENT_ROOT = Path(__file__).resolve().parents[2]
if str(AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(AGENT_ROOT))

from src.main import AgentConfig, ResearchAgent, Step, STATUS_SUCCEEDED  # noqa: E402
from tools.search_tool import Document, SearchTool  # noqa: E402


class SlowThenFastSearch:
    """A search tool that degrades on the first call and succeeds afterwards."""

    name = "search"
    risk = "low"

    def __init__(self) -> None:
        self.calls = 0

    def call(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        self.calls += 1
        if self.calls == 1:
            return {"query": arguments.get("query", ""), "count": 0, "results": [], "degraded": True}
        return {
            "query": arguments.get("query", ""),
            "count": 1,
            "results": [{"document_id": "doc-9", "title": "Onboarding", "snippet": "steps", "score": 1.0}],
            "degraded": False,
        }


class StubModel:
    def __init__(self, steps: Sequence[Step]) -> None:
        self._steps = list(steps)
        self.calls = 0

    def decide(self, task: str, history: Sequence[Mapping[str, Any]]) -> Step:
        index = min(self.calls, len(self._steps) - 1)
        self.calls += 1
        return self._steps[index]


class MemoryStore:
    def __init__(self) -> None:
        self.checkpoints: dict[str, dict[str, Any]] = {}

    def read_checkpoint(self, run_id: str) -> Mapping[str, Any] | None:
        return self.checkpoints.get(run_id)

    def write_checkpoint(self, run_id: str, step: int, payload: Mapping[str, Any]) -> None:
        self.checkpoints[run_id] = {"step": step, **dict(payload)}


class NullTelemetry:
    def emit(self, event: str, fields: Mapping[str, Any]) -> None:
        return None


class ApproveAll:
    def request(self, run_id: str, tool: str, arguments: Mapping[str, Any]) -> bool:
        return True


class WorkflowTests(unittest.TestCase):
    def test_two_tool_workflow_reaches_a_final_answer(self) -> None:
        model = StubModel(
            [
                Step(kind="tool", tool="search", arguments={"query": "onboarding"}),
                Step(kind="tool", tool="search", arguments={"query": "onboarding steps"}),
                Step(kind="final", answer="See doc-9."),
            ]
        )
        store = MemoryStore()
        agent = ResearchAgent(
            AgentConfig(max_steps=8, timeout_seconds=120),
            model,
            store,
            [SlowThenFastSearch()],
            NullTelemetry(),
            ApproveAll(),
        )

        result = agent.run("How does onboarding work?", "run-int-1")

        self.assertEqual(result.status, STATUS_SUCCEEDED)
        self.assertEqual(result.answer, "See doc-9.")
        self.assertEqual(len(result.tool_calls), 2)
        self.assertTrue(result.degraded)

    def test_run_resumes_from_a_checkpoint(self) -> None:
        store = MemoryStore()
        store.checkpoints["run-int-2"] = {"step": 0, "history": [{"step": 0, "tool": "search"}]}
        model = StubModel([Step(kind="final", answer="resumed")])
        agent = ResearchAgent(
            AgentConfig(max_steps=8, timeout_seconds=120),
            model,
            store,
            [SearchTool([Document("doc-1", "t", "s", 1.0)])],
            NullTelemetry(),
            ApproveAll(),
        )

        result = agent.run("Continue", "run-int-2")

        self.assertEqual(result.status, STATUS_SUCCEEDED)
        self.assertEqual(result.steps, 2)
        self.assertEqual(result.tool_calls, ())

    def test_search_tool_ranks_by_score(self) -> None:
        tool = SearchTool(
            [
                Document("doc-b", "Revenue", "revenue only", 1.0),
                Document("doc-a", "Revenue policy", "quarterly revenue rules", 1.0),
                Document("doc-c", "Unrelated", "nothing here", 1.0),
            ]
        )
        output = tool.call({"query": "quarterly revenue", "limit": 3})

        # doc-a matches both query terms, doc-b matches one, doc-c matches none.
        self.assertEqual([item["document_id"] for item in output["results"]], ["doc-a", "doc-b"])

    def test_equal_scores_break_the_tie_by_identifier(self) -> None:
        tool = SearchTool(
            [
                Document("doc-z", "Revenue", "revenue", 1.0),
                Document("doc-a", "Revenue", "revenue", 1.0),
            ]
        )
        output = tool.call({"query": "revenue", "limit": 2})

        self.assertEqual([item["document_id"] for item in output["results"]], ["doc-a", "doc-z"])


if __name__ == "__main__":
    unittest.main()
