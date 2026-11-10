# Architecture

This document defines system boundaries, module layers, and dependency
direction. Read it before any cross-module change. Update it in the same pull
request as the architecture change it describes.

## 1. Scope

This repository hosts one enterprise agent platform. It contains two systems
that share one repository but keep separate responsibilities.

| System | Purpose | Main directories |
| --- | --- | --- |
| Coding-agent engineering system | Let coding agents understand, change, verify, and maintain this repository | `AGENTS.md`, `ARCHITECTURE.md`, `docs/`, `.agents/`, `.codex/`, `.github/`, `scripts/` |
| Runtime agent application system | Run business agents as production services | `agents/`, `apps/`, `packages/`, `schemas/`, `evals/`, `infra/`, `tests/` |

The two systems must not share directory responsibilities. A coding-agent
instruction file is not a business agent definition.

## 2. System Context

```
        +---------------------+        +----------------------+
        |  Coding agents      |        |  Human engineers     |
        |  (Codex, Copilot)   |        |  (review, approval)  |
        +----------+----------+        +----------+-----------+
                   |                              |
                   |  repository knowledge        |  review, approval
                   v                              v
        +---------------------------------------------------+
        |              Enterprise agent platform            |
        |  apps/        agents/        packages/             |
        +----+----------------+---------------+-------------+
             |                |               |
             v                v               v
        +---------+     +-----------+   +---------------+
        | Gateway |     | State     |   | Observability |
        | policy  |     | store     |   | traces, logs  |
        +---------+     +-----------+   +---------------+
             |                |               |
             v                v               v
        +---------------------------------------------------+
        |        External systems: model APIs, tools,        |
        |        data sources, customer systems              |
        +---------------------------------------------------+
```

## 3. Module Layers

Business code is divided into six fixed layers. The order below is the allowed
dependency direction.

| Layer | Responsibility | Example location |
| --- | --- | --- |
| `Types` | Data shapes, schemas, enums. No behavior. | `packages/agent-contracts/src/types.ts` |
| `Config` | Configuration loading and validation. | `packages/state-store/src/config.ts` |
| `Repo` | Persistence and external I/O. | `packages/state-store/src/repository.ts` |
| `Service` | Business rules and orchestration. | `agents/research-agent/src/main.py` |
| `Runtime` | Process entry, scheduling, lifecycle. | `apps/worker/src/index.ts` |
| `UI` | Presentation and user interaction. | `apps/admin-console/src/index.tsx` |

A layer may depend only on layers below it. `Types` depends on nothing inside
the platform. `UI` depends on `Runtime` and `Types`.

Cross-domain capabilities do not enter through a layer. They enter through an
explicit Provider interface:

| Capability | Provider interface | Implementation location |
| --- | --- | --- |
| Identity | `IdentityProvider` | `packages/tool-adapters/src/identity.ts` |
| External connectors | `ConnectorProvider` | `packages/tool-adapters/src/connector.ts` |
| Telemetry | `TelemetryProvider` | `packages/observability/src/provider.ts` |
| Feature flags | `FeatureFlagProvider` | `packages/policy-engine/src/flags.ts` |
| Model access | `ModelProvider` | `packages/tool-adapters/src/model.ts` |

The full rule set, including allowed import paths and forbidden edges, is in
`docs/architecture/dependency-rules.md`.

## 4. Enforced Constraints

Intent lives in documents. Enforcement lives in automation. Every rule below
has a machine check.

| Constraint | Check | Location |
| --- | --- | --- |
| Layer dependency direction | Architecture check | `scripts/check-architecture.py` |
| Agent manifest validity | Manifest check | `scripts/check-agent-manifests.py` |
| Document links and indexes | Link check | `scripts/check-doc-links.py` |
| Public interface compatibility | Contract tests | `tests/contracts/` |
| Tool input and output shapes | JSON Schema | `schemas/tool-contracts/` |
| Code formatting and lint | CI workflow | `.github/workflows/pull-request.yml` |

A rule that matters must have a check. A rule without a check is a suggestion.

## 5. Agent Runtime Architecture

Each business agent is an isolated module with the same internal layout.

```
agents/<agent-name>/
├── AGENTS.md          # local instructions for coding agents
├── agent.yaml         # manifest: identity, model, tools, limits, owner
├── src/               # Service layer implementation
├── prompts/           # versioned prompt files
├── tools/             # agent-specific tool implementations
├── workflows/         # orchestration graphs, when the agent has one
└── tests/             # unit, integration, eval, safety
```

Runtime requirements for every agent:

| Requirement | Reason |
| --- | --- |
| Persistent state and checkpoints | A failed run resumes without full re-execution |
| Idempotent tool calls | A retry must not repeat a payment, send, or delete |
| Tool authorization gateway | The agent cannot bypass permission policy |
| Human approval node | Irreversible and high-risk actions stop for a human |
| End-to-end trace | Model, tool, and workflow failures are locatable |
| Version rollback | A quality regression restores a verified version |

Checkpoints are not transactions. If an agent crashes after an external side
effect, recovery may repeat that side effect. Use idempotency keys, operation
logs, or compensating actions.

## 6. Contracts

- Shared shapes live in `packages/agent-contracts/`. They are versioned and
  reviewed by the architecture team.
- JSON Schemas live in `schemas/`. `schemas/agent-manifest.schema.json`
  validates every `agent.yaml`.
- Tool contracts live in `schemas/tool-contracts/`.
- A breaking contract change requires an ADR in `docs/architecture/adr/`.
- Producers and consumers must tolerate additive fields.

## 7. Data and State

| State type | Storage | Lifetime |
| --- | --- | --- |
| Run checkpoints | `state-store` provider | Until run completion plus retention window |
| Conversation memory | `state-store` provider | Per policy retention |
| Evaluation artifacts | `evals/` and object storage | Per baseline policy |
| Traces and logs | Observability backend | Per retention policy |

Production deployments use external persistence. In-process state is for local
development only.

## 8. Failure Domains

| Domain | Failure impact | Isolation |
| --- | --- | --- |
| One business agent | That agent's tasks fail | Separate module, separate deploy unit |
| Shared contract package | All consumers | Versioned releases, contract tests |
| Policy engine | All tool calls | Fail closed |
| State store | Run recovery | Replicated external storage |
| Model provider | All agents | Provider abstraction, fallback model |

## 9. Evolution Rules

- Promote a module to a separate service only when it needs independent
  deployment, permissions, failure domain, or scaling. Do not split an agent
  into a microservice just because the agent count grows.
- Add a directory only when something real goes into it. Do not create empty
  structure for unused capability.
- Keep the repository root small. Add a new top-level directory only when no
  existing top-level directory owns the responsibility.
- Record every architecture decision in `docs/architecture/adr/`.
