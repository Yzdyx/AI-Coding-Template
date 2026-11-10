---
name: release-check
description: Decide whether a candidate version may be released, from recorded evidence.
---

# Release Check

Run this skill before promoting a build to the next environment.

## Steps

1. Collect the version record for the candidate:

   | Object | Value |
   | --- | --- |
   | Source revision | Git commit SHA |
   | Agent manifest version | `agents/<name>/agent.yaml` `version` |
   | Prompt version | hash of `agents/<name>/prompts/` |
   | Skill version | Git SHA of `.agents/skills/` |
   | Model | provider and model identifier |
   | Tool contracts | version of `schemas/tool-contracts/` |
   | Knowledge and data | index or snapshot identifier |
   | Evaluation | dataset, evaluator and baseline identifiers |
   | Runtime | image digest and lockfile |
   | Release | release identifier |

2. Check each release gate in
   [`references/release-gates.md`](references/release-gates.md).
3. Compare the candidate metrics against the approved baseline.
4. Confirm a rollback target exists and was verified.
5. Confirm the change was reviewed by the owning team in `CODEOWNERS`.
6. Record the decision, the evidence and the approver.

## Rules

- A missing version object blocks the release. Reproducibility is not optional.
- A model-graded score alone never authorizes a release.
- If a gate could not run, the release is blocked. Do not release on a hope.
- Publish the rollback plan before the rollout, not after the first error.
