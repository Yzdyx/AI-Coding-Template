# Command: pr-review

Review one pull request against repository rules.

## Inputs
- `PR`: pull request number or URL.

## Steps
1. Read the PR description, the diff and the linked issue.
2. Check the task scope. List every file changed outside the declared scope.
3. Verify the change against `AGENTS.md` and `ARCHITECTURE.md`.
4. Check the dependency direction against `docs/architecture/dependency-rules.md`.
5. Check contract changes against `schemas/`.
6. Confirm the reported checks actually ran. Look for a skipped test.
7. Look for secrets, credentials and internal hostnames in the diff.
8. Write findings ordered by severity.

## Output
| Severity | File:line | Finding | Required action |
| --- | --- | --- | --- |

## Rules
- Do not approve a change that weakens a test or a policy check.
- Do not request a style change that a formatter already enforces.
- State uncertainty explicitly. Do not guess.
