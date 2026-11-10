---
name: verify-change
description: Verify a change against the repository quality gates and report the real output.
---

# Verify Change

Run this skill after modifying source code, schemas, manifests or build logic.

## Steps

1. Identify the affected packages from the Git diff.
2. Run the format and lint checks of every affected package.
3. Run type checking and the unit tests of every affected package.
4. Run contract tests for every changed public interface.
5. Run the three repository checks.
6. Run the aggregate gate:

   ```bash
   python .agents/skills/verify-change/scripts/verify.py --root .
   ```

7. Report every failure with the file path, the command and the real output.

## Quality gates

The gate list is in [`references/quality-gates.md`](references/quality-gates.md).

## Rules

- Do not report success when a required check was skipped.
- Do not change a test expectation to hide a regression.
- Report a check that could not run as `blocked`, with the reason.
- Attach the command and its output to the pull request description.
