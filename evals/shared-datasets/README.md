# Shared Datasets

Datasets in this directory are reused by more than one agent. An agent-specific
dataset stays under `agents/<name>/tests/eval/`.

## Datasets

| File | Agent | Cases | Origin | Last reviewed |
| --- | --- | --- | --- | --- |
| [`retrieval-smoke.jsonl`](retrieval-smoke.jsonl) | `research-agent` | 4 | Written for the smoke suite in `../regression/smoke.yaml` | 2026-01 |

## Format

One JSON Lines file per dataset. One case per line.

```json
{"id": "retrieval-001", "input": {"query": "quarterly revenue"}, "expect": {"tools": ["search"], "status": "succeeded"}}
```

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Stable case identifier. Never reuse an identifier for a new case |
| `input` | yes | The task input handed to the agent |
| `expect.tools` | no | Tool names the run must call, in order when the order matters |
| `expect.status` | no | The expected terminal status |
| `expect.degraded` | no | Whether a degraded result is acceptable |
| `tags` | no | Free-form labels for filtering, for example `slow-upstream` |

## Rules

1. Never edit a case in place to make a run pass. Add a case, or change the baseline with approval.
2. A case with no assertion is documentation, not a test. Remove it or add an assertion.
3. Every dataset records its origin and the date it was last reviewed.
