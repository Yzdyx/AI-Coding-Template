---
applyTo: "agents/**/*.py,scripts/**/*.py,tests/**/*.py"
---

# Python Instructions

These rules apply to Python under `agents/`, `scripts/` and `tests/`.

## Runtime

- Target Python 3.12 or newer. Use `from __future__ import annotations`.
- Standard library only, unless the package declares a dependency.
- Type-annotate every public function.

## Layers

- `agents/<name>/src/main.py` is the `Service` layer. It holds business rules and orchestration.
- `agents/<name>/tools/` holds tool implementations. A tool validates its input and declares a risk level.
- No network call in a unit test. Inject a stub provider instead.

## Style

- `snake_case` for functions and variables, `PascalCase` for classes.
- One module, one responsibility. Keep files under 400 lines.
- Raise a specific exception type. Never raise a bare `Exception`.

## Tests

- Use `unittest` from the standard library.
- Tests must pass with `python -m unittest discover -s agents/<name>/tests -t agents/<name> -p "test_*.py"`.
- Tests must be deterministic. Freeze the clock, fix the seed.
- A safety test asserts a refusal, not just an absence of an error.
