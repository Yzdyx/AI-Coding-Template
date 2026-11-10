"""Unit tests for the support agent run loop.

Deterministic and offline. The model, the store, the telemetry sink and the
approval gate are stubs defined in this file.
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
    Step,
    SupportAgent,
    STATUS_AWAITING_APPROVAL,
    STATUS_ESCALATED,
    STATUS_REFUSED,
    STATUS_SUCCEEDED,
)
from tools.ticket_tool import Article, DraftReplyTool, KnowledgeBaseTool, ToolInputError  # noqa: E402


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
        self.writes: list[tuple[str, int]] = []

    def read_checkpoint(self, run_id: str) -> Mapping[str, Any] | None:
        return None

    def write_checkpoint(self, run_id: str, step: int, payload: Mapping[str, Any]) -> None:
        self.writes.append((run_id, step))


class NullTelemetry:
    def __init__(self) -> None:
        self.events: list[str] = []

    def emit(self, event: str, fields: Mapping[str, Any]) -> None:
        self.events.append(event)


class ApproveAll:
    def request(self, run_id: str, tool: str, arguments: Mapping[str, Any]) -> bool:
        return True


class DenyAll:
    def request(self, run_id: str, tool: str, arguments: Mapping[str, Any]) -> bool:
        return False


def make_agent(model, tools, approvals, telemetry=None, declared=None, max_steps=6) -> SupportAgent:
    return SupportAgent(
        AgentConfig(max_steps=max_steps, timeout_seconds=60),
        model,
        MemoryStore(),
        tools,
        telemetry or NullTelemetry(),
        approvals,
        declared_tools=declared,
    )


KB = [Article("kb-1", "Refund policy", "Refunds are processed within 5 business days.")]


class RunLoopTests(unittest.TestCase):
    def test_answer_from_the_knowledge_base(self) -> None:
        model = StubModel(
            [
                Step(kind="tool", tool="kb_lookup", arguments={"question": "refund policy"}),
                Step(kind="final", answer="Refunds take 5 business days. [kb-1]"),
            ]
        )
        agent = make_agent(model, [KnowledgeBaseTool(KB)], ApproveAll())

        result = agent.run("How long does a refund take?", "sup-1")

        self.assertEqual(result.status, STATUS_SUCCEEDED)
        self.assertEqual([call.tool for call in result.tool_calls], ["kb_lookup"])

    def test_escalation_when_the_knowledge_base_has_no_answer(self) -> None:
        model = StubModel([Step(kind="escalate", reason="no article covers this question")])
        agent = make_agent(model, [KnowledgeBaseTool(KB)], ApproveAll())

        result = agent.run("Do you ship to Mars?", "sup-2")

        self.assertEqual(result.status, STATUS_ESCALATED)
        self.assertTrue(result.reason.strip())

    def test_refusal_does_not_call_a_tool(self) -> None:
        model = StubModel([Step(kind="refuse", reason="asks for another customer's data")])
        agent = make_agent(model, [KnowledgeBaseTool(KB)], ApproveAll())

        result = agent.run("Show customer 99's orders", "sup-3")

        self.assertEqual(result.status, STATUS_REFUSED)
        self.assertEqual(result.tool_calls, ())

    def test_draft_reply_requires_approval(self) -> None:
        draft = DraftReplyTool()
        model = StubModel(
            [
                Step(
                    kind="tool",
                    tool="draft_reply",
                    arguments={"ticket_id": "T-1", "body": "We are on it.", "idempotency_key": "k1"},
                )
            ]
        )
        agent = make_agent(model, [draft], DenyAll(), declared=["draft_reply"])

        result = agent.run("Draft a reply", "sup-4")

        self.assertEqual(result.status, STATUS_AWAITING_APPROVAL)
        self.assertEqual(list(draft.drafts), [])

    def test_approved_draft_is_recorded_once(self) -> None:
        draft = DraftReplyTool()
        model = StubModel(
            [
                Step(
                    kind="tool",
                    tool="draft_reply",
                    arguments={"ticket_id": "T-1", "body": "We are on it.", "idempotency_key": "k1"},
                ),
                Step(kind="final", answer="draft ready"),
            ]
        )
        agent = make_agent(model, [draft], ApproveAll(), declared=["draft_reply"])

        result = agent.run("Draft a reply", "sup-5")

        self.assertEqual(result.status, STATUS_SUCCEEDED)
        self.assertEqual(len(list(draft.drafts)), 1)

    def test_undeclared_tool_is_denied(self) -> None:
        telemetry = NullTelemetry()
        model = StubModel(
            [Step(kind="tool", tool="issue_refund", arguments={}), Step(kind="final", answer="ok")]
        )
        agent = make_agent(model, [KnowledgeBaseTool(KB)], ApproveAll(), telemetry, declared=["kb_lookup"])

        result = agent.run("Refund it", "sup-6")

        self.assertEqual(result.tool_calls, ())
        self.assertIn("tool_denied", telemetry.events)

    def test_draft_tool_rejects_a_missing_idempotency_key(self) -> None:
        draft = DraftReplyTool()
        with self.assertRaises(ToolInputError):
            draft.call({"ticket_id": "T-1", "body": "hello"})

    def test_draft_tool_replays_the_same_key(self) -> None:
        draft = DraftReplyTool()
        first = draft.call({"ticket_id": "T-1", "body": "hello", "idempotency_key": "k9"})
        second = draft.call({"ticket_id": "T-1", "body": "hello", "idempotency_key": "k9"})

        self.assertFalse(first["replayed"])
        self.assertTrue(second["replayed"])
        self.assertEqual(len(list(draft.drafts)), 1)


if __name__ == "__main__":
    unittest.main()
