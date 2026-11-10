# Task Runner

Thin wrappers over the commands a task needs, so a contributor runs one command
instead of five.

## Tasks

The definitions are in [`Taskfile.yml`](Taskfile.yml). Run `task` to list them.

| Task | Purpose |
| --- | --- |
| `setup` | Install the workspace dependencies |
| `lint` / `typecheck` / `test` | Static check, type check and test every workspace package |
| `agents` | Run every agent test suite |
| `contracts` | Run the contract and end-to-end tests |
| `checks` | The three repository checks |
| `architecture` / `manifests` / `docs` | One repository check each |
| `verify` | Every quality gate |
| `eval` | The agent evaluation suites and the baseline check |
| `impact` | Consumers of a module (`task impact MODULE=@agent-platform/state-store`) |
| `dev` / `dev:down` | Start or stop the local stack |
| `clean` | Remove local build and cache artifacts |

## Rules

1. A task wraps an existing command. It never reimplements one.
2. A task that can fail must exit with a non-zero code.
3. A task prints the real command it ran, so the output is reproducible by hand.
4. The task list and the CI workflow stay in step: a task added here is added there.

## Planned

`generate_db_schema.py` regenerates [`../../docs/generated/db-schema.md`](../../docs/generated/db-schema.md).
Until it exists, that document is refreshed by hand and the file says so.
