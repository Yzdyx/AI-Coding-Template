---
name: impact-analysis
description: Map the modules, contracts and owners a change touches before any code is edited.
---

# Impact Analysis

Run this skill before a cross-module change, and before a change to a shared contract.

## Steps

1. Read the task metadata. Record the declared scope paths.
2. List the files the change will touch. Group them by module.
3. For every touched module, find its public entry point.
4. Find every consumer of a changed public interface:

   ```bash
   python .agents/skills/impact-analysis/scripts/impact_analysis.py --root . --module <package-name>
   ```

5. Classify every affected contract: `additive`, `breaking` or `internal`.
6. Read `docs/architecture/dependency-rules.md`. Check the direction of every new import.
7. Read `CODEOWNERS`. Record the owning team of every touched path.
8. Write the result into the execution plan under `docs/exec-plans/active/`.

## Output

| Module | Changed public interface | Consumers | Contract class | Owner |
| --- | --- | --- | --- | --- |

## Rules

- A breaking contract change stops the task. Report it to `@architecture-team`.
- Do not edit code before the impact table is complete.
- Report an unknown consumer as unknown. Never assume there is none.
- Report findings outside the task scope. Do not fix them silently.
