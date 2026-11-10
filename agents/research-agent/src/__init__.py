"""Public surface of the research agent.

Cross-module consumers import these symbols. Do not import from
`agents.research-agent.src.main` directly: the module path is an implementation
detail, and a hyphen in a path is not a valid Python identifier anyway.
"""

from .main import (
    AgentConfig,
    ApprovalGate,
    ModelProvider,
    ResearchAgent,
    RunResult,
    StateStore,
    Step,
    Telemetry,
    Tool,
    ToolCall,
)

__all__ = [
    "AgentConfig",
    "ApprovalGate",
    "ModelProvider",
    "ResearchAgent",
    "RunResult",
    "StateStore",
    "Step",
    "Telemetry",
    "Tool",
    "ToolCall",
]
