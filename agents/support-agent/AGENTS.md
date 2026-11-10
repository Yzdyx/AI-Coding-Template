# support-agent — module instructions

Layer: `Service`. This module answers customer-support questions from the
internal knowledge base and drafts a ticket reply for a human to send.

## Scope

| In scope | Out of scope |
| --- | --- |
| Knowledge-base lookup and answer drafting | Sending a reply to a customer |
| Ticket classification and routing suggestion | Changing a ticket's billing state |
| Prompt and tool ownership for this module | Platform providers |

## Rules

- Depend on interfaces only. Receive the model provider, the state store, the telemetry sink and the approval gate as constructor arguments.
- Never send a message. This agent drafts. A human sends.
- A tool whose risk is `high` stops for approval. The ticket tool is `high` risk for exactly this reason.
- Every side-effecting call carries an idempotency key of the form `<run_id>:<step>:<tool>`.
- Answer only from knowledge-base content. When the content does not cover the question, escalate instead of guessing.
- Never include a credential, an internal hostname or another customer's data in a draft.
- Respect `limits.max_steps` and `limits.timeout_seconds` from `agent.yaml`.

## Files

| File | Role |
| --- | --- |
| `agent.yaml` | Manifest: identity, model, tools, limits, tests |
| `src/main.py` | Service layer: the run loop |
| `prompts/system.md` | Versioned system prompt |
| `tools/ticket_tool.py` | Ticket lookup and draft creation |
| `tests/` | Unit and evaluation tests |

## Checks

```bash
python -m unittest discover -s agents/support-agent/tests -t agents/support-agent -p "test_*.py"
python scripts/check-agent-manifests.py
python scripts/check-architecture.py
```
