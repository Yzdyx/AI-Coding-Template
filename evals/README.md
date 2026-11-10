# Evaluation Assets

This directory holds every artifact used to judge agent behavior. A change to an
agent is not complete until its evaluation runs against these assets.

## Layout

| Path | Content |
| --- | --- |
| `shared-datasets/` | Datasets reused across agents |
| `regression/` | Suites that must not regress |
| `safety/` | Adversarial and red-line suites |
| `baselines/` | Approved thresholds and version records |

## The four evaluation levels

| Level | Question | Runs where |
| --- | --- | --- |
| L1 Deterministic | Does the software behave as specified? | Unit, contract and architecture checks |
| L2 Behavior | Does the agent complete the task, choose the right tool, with the right arguments? | `regression/` |
| L3 Safety | Does the agent resist injection, refuse out-of-scope actions, respect tenant isolation? | `safety/` |
| L4 System | Does it recover, stay inside latency and cost budgets, survive a dependency failure? | Staging and production |

## Rules

1. A dataset is versioned. A change to a dataset is a change to the baseline.
2. A threshold change requires approval from the owning team and `@quality-team`.
3. A model-graded score alone never decides a release. Pair it with a deterministic assertion.
4. A failing safety case blocks the change. There is no exception path.
5. Record the dataset, evaluator and baseline identifiers with every result.

## Related

- [`baselines/baseline-2026-01.json`](baselines/baseline-2026-01.json)
- [`../.agents/skills/release-check/SKILL.md`](../.agents/skills/release-check/SKILL.md)
- [`../docs/QUALITY_SCORE.md`](../docs/QUALITY_SCORE.md)
