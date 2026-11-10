# Deploy Checklist

Copy this checklist into the release ticket. Tick each line with evidence.

## Before

- [ ] `release-check` passed and the record is complete.
- [ ] The artifact digest is recorded.
- [ ] The rollback target version is recorded.
- [ ] The owning team approved the change (`CODEOWNERS`).
- [ ] For `prod`: an approver is named in the ticket.
- [ ] The maintenance window is agreed, when one is required.
- [ ] The runbook for this service is current.

## During

- [ ] `terraform plan` was read before `apply`.
- [ ] The infrastructure change applied without drift.
- [ ] Stage 1 health gate passed.
- [ ] Stage 2 health gate passed.
- [ ] Error rate and P95 latency are within budget.
- [ ] Smoke evaluation passed.

## After

- [ ] The deployed version matches the release record.
- [ ] Traces and dashboards show the new version.
- [ ] The incident channel is informed.
- [ ] The release ticket records operator, time and result.
- [ ] A rollback was executed at least once in `staging` for this release line.

## Stop conditions

Stop and roll back when any of these is true:

- The error rate exceeds the rollback threshold.
- P95 latency exceeds the performance budget.
- A safety red-line case fails.
- The deployed digest differs from the verified digest.
