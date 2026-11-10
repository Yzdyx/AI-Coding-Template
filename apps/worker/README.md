# worker

Background worker for the enterprise agent platform. It claims agent tasks
from the shared queue, drives one run to completion, writes a checkpoint after
every step, and releases the task lock.

Layer: **Runtime**. It sits above `Config`, `Repo`, `Service`, and `Types`
following the dependency direction declared in `ARCHITECTURE.md`.

## Purpose

- Claim exactly one task per loop iteration, under a bounded lease.
- Run the agent through the `ModelProvider`, then execute each planned tool
  call through the `ConnectorProvider`.
- Write a checkpoint after every step so a crash resumes instead of replaying
  the whole run.
- Stop at a human approval checkpoint when the policy engine classifies a step
  as high-risk or irreversible, then hand the lock back.
- Guarantee that a retry never repeats an external side effect.

## Correctness properties

| Property | How it is achieved |
| --- | --- |
| Idempotent side effects | Every step carries a deterministic idempotency key, `${runId}:${stepId}`. Before invoking a tool the worker looks the key up in the operation log. A hit means the effect already happened, so the stored result is reused and the tool is not called again. |
| Crash-safe recovery | The worker loads the latest checkpoint, resumes at its `stepIndex`, and skips steps whose idempotency key is already recorded. |
| Human approval gate | A policy decision of `require_approval` creates an `ApprovalRequest`, writes an `awaiting_approval` checkpoint, and returns without performing the side effect. The queue does not re-offer a paused run, so a pending approval cannot hot-loop. |
| Deterministic re-planning | The planning model call uses the key `${runId}:plan`, so a resumed run derives the same plan. |
| Bounded lease | A task is claimed with a lease. A worker that dies mid-task loses the lease and the task becomes claimable again. |

Checkpoints are not transactions. If the process dies after an external side
effect and before the checkpoint is written, recovery may attempt that step
again, which is why the idempotency key is written before the tool result is
committed.

## Entry points

| File | Role |
| --- | --- |
| `src/index.ts` | Worker Runtime entry point. Configuration load, queue loop, per-task processing, dependency assembly, graceful shutdown. |

## Task lifecycle

```
claim  ->  load checkpoint  ->  plan (idempotent)
       ->  for each step:
             idempotency lookup  ->  policy decision
             ->  require_approval: create approval, checkpoint, release lock
             ->  allow: invoke connector, log result, checkpoint
       ->  complete task  ->  release lock
```

## Environment variables

Values are placeholders only. The repository holds no real credentials, keys,
or internal addresses.

| Variable | Required | Default | Meaning |
| --- | --- | --- | --- |
| `WORKER_ID` | no | `worker-${HOSTNAME}-${PID}` | Stable worker identity used for task leases. |
| `WORKER_POLL_INTERVAL_MS` | no | `1000` | Idle delay between claim attempts. |
| `WORKER_LEASE_MS` | no | `60000` | Task lease duration. |
| `WORKER_MAX_ATTEMPTS` | no | `3` | Attempts before a task is parked as failed. |
| `WORKER_SHUTDOWN_TIMEOUT_MS` | no | `30000` | Time allowed for the current task to finish. |
| `AGENT_STATE_STORE_URL` | yes | none | State store endpoint, for example `${AGENT_STATE_STORE_URL}`. |
| `AGENT_MODEL_PROVIDER_URL` | yes | none | Model provider endpoint, for example `${AGENT_MODEL_PROVIDER_URL}`. |
| `AGENT_CONNECTOR_ENDPOINT` | yes | none | Connector provider endpoint, for example `${AGENT_CONNECTOR_ENDPOINT}`. |
| `AGENT_POLICY_BUNDLE` | no | `default` | Policy bundle name loaded at start-up. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | no | `https://telemetry.example.com` | Telemetry collector endpoint. |

## Run

```bash
# Install workspace dependencies from the repository root.
npm install

# Type-check, compile, and emit declarations into dist/.
npm run build

# Start one worker process.
node dist/index.js
```

Development loop (rebuild on change):

```bash
npm run dev
```

Checks:

```bash
npm run lint
npm test
```
