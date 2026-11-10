# agent-api — module instructions

Layer: `Runtime`. This module is a composition root: it wires providers, exposes the HTTP API and manages the process lifecycle.

## Rules

- Business rules do not live here. Put them in `packages/` or in `agents/<name>/src/`.
- This is one of the two allowed places to construct a provider instance. The other is `apps/worker/src/index.ts`.
- Load and validate configuration once, at start-up. Fail closed on a missing required value.
- Never log a request body, a token or a header that may hold a secret.
- Authorize through `packages/policy-engine/`. Do not inline a permission check.

## Files

| File | Role |
| --- | --- |
| `src/index.ts` | Configuration loading, start-up, graceful shutdown |
| `src/server.ts` | HTTP surface, routing, request validation |

## Checks

```bash
pnpm --filter @agent-platform/agent-api test
pnpm --filter @agent-platform/agent-api typecheck
python scripts/check-architecture.py
```

## Contracts

- The OpenAPI document is the source of truth. Update it in the same pull request as the code.
- Request and response bodies validate against `schemas/`.
- A state-changing endpoint requires an `Idempotency-Key` header.
