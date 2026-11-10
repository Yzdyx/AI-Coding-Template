# @agent-platform/eval-kit

Evaluation harness. Layer: `Service`.

## Rules

1. A case states an expected value. A case with no assertion is documentation, not a test.
2. A failure report names the case id, the input, the expected value and the actual value. A score alone is not a report.
3. A model-graded score never decides a release on its own. Pair it with a deterministic assertion.
4. A safety case that cannot be evaluated is `blocked`, never `passed`.
5. Never edit a case to make a run pass. Add a case, or change the baseline with approval.

## Contents

| Symbol | Role |
| --- | --- |
| `EvalCase` | One case: id, input, expectation |
| `EvalResult` | Outcome: `passed`, `failed`, `blocked` |
| `runSuite` | Runs cases through an injected runner |

## Related

- [`../../evals/README.md`](../../evals/README.md)
- [`../../evals/baselines/baseline-2026-01.json`](../../evals/baselines/baseline-2026-01.json)
- [`../../.agents/skills/release-check/SKILL.md`](../../.agents/skills/release-check/SKILL.md)
