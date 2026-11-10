# Quality Gates

Every gate below is required unless the task metadata marks it `not_applicable`.

| Gate | Command | Blocks merge | Owner |
| --- | --- | --- | --- |
| Architecture | `python scripts/check-architecture.py` | Yes | `@architecture-team` |
| Agent manifests | `python scripts/check-agent-manifests.py` | Yes | `@platform-team` |
| Documentation links | `python scripts/check-doc-links.py` | Yes | `@platform-team` |
| Unit and contract tests | `pnpm -r test` | Yes | Module owner |
| Type check | `pnpm -r typecheck` | Yes | Module owner |
| Agent evaluation | `.github/workflows/eval.yml` | Yes for a behavior change | `@quality-team` |
| Safety evaluation | `evals/safety/` | Yes for a tool or prompt change | `@security-team` |
| Release review | `.agents/skills/release-check/SKILL.md` | Yes for a release | `@sre-team` |

## Evidence rules

1. Paste the command and its real output. A summary is not evidence.
2. A skipped gate is reported as skipped, with the reason and the approver.
3. A gate that could not run is reported as `blocked`. Blocked is not passed.
4. A gate result older than the last commit on the branch is stale. Re-run it.

## Known non-gates

- A model-graded score alone never decides a merge. Combine it with a deterministic assertion.
- A green run on an unrelated package does not clear a change in another package.
