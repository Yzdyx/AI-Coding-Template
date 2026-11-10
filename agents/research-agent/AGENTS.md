# research-agent — module instructions

Layer: `Service`. This module answers research questions by retrieving documents
and synthesising an answer. It owns its prompts, its tools and its tests.

## Scope

| In scope | Out of scope |
| --- | --- |
| Retrieval planning, synthesis, degradation on a slow upstream | HTTP routing, process lifecycle |
| Tool implementations under `tools/` | Platform providers under `packages/` |
| Prompt versions under `prompts/` | Shared contracts under `schemas/` |

## Rules

- Depend on interfaces only. Receive `ModelProvider`, `StateStore`, `Telemetry` and the approval gate as constructor arguments.
- Never instantiate a provider here. Composition happens in `apps/worker/src/index.ts`.
- Write a checkpoint after every step. A resumed run must not repeat a completed side effect.
- Every side-effecting tool call carries an idempotency key of the form `<run_id>:<step>:<tool>`.
- A tool whose risk is `high` stops for approval before it runs.
- A tool absent from `agent.yaml` is denied. Do not add a fallback that calls it anyway.
- Respect `limits.max_steps` and `limits.timeout_seconds`. Stop and record a run event at the bound.
- A degraded result is marked. Never return a partial result as a complete one.

## Files

| File | Role |
| --- | --- |
| `agent.yaml` | Manifest: identity, model, tools, limits, tests |
| `src/main.py` | Service layer: the run loop |
| `prompts/system.md` | Versioned system prompt |
| `tools/` | Tool implementations |
| `workflows/retrieval.yaml` | Orchestration graph |
| `tests/` | Unit, integration, evaluation and safety tests |

## Checks

```bash
python -m unittest discover -s agents/research-agent/tests -t agents/research-agent -p "test_*.py"
python scripts/check-agent-manifests.py
python scripts/check-architecture.py
```
