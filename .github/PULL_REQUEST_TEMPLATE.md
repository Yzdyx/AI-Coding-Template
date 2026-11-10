## Task

- Task id: `AGENT-____`
- Execution plan: `docs/exec-plans/active/____`
- Owning team: `@____`

## What changed

<!-- One paragraph. State the behavior change, not the file list. -->

## Scope

- Paths changed:
- Paths deliberately not changed:

## Contracts

| Contract | Class (`internal` / `additive` / `breaking`) | Consumers updated |
| --- | --- | --- |
|  |  |  |

A `breaking` change requires an ADR and an architecture review. Link it here.

## Verification

Paste the command and its real output. Do not summarize.

```text
python scripts/check-architecture.py
python scripts/check-agent-manifests.py
python scripts/check-doc-links.py
python -m unittest discover -s agents/research-agent/tests -t agents/research-agent -p "test_*.py"
python -m unittest discover -s agents/support-agent/tests -t agents/support-agent -p "test_*.py"
```

- [ ] Every required check ran.
- [ ] No check was skipped without a stated reason.
- [ ] No test expectation was changed to hide a regression.

## Risk

- Risk level: `low` / `medium` / `high`
- Production write: `yes` / `no`
- Rollback plan:

## Reviewer notes

- [ ] Layer direction respected.
- [ ] No secret, token or internal hostname in the diff.
- [ ] Documentation updated in this pull request.
