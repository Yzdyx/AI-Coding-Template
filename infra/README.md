# Infrastructure

Terraform modules, per-environment compositions and policy files.

## Layout

| Path | Content |
| --- | --- |
| `modules/` | Reusable modules. No environment-specific value here |
| `environments/dev/` | Development composition |
| `environments/staging/` | Staging composition |
| `environments/prod/` | Production composition. Protected path |
| `policies/` | Authorization policies consumed by the policy engine |

## Rules

1. Never edit a live resource by hand. Change the module, then re-apply.
2. `infra/environments/prod/` is a protected path. It requires approval from `@sre-team`.
3. Read the plan before applying it. A plan you have not read is not a plan.
4. Every environment pins the module version it uses.
5. Secrets never appear in a `.tf` file. Read them from the secret manager.
6. A policy change is a security change. It needs review by `@security-team`.

## Workflow

```bash
terraform -chdir=infra/environments/dev init
terraform -chdir=infra/environments/dev plan
terraform -chdir=infra/environments/dev apply
```

Promotion order is `dev -> staging -> prod`. A stage is skipped only with a recorded reason.

## Related

- [`../.agents/skills/deploy/SKILL.md`](../.agents/skills/deploy/SKILL.md)
- [`../docs/operations/runbooks/rollback.md`](../docs/operations/runbooks/rollback.md)
- [`../docs/security/security-architecture.md`](../docs/security/security-architecture.md)
