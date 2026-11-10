# Policies

Authorization policies consumed by the tool gateway and by
`packages/policy-engine/`. A policy decides whether a subject may call a tool
with given arguments in a given context.

## Files

| File | Scope |
| --- | --- |
| [`agent-policy.yaml`](agent-policy.yaml) | Policy bundle descriptor loaded by the tool gateway |
| [`agent-tool-access.rego`](agent-tool-access.rego) | Tool access per agent, risk level and tenant |

## Rules

1. Deny by default. A policy that cannot evaluate a request denies it.
2. The policy engine fails closed. A policy engine that is unreachable means the call is denied.
3. A high-risk tool requires an approval record. The policy checks the record, not the caller's claim.
4. The tenant identifier comes from the authenticated subject. A tenant identifier supplied by the caller is ignored.
5. Never weaken a policy to make a change pass. Report it to `@security-team`.

## Testing

A policy change requires a test case for the allow path and for the deny path.

```bash
opa test infra/policies
```

## Related

- [`../../docs/security/security-architecture.md`](../../docs/security/security-architecture.md)
- [`../../packages/policy-engine/`](../../packages/policy-engine/)
- [`../../docs/security/threat-model.md`](../../docs/security/threat-model.md)
