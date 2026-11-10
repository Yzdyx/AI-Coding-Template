"""research-agent: retrieval and synthesis service.

Layer: Service. Business rules and orchestration live here. Every side effect
arrives through an injected interface: the model provider, the state store, the
telemetry sink, the approval gate and the tool set. This module opens no network
connection by itself, so it runs offline in tests.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

HIGH_RISK = "high"

STATUS_SUCCEEDED = "succeeded"
STATUS_REFUSED = "refused"
STATUS_AWAITING_APPROVAL = "awaiting_approval"
STATUS_STOPPED = "stopped"


@dataclass(frozen=True)
class AgentConfig:
    """Runtime bounds and identity. Values come from the environment."""

    agent_name: str = "research-agent"
    model_name: str = "gpt-5-codex"
    max_steps: int = 24
    timeout_seconds: int = 600
    tenant: str = "tenant-local"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "AgentConfig":
        """Read configuration from the environment. A malformed integer fails closed."""
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
            agent_name=values.get("AGENT_NAME", "research-agent"),
            model_name=values.get("AGENT_MODEL", "gpt-5-codex"),
            max_steps=read_int("AGENT_MAX_STEPS", 24),
            timeout_seconds=read_int("AGENT_TIMEOUT_SECONDS", 600),
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
    degraded: bool = False
    tool_calls: Sequence[ToolCall] = ()


@runtime_checkable
class ModelProvider(Protocol):
    """Decides the next step. Implemented by an adapter, injected by the runtime."""

    def decide(self, task: str, history: Sequence[Mapping[str, Any]]) -> Step:
        """Return the next step. Must not raise on untrusted input."""


@runtime_checkable
class StateStore(Protocol):
    """Durable run state. Backed by packages/state-store in production."""

    def read_checkpoint(self, run_id: str) -> Mapping[str, Any] | None:
        """Return the last checkpoint, or None when the run is new."""

    def write_checkpoint(self, run_id: str, step: int, payload: Mapping[str, Any]) -> None:
        """Persist the state needed to resume the run."""


@runtime_checkable
class Telemetry(Protocol):
    """Run events. Backed by packages/observability in production."""

    def emit(self, event: str, fields: Mapping[str, Any]) -> None:
        """Record one run event."""


@runtime_checkable
class ApprovalGate(Protocol):
    """Human approval for a high-risk action."""

    def request(self, run_id: str, tool: str, arguments: Mapping[str, Any]) -> bool:
        """Return True only when a human approved this exact action."""


@runtime_checkable
class Tool(Protocol):
    """A callable capability declared in the manifest."""

    name: str
    risk: str

    def call(self, arguments: Mapping[str, Any]) -> Mapping[str, Any]:
        """Execute the tool. Input is validated inside the tool."""


class ResearchAgent:
    """The research run loop.

    The loop is deliberately small: read the checkpoint, ask the model for one
    step, gate the step, execute it, checkpoint, repeat. Every side effect is
    keyed by an idempotency key so a resumed run cannot repeat it.
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
        """Run the agent until it finishes, refuses, stops or needs approval."""
        checkpoint = self._store.read_checkpoint(run_id)
        history: list[dict[str, Any]] = list(checkpoint["history"]) if checkpoint else []
        start_step = int(checkpoint["step"]) + 1 if checkpoint else 0
        executed: list[ToolCall] = []
        degraded = False

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

            if decision.kind == "final":
                self._store.write_checkpoint(run_id, step_index, {"history": history, "done": True})
                self._telemetry.emit("run_finished", {"run_id": run_id, "step": step_index})
                return RunResult(
                    run_id=run_id,
                    status=STATUS_SUCCEEDED,
                    steps=step_index + 1,
                    answer=decision.answer,
                    degraded=degraded,
                    tool_calls=tuple(executed),
                )

            tool = self._tools.get(decision.tool)
            if tool is None or decision.tool not in self._declared:
                # A tool outside the manifest is denied, not improvised.
                self._telemetry.emit(
                    "tool_denied",
                    {"run_id": run_id, "step": step_index, "tool": decision.tool},
                )
                history.append({"step": step_index, "tool_denied": decision.tool})
                self._store.write_checkpoint(run_id, step_index, {"history": history})
                continue

            idempotency_key = f"{run_id}:{step_index}:{tool.name}"

            if tool.risk == HIGH_RISK:
                approved = self._approvals.request(run_id, tool.name, decision.arguments)
                if not approved:
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
            if output.get("degraded") is True:
                degraded = True

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
                    "degraded": output.get("degraded", False),
                },
            )

        self._telemetry.emit("run_stopped", {"run_id": run_id, "reason": "max_steps"})
        return RunResult(
            run_id=run_id,
            status=STATUS_STOPPED,
            steps=self._config.max_steps,
            reason="max_steps",
            degraded=degraded,
            tool_calls=tuple(executed),
        )


def build_agent(
    config: AgentConfig,
    model: ModelProvider,
    store: StateStore,
    tools: Sequence[Tool],
    telemetry: Telemetry,
    approvals: ApprovalGate,
    declared_tools: Sequence[str] | None = None,
) -> ResearchAgent:
    """Composition helper for callers that already hold the interfaces."""
    return ResearchAgent(config, model, store, tools, telemetry, approvals, declared_tools)
