# worker — module instructions

Layer: `Runtime`. This module claims tasks, runs them and checkpoints progress.

## Rules

- Business rules do not live here. The worker drives `Service`-layer code; it does not implement it.
- This is one of the two allowed places to construct a provider instance.
- Every task claim is atomic. Two workers must never own the same task.
- Write a checkpoint after every step. A resumed run must not repeat a completed side effect.
- Every side-effecting tool call carries an idempotency key.
- A high-risk tool call stops for human approval before it executes.
- Respect `limits.max_steps` and `limits.timeout_seconds` from the agent manifest. Stop and record a run event when either bound is exceeded.

## Files

| File | Role |
| --- | --- |
| `src/index.ts` | Task loop, scheduling, composition root |

## Checks

```bash
pnpm --filter @agent-platform/worker test
pnpm --filter @agent-platform/worker typecheck
python scripts/check-architecture.py
```

## Failure handling

- A failed step is recorded as a run event. Do not swallow it.
- A run that exceeds a bound is stopped, not extended.
- A crash after an external side effect may repeat that side effect. Use an idempotency key or a compensating action.
