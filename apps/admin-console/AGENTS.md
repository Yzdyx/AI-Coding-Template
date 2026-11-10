# admin-console — module instructions

Layer: `UI`. This module shows agent runs, approvals and policy state to operators.

## Rules

- Presentation only. No business rule, no authorization decision, no data access.
- Import `Types` and `Runtime` interfaces only. Never import `Service`, `Repo` or `Config`.
- Every capability the console needs is exposed by the `Runtime` layer as an explicit interface.
- Never handle a secret, a token or a credential in this module.
- Show a degraded result as degraded. Never render a partial result as complete.

## Files

| File | Role |
| --- | --- |
| `src/index.tsx` | Console entry, run list and approval queue |

## Checks

```bash
pnpm --filter @agent-platform/admin-console test
pnpm --filter @agent-platform/admin-console typecheck
python scripts/check-architecture.py
```

## Accessibility

- Every interactive control is reachable by keyboard.
- Every status is conveyed by text, not by color alone.
- A destructive action requires an explicit confirmation step.
