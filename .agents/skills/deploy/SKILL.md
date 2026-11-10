---
name: deploy
description: Deploy a verified artifact to one environment with a recorded rollback target.
---

# Deploy

Use this skill to promote a verified artifact. It never builds a release candidate; that is `release-check`.

## Inputs

- `ENVIRONMENT`: `dev`, `staging` or `prod`.
- `RELEASE`: release identifier produced by `release-check`.
- `APPROVER`: required for `prod`.

## Steps

1. Confirm the environment exists under `infra/environments/<ENVIRONMENT>/`.
2. Confirm the release record from `release-check` exists and is complete.
3. Record the current version as the rollback target.
4. Apply the infrastructure change:

   ```bash
   terraform -chdir=infra/environments/<ENVIRONMENT> plan
   terraform -chdir=infra/environments/<ENVIRONMENT> apply
   ```

5. Deploy the artifact. Roll out in stages.
6. Verify the health gate after each stage:
   - error rate within the threshold,
   - P95 latency within the budget,
   - the smoke evaluation passes.
7. Record the deployed version, the operator and the timestamp.
8. Stop and roll back at the first failed gate.

## Rules

- Never deploy to `prod` without an approver recorded in the release ticket.
- Never apply a plan you have not read.
- Never edit a live resource by hand. Change the module, then re-apply.
- A rollback target must exist before the first stage starts.
