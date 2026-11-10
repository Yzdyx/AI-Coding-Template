# Command: resolve-bug

Diagnose and fix one reported bug.

## Inputs
- `ISSUE`: issue number or a reproduction description.

## Steps
1. Reproduce the failure. Record the exact command and the observed output.
2. Localize the fault. State the module and the boundary it crosses.
3. Identify the root cause. Do not stop at the first symptom.
4. Write a failing test that captures the defect.
5. Apply the smallest fix that makes the test pass.
6. Run the affected unit, integration and contract tests.
7. Run `python scripts/check-architecture.py`.
8. Report the root cause, the fix and the remaining risk.

## Rules
- Never fix a symptom by weakening a check.
- Never widen a type or a permission to silence an error.
- If the root cause is in shared code, fix it once in `packages/`.
