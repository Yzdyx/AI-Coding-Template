/**
 * State store configuration.
 *
 * Layer: Config. It reads and validates values and merges defaults. It performs
 * no I/O and holds no business rule. A missing required value fails closed.
 */

/** Validated configuration for the state store. */
export interface StateStoreConfig {
  readonly url: string;
  readonly tenant: string;
  readonly maxPoolSize: number;
  readonly statementTimeoutMs: number;
  readonly checkpointTtlSeconds: number;
  readonly idempotencyTtlMs: number;
  /** Default lease for a claimed task, in milliseconds. */
  readonly taskLeaseMs: number;
}

/** Partial input accepted by the loader. */
export interface StateStoreConfigInput {
  readonly url: string;
  readonly tenant?: string;
  readonly maxPoolSize?: number;
  readonly statementTimeoutMs?: number;
  readonly checkpointTtlSeconds?: number;
  readonly idempotencyTtlMs?: number;
  readonly taskLeaseMs?: number;
}

const DEFAULT_TENANT = 'tenant-local';
const DEFAULT_MAX_POOL_SIZE = 10;
const DEFAULT_STATEMENT_TIMEOUT_MS = 5_000;
const DEFAULT_CHECKPOINT_TTL_SECONDS = 86_400;
const DEFAULT_IDEMPOTENCY_TTL_MS = 300_000;
const DEFAULT_TASK_LEASE_MS = 900_000;

/** Thrown when the configuration contract is not satisfied. */
export class ConfigurationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConfigurationError';
  }
}

function positive(value: number | undefined, fallback: number, key: string): number {
  if (value === undefined) {
    return fallback;
  }
  if (!Number.isInteger(value) || value <= 0) {
    throw new ConfigurationError(`${key} must be a positive integer, received ${value}`);
  }
  return value;
}

/**
 * Validates and merges the configuration.
 *
 * The URL is required. A state store without a URL cannot persist a checkpoint,
 * so the loader refuses rather than starting an unscoped store.
 */
export function loadStateStoreConfig(input: StateStoreConfigInput): StateStoreConfig {
  if (typeof input.url !== 'string' || input.url.trim() === '') {
    throw new ConfigurationError('url is required');
  }
  return {
    url: input.url,
    tenant: input.tenant ?? DEFAULT_TENANT,
    maxPoolSize: positive(input.maxPoolSize, DEFAULT_MAX_POOL_SIZE, 'maxPoolSize'),
    statementTimeoutMs: positive(
      input.statementTimeoutMs,
      DEFAULT_STATEMENT_TIMEOUT_MS,
      'statementTimeoutMs',
    ),
    checkpointTtlSeconds: positive(
      input.checkpointTtlSeconds,
      DEFAULT_CHECKPOINT_TTL_SECONDS,
      'checkpointTtlSeconds',
    ),
    idempotencyTtlMs: positive(input.idempotencyTtlMs, DEFAULT_IDEMPOTENCY_TTL_MS, 'idempotencyTtlMs'),
    taskLeaseMs: positive(input.taskLeaseMs, DEFAULT_TASK_LEASE_MS, 'taskLeaseMs'),
  };
}
