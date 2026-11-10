---
applyTo: "apps/**/*.{ts,tsx},packages/**/*.ts"
---

# TypeScript Instructions

These rules apply to every TypeScript file in `apps/` and `packages/`.

## Types

- `strict` mode stays on. Do not disable it per file.
- Do not use `any`. Use `unknown` and narrow it.
- Validate external input at the boundary. Never trust a cast.

## Imports

- Import another package by its name, never by a relative path into its `src/`.
- Never import another package's `src/internal/**`.
- Keep the direction `Types -> Config -> Repo -> Service -> Runtime -> UI`.
- `scripts/check-architecture.py` rejects a violation.

## Style

- One public capability per package.
- Inject side effects (clock, network, storage) as parameters.
- Handle every error path. An empty catch is a defect.
- Files use `kebab-case`. Types use `PascalCase`.

## Tests

- Tests live in `tests/` or beside the source as `*.test.ts`.
- Run `node --test` for the package.
- A bug fix adds a regression test that failed before the fix.
