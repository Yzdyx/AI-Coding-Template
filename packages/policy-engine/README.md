# @agent-platform/policy-engine

Authorization decisions and feature flags. Layer: `Service`.

## Rules

1. **Fail closed.** A decision engine that cannot evaluate a request returns `deny`. It never returns `allow` by default.
2. The tenant identifier comes from the authenticated subject. A tenant identifier supplied by the caller is ignored.
3. A `high` risk call requires a recorded approval. The engine checks the record, not the caller's claim.
4. Never inline a permission check in an application or an agent. Call this package.
5. Policy source files live in [`../../infra/policies/`](../../infra/policies/).

## Contents

| Symbol | Role |
| --- | --- |
| `PolicyEngine` | Decides whether a tool call is allowed |
| `PolicyRequest` | Input of a decision |
| `FeatureFlagProvider` | Feature flags, injected at the composition root |

## Related

- [`../../infra/policies/agent-tool-access.rego`](../../infra/policies/agent-tool-access.rego)
- [`../../docs/security/security-architecture.md`](../../docs/security/security-architecture.md)
