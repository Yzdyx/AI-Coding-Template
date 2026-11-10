# Dependency Policy Reference

This file is a summary. The binding rules are in
[`docs/architecture/dependency-rules.md`](../../../../docs/architecture/dependency-rules.md).

## The one rule that decides most reviews

Dependencies point one way only: `Types -> Config -> Repo -> Service -> Runtime -> UI`.

## The four violations a reviewer must catch

| Violation | Example | Why it is rejected |
| --- | --- | --- |
| Upward import | `Repo` importing `Service` | The lower layer gains knowledge of a caller |
| Cross-domain import | `agents/support-agent` importing `agents/research-agent` | Modules must stay independently replaceable |
| Deep import | `import '@agent-platform/state-store/src/repository.js'` | Binds a consumer to an internal layout |
| Direct provider construction | `new ReferenceModelProvider(...)` inside `Service` | The implementation becomes untestable and bypasses policy |

## Contract classification

| Class | Meaning | Allowed in a feature PR |
| --- | --- | --- |
| `internal` | Not reachable from outside the module | Yes |
| `additive` | A new optional field, a new endpoint, a new tool | Yes, with a schema update |
| `breaking` | A renamed field, a changed meaning, a removed endpoint | No. Requires an ADR and an architecture review |

## Owner lookup

Read `CODEOWNERS`. The last matching pattern wins. A path with no owner is a finding.
