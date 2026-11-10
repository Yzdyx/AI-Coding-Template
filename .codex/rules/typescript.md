# TypeScript Rules

Applies to `apps/**` and `packages/**`.

## Types
- `strict: true` is mandatory. Never disable it per file.
- Do not use `any`. Use `unknown` and narrow it.
- Export types from the package entrypoint. Do not deep-import types.
- Validate external input at the boundary. Do not trust a cast.

## Modules
- Import through the package entrypoint only.
- Never import from `src/internal/**` of another package.
- Keep one public capability per package.
- No circular imports. `scripts/check-architecture.py` blocks them.

## Style
- Prefer pure functions for business rules.
- Inject side effects (clock, network, storage) through parameters.
- Handle every error path. Do not swallow an error with an empty catch.
- Name files in `kebab-case`. Name types in `PascalCase`.

## Review checklist
- [ ] No `any`, no `@ts-ignore` without a linked issue.
- [ ] Public interface change is reflected in `schemas/`.
- [ ] New dependency is justified and pinned.
