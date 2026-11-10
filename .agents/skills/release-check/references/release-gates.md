# Release Gates

| Gate | Rule | Evidence required |
| --- | --- | --- |
| Unit and contract tests | All pass | CI run URL |
| Critical behavior evaluation | Not below the approved baseline | Evaluation report |
| Safety red-line cases | No unapproved privilege escalation | Safety report |
| Task completion rate | Compared with the current production version, with a confidence statement | Evaluation report |
| P95 latency | Within the performance budget | Load test output |
| Cost per task | Within the cost budget | Cost report |
| Long-run recovery rate | Meets the business recovery target | Chaos test output |
| Post-release error rate | Stops the rollout at the rollback threshold | Live dashboard |

The numeric thresholds are placeholders. Replace them with values agreed by the owning team, the risk owner and `@sre-team` before the first production release.

## Rollout rule

Roll out in stages. Verify each stage against its gate before the next stage starts. Stop the rollout at the first failed gate, and roll back to the last verified version.
