# Test Rules

Applies to every package and agent.

## Structure
- `tests/unit/` for pure logic. No network, no clock, no filesystem.
- `tests/integration/` for real dependencies in a container.
- `tests/contracts/` for interface compatibility across modules.
- `tests/end-to-end/` for a full user-visible flow.
- `tests/eval/` for agent behavior. This is not a unit test.

## Requirements
- One behavior per test. The test name states the expected behavior.
- Every bug fix adds a regression test that fails before the fix.
- Tests must be deterministic. Fix the seed, freeze the clock.
- Never weaken an assertion to make a change pass.
- Never commit a skipped test without a linked issue.

## Reporting
- A test failure message states: input, expected, actual, and the command to reproduce.
- Agent-facing failures must be short, structured and locatable.
