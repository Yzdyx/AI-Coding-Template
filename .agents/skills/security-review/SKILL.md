---
name: security-review
description: Find security defects in a change before merge, across six fixed classes.
---

# Security Review

Run this skill on any change that touches prompts, tools, permissions, connectors, logs or infrastructure.

## The six classes

1. **Secret exposure** — credentials, tokens, keys, internal hostnames in code, tests, logs or traces.
2. **Prompt injection** — untrusted text reaching a system prompt, a tool argument or a planning step.
3. **Authorization** — a new endpoint, tool or job without a policy check.
4. **Data isolation** — a query that can cross a tenant or a workspace boundary.
5. **Tool safety** — a side-effecting tool without an idempotency key or an approval node.
6. **Dependency risk** — a new dependency with an unpinned version or an unknown owner.

## Steps

1. Read the diff. Read the linked execution plan.
2. Walk the six classes in order. Record a finding or an explicit "no finding" per class.
3. Trace every new external input to its sink: model prompt, tool argument, log field, database write.
4. Confirm each side-effecting tool call carries an idempotency key.
5. Confirm each high-risk tool call stops for human approval.
6. Confirm no control was removed or weakened. Compare with the previous revision.

## Output

| Severity | File:line | Class | Finding | Required action |
| --- | --- | --- | --- | --- |

## Rules

- Report a suspicion as a suspicion, with the evidence.
- A missing control is a finding. Absence of evidence is not evidence of safety.
- Never downgrade a finding because the change is urgent.
- Do not edit a policy. Report it to `@security-team`.
