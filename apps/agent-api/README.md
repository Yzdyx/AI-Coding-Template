# agent-api

HTTP entry point for the enterprise agent platform. It exposes the platform
API that the admin console, internal services, and external clients call.

Layer: **Runtime**. It sits above `Config`, `Repo`, `Service`, and `Types` and
below `UI`, following the dependency direction declared in `ARCHITECTURE.md`.

## Purpose

- Terminate HTTP, resolve the caller identity, and enforce policy before any
  work is accepted.
- Expose the agent registry, run status, run events, and the human approval
  queue as a small, stable JSON surface.
- Accept new runs with a caller-supplied idempotency key so a retried request
  never starts a duplicate run.
- Own process lifecycle: configuration load, server start, and graceful
  shutdown with a bounded drain window.

The service contains no business rules. Policy, persistence, telemetry, and
identity enter through the Provider interfaces implemented in `packages/`.

## Entry points

| File | Role |
| --- | --- |
| `src/index.ts` | Runtime entry point. Loads configuration, starts the server, installs `SIGINT`/`SIGTERM` handlers, drains in-flight requests. |
| `src/server.ts` | Request routing layer. Declares the handler types, builds the route table, and owns transport concerns only. |

## API surface

All routes are served under `AGENT_API_BASE_PATH` (default `/api/v1`).

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/healthz` | Liveness probe. Returns the service name and the current time. |
| `GET` | `/agents` | List registered agent manifests. |
| `GET` | `/agents/:agentId` | Read one agent manifest. |
| `GET` | `/runs` | List runs, optionally filtered by `status`. |
| `POST` | `/runs` | Create a run. Requires `agentId` and `idempotencyKey`. |
| `GET` | `/runs/:runId` | Read a run with its checkpoints. |
| `GET` | `/runs/:runId/events` | Read the run event stream after a sequence number. |
| `GET` | `/approvals` | List approval requests, filtered by `status`. |
| `POST` | `/approvals/:approvalId/decision` | Record a human approval decision. |

## Environment variables

Values are placeholders only. The repository holds no real credentials, keys,
or internal addresses.

| Variable | Required | Default | Meaning |
| --- | --- | --- | --- |
| `AGENT_API_HOST` | no | `0.0.0.0` | Bind address. |
| `AGENT_API_PORT` | no | `8080` | Bind port. |
| `AGENT_API_BASE_PATH` | no | `/api/v1` | Route prefix. |
| `AGENT_API_REQUIRE_AUTH` | no | `true` | Reject unauthenticated requests. |
| `AGENT_API_SHUTDOWN_TIMEOUT_MS` | no | `10000` | Drain window before a forced exit. |
| `AGENT_STATE_STORE_URL` | yes | none | State store endpoint, for example `${AGENT_STATE_STORE_URL}`. |
| `AGENT_MODEL_PROVIDER_URL` | yes | none | Model provider endpoint, for example `${AGENT_MODEL_PROVIDER_URL}`. |
| `AGENT_POLICY_BUNDLE` | no | `default` | Policy bundle name loaded at start-up. |
| `AGENT_IDENTITY_ISSUER` | no | `https://identity.example.com` | Identity issuer used to resolve principals. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | no | `https://telemetry.example.com` | Telemetry collector endpoint. |

## Run

```bash
# Install workspace dependencies from the repository root.
npm install

# Type-check, compile, and emit declarations into dist/.
npm run build

# Start the service.
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
