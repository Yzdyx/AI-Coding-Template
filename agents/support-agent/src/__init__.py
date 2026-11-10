"""Public surface of the support agent.

Cross-module consumers import these symbols. Do not import from the
implementation module directly.
"""

from .main import (
    AgentConfig,
    ApprovalGate,
    ModelProvider,
    RunResult,
    StateStore,
    Step,
    SupportAgent,
    Telemetry,
    Tool,
    ToolCall,
)

__all__ = [
    "AgentConfig",
    "ApprovalGate",
    "ModelProvider",
    "RunResult",
    "StateStore",
    "Step",
    "SupportAgent",
    "Telemetry",
    "Tool",
    "ToolCall",
]
