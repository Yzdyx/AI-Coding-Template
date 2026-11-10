# @agent-platform/agent-contracts

Shared types for the platform. Layer: `Types`.

## Rules

1. No behaviour. No I/O. No import from any other layer.
2. Every type here is a contract. A change needs review by `@architecture-team`.
3. A breaking change needs an ADR. An additive change needs a schema update in `schemas/`.
4. Consumers read the fields they know and preserve the fields they do not.

## Contents

| Type | Used by |
| --- | --- |
| `RunStatus`, `RunRecord`, `AgentRunSummary` | `apps/agent-api`, `apps/worker`, `apps/admin-console` |
| `RunCheckpoint`, `AgentEvent` | `apps/worker`, `apps/agent-api` |
| `ApprovalRequest`, `ApprovalStatus` | Approval queue, `apps/admin-console` |
| `TaskEnvelope` | `apps/worker` |
| `ToolInvocation`, `ToolResult`, `RiskLevel` | Tool gateway, `packages/tool-adapters` |
| `AgentManifest` | `scripts/check-agent-manifests.py` contract, `apps/worker` |
| `PolicyDecision`, `PolicyEffect` | `packages/policy-engine` |
| `ModelMessage` | `packages/tool-adapters` |

## Related

- [`../../schemas/agent-manifest.schema.json`](../../schemas/agent-manifest.schema.json)
- [`../../docs/architecture/dependency-rules.md`](../../docs/architecture/dependency-rules.md)
