# @agent-platform/state-store

Configuration and durable persistence. Layers: `Config` and `Repo`.

One package may hold more than one layer. The layer is a property of the file,
not of the directory: `src/config.ts` is `Config`, `src/repository.ts` is `Repo`.
`src/repository.ts` must never import a `Service` file.

## Rules

1. The repository holds no business rule. It reads and writes.
2. A checkpoint is written after every step. A resumed run must not repeat a completed side effect.
3. Every side-effecting tool call has an idempotency record. A repeated key returns the first result.
4. The tenant identifier is applied by this package, never taken from the caller's payload.
5. A missing required configuration value is an error. The store never invents a default for a required value.

## Contents

| Symbol | Layer | Role |
| --- | --- | --- |
| `StateStoreConfig`, `loadStateStoreConfig` | `Config` | Read and validate configuration |
| `StateStoreRepository` | `Repo` | Checkpoints, run records, idempotency ledger |

## Related

- [`../../docs/generated/db-schema.md`](../../docs/generated/db-schema.md)
- [`../../docs/RELIABILITY.md`](../../docs/RELIABILITY.md)
