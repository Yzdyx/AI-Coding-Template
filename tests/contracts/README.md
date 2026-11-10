# Contract Tests

Compatibility tests for the public interfaces of every package. A contract test
answers one question: can a consumer still use this interface after the change?

## What belongs here

| Test | Asserts |
| --- | --- |
| Schema compatibility | A payload valid before the change is still valid after it |
| Interface shape | A required field was not removed or renamed |
| Tool contract | `schemas/tool-contracts/` still matches the tool implementation |
| Policy contract | A decision shape consumed by the gateway did not change meaning |

## Rules

1. A contract test uses a recorded payload, not a live service.
2. A breaking change fails here before it fails in production.
3. Adding an optional field does not break a contract test. Removing or renaming a field does.
4. A contract test is not a substitute for an end-to-end test. It checks shape, not behavior.

## Running

```bash
python -m unittest discover -s tests/contracts -p "test_*.py"
python -m unittest discover -s tests/end-to-end -p "test_*.py"
```

The manifest contract test parses every `agents/*/agent.yaml` with an inline
YAML-subset parser, so it runs on a clean checkout with no dependency install.

## Related

- [`../../schemas/`](../../schemas/)
- [`../../docs/architecture/dependency-rules.md`](../../docs/architecture/dependency-rules.md) section 6
- [`../../.agents/skills/impact-analysis/SKILL.md`](../../.agents/skills/impact-analysis/SKILL.md)
