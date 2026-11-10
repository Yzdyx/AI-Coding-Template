# @agent-platform/admin-console

Operator console for agent runs, approvals and policy state.

- Layer: `UI`.
- Runtime: Node 22 or newer.

## Responsibilities

| In scope | Out of scope |
| --- | --- |
| Render run state and the approval queue | Business rules |
| Forward an operator decision to the Runtime layer | Authorization decisions |
| Show a degraded result as degraded | Data access |

## Rules

- Import `Types` and `Runtime` interfaces only. Never import `Service`, `Repo` or `Config`.
- Never handle a secret, a token or a credential.
- A destructive action requires an explicit confirmation step.

## Scripts

| Command | Purpose |
| --- | --- |
| `pnpm --filter @agent-platform/admin-console typecheck` | Type check |
| `pnpm --filter @agent-platform/admin-console lint` | Static check |
| `pnpm --filter @agent-platform/admin-console test` | Unit tests |

## Related documents

- [`../../AGENTS.md`](../../AGENTS.md)
- [`../../docs/FRONTEND.md`](../../docs/FRONTEND.md)
- [`../../docs/architecture/dependency-rules.md`](../../docs/architecture/dependency-rules.md)
