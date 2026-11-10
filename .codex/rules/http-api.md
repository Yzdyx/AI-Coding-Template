# HTTP API Rules

Applies to `apps/agent-api/**`.

## Contract
- The OpenAPI document is the source of truth. Update it in the same PR as the code.
- Additive changes only within a major version. Never change a field meaning in place.
- Every request and response body is validated against a JSON Schema in `schemas/`.

## Requests
- Require an `Idempotency-Key` header on every state-changing endpoint.
- Propagate a `traceparent` header. Generate one when it is missing.
- Reject unknown fields instead of ignoring them.

## Responses
- Errors use one shape: `code`, `message`, `trace_id`, `details`.
- Never return a stack trace or an internal path.
- Return `429` with `Retry-After` when a rate limit is hit.

## Security
- Authenticate every endpoint. Deny by default.
- Authorize through `packages/policy-engine/`. Do not inline a permission check.
- Never log a request body that may hold a secret.
