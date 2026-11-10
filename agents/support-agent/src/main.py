"""support-agent: knowledge-base answering and reply drafting.

Layer: Service. The agent drafts a reply; a human sends it. Every side effect
arrives through an injected interface, so the module runs offline in tests.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

HIGH_RISK = "high"

STATUS_SUCCEEDED = "succeeded"
STATUS_REFUSED = "refused"
STATUS_ESCALATED = "escalated"
STATUS_AWAITING_APPROVAL = "awaiting_approval"
STATUS_STOPPED = "stopped"


@dataclass(frozen=True)
class AgentConfig:
    """Runtime bounds and identity. Values come from the environment."""

    agent_name: str = "support-agent"
    model_name: str = "gpt-5-codex"
    max_steps: int = 16
    timeout_seconds: int = 300
    tenant: str = "tenant-local"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AgentConfig":
        values: Mapping[str, str] = os.environ if env is None else env

        def read_int(key: str, fallback: int) -> int:
            raw = values.get(key, "")
            if raw.strip() == "":
                return fallback
            try:
                return int(raw)
            except ValueError as error:
                raise ValueError(f"{key} must be an integer, received {raw!r}") from error

        return cls(
            agent_name=values.get("AGENT_NAME", "support-agent"),
            model_name=values.get("AGENT_MODEL", "gpt-5-codex"),
            max_steps=read_int("AGENT_MAX_STEPS", 16),
            timeout_seconds=read_int("AGENT_TIMEOUT_SECONDS", 300),
            tenant=values.get("AGENT_TENANT", "tenant-local"),
        )


@dataclass(frozen=True)
class Step:
    """One decision produced by the model provider."""

    kind: str
    tool: str = ""
    arguments: Mapping[str, Any] = field(default_factory=dict)
    answer: str = ""
    reason: str = ""


@dataclass(frozen=True)
class ToolCall:
    """Record of one executed tool call."""

    step: int
    tool: str
    risk: str
    idempotency_key: str
    output: Mapping[str, Any]


@dataclass(frozen=True)
class RunResult:
    """Terminal state of one run."""

    run_id: str
    status: str
    steps: int
    answer: str = ""
    reason: str = ""
    tool_calls: Sequence[ToolCall] = ()


@runtime_checkable
class ModelProvider(Protocol):
    def decide(self, task: str, history: Sequence[Mapping[str, Any]]) -> Step:
        """Return the next step. Must not raise on untrusted input."""


@runtime_checkable
class StateStore(Protocol):
    def read_checkpoint(self, run_id: str) -> Mapping[str, Any] | None:
        """Return the last checkpoint, or None when the run is new."""

    def write_checkpoint(self, run_id: str, step: int, payload: Mapping[str, Any]) -> None:
        """Persist the state needed to resume the run."""


@runtime_checkable
class Telemetry(Protocol):
    def emit(self, event: str, fields: Mapping[str, Any]) -> None:
        """Record one run event."""


@runtime_checkable
class ApprovalGate(Protocol):
    def request(self, run_id: str, tool: str, arguments: Mapping[str, Any]) -> bool:
        """Return True only when a human approved this exact action."""


@runtime_checkable
class Tool(Protocol):
    name: str
    risk: str

    def call(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        """Execute the tool. Input is validated inside the tool."""


class SupportAgent:
    """The support run loop.

    The agent answers from the knowledge base and drafts a reply. Sending is out
    of scope: `draft_reply` is `high` risk and stops for approval.
    """

    def __init__(
        self,
        config: AgentConfig,
        model: ModelProvider,
        store: StateStore,
        tools: Sequence[Tool],
        telemetry: Telemetry,
        approvals: ApprovalGate,
        declared_tools: Sequence[str] | None = None,
    ) -> None:
        self._config = config
        self._model = model
        self._store = store
        self._tools = {tool.name: tool for tool in tools}
        self._telemetry = telemetry
        self._approvals = approvals
        self._declared = frozenset(declared_tools if declared_tools is not None else self._tools)

    @property
    def config(self) -> AgentConfig:
        return self._config

    def run(self, task: str, run_id: str) -> RunResult:
        checkpoint = self._store.read_checkpoint(run_id)
        history: list[dict[str, Any]] = list(checkpoint["history"]) if checkpoint else []
        start_step = int(checkpoint["step"]) + 1 if checkpoint else 0
        executed: list[ToolCall] = []

        self._telemetry.emit("run_started", {"run_id": run_id, "agent": self._config.agent_name})

        for step_index in range(start_step, self._config.max_steps):
            decision = self._model.decide(task, history)

            if decision.kind == "refuse":
                self._telemetry.emit(
                    "run_refused", {"run_id": run_id, "step": step_index, "reason": decision.reason}
                )
                return RunResult(
                    run_id=run_id,
                    status=STATUS_REFUSED,
                    steps=step_index + 1,
                    reason=decision.reason,
                    tool_calls=tuple(executed),
                )

            if decision.kind == "escalate":
                self._telemetry.emit(
                    "run_escalated", {"run_id": run_id, "step": step_index, "reason": decision.reason}
                )
                return RunResult(
                    run_id=run_id,
                    status=STATUS_ESCALATED,
                    steps=step_index + 1,
                    reason=decision.reason,
                    tool_calls=tuple(executed),
                )

            if decision.kind == "final":
                self._store.write_checkpoint(run_id, step_index, {"history": history, "done": True})
                return RunResult(
                    run_id=run_id,
                    status=STATUS_SUCCEEDED,
                    steps=step_index + 1,
                    answer=decision.answer,
                    tool_calls=tuple(executed),
                )

            tool = self._tools.get(decision.tool)
            if tool is None or decision.tool not in self._declared:
                self._telemetry.emit(
                    "tool_denied",
                    {"run_id": run_id, "step": step_index, "tool": decision.tool},
                )
                history.append({"step": step_index, "tool_denied": decision.tool})
                self._store.write_checkpoint(run_id, step_index, {"history": history})
                continue

            idempotency_key = f"{run_id}:{step_index}:{tool.name}"

            if tool.risk == HIGH_RISK:
                if not self._approvals.request(run_id, tool.name, decision.arguments):
                    self._telemetry.emit(
                        "approval_required",
                        {"run_id": run_id, "step": step_index, "tool": tool.name},
                    )
                    return RunResult(
                        run_id=run_id,
                        status=STATUS_AWAITING_APPROVAL,
                        steps=step_index + 1,
                        reason=f"tool {tool.name} requires human approval",
                        tool_calls=tuple(executed),
                    )

            output = tool.call(decision.arguments)
            executed.append(
                ToolCall(
                    step=step_index,
                    tool=tool.name,
                    risk=tool.risk,
                    idempotency_key=idempotency_key,
                    output=output,
                )
            )
            history.append({"step": step_index, "tool": tool.name, "output": dict(output)})
            self._store.write_checkpoint(run_id, step_index, {"history": history})
            self._telemetry.emit(
                "tool_called",
                {
                    "run_id": run_id,
                    "step": step_index,
                    "tool": tool.name,
                    "risk": tool.risk,
                    "idempotency_key": idempotency_key,
                },
            )

        self._telemetry.emit("run_stopped", {"run_id": run_id, "reason": "max_steps"})
        return RunResult(
            run_id=run_id,
            status=STATUS_STOPPED,
            steps=self._config.max_steps,
            reason="max_steps",
            tool_calls=tuple(executed),
        )
