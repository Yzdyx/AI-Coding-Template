/**
 * Connector provider.
 *
 * Layer: Repo. It invokes an external tool. The reference implementation keeps
 * its results in memory and enforces the idempotency rule, so a local
 * environment and the tests run without a third-party system.
 *
 * Two invariants:
 *
 *   1. Idempotency. A repeated key returns the stored result. It never repeats
 *      the side effect. This is the platform's main defence against a duplicate
 *      payment, send or delete.
 *   2. No invented tool. An unregistered tool fails closed. It is never silently
 *      treated as a success.
 */

import type { ToolInvocation, ToolResult } from '@agent-platform/agent-contracts';

/** A registered tool implementation. */
export type ToolHandler = (
  arguments_: Readonly<Record<string, unknown>>,
) => Promise<Readonly<Record<string, unknown>>> | Readonly<Record<string, unknown>>;

/** One invocation request. */
export interface ConnectorInvocation extends ToolInvocation {
  /** Required. A call without a key is rejected by the policy engine first. */
  readonly idempotencyKey: string;
}

/** Configuration for the reference connector provider. */
export interface ConnectorProviderConfig {
  /** Connector endpoint. Recorded for the audit trail; the reference build does not call it. */
  readonly endpoint: string;
  /** How long a stored result is replayable, in milliseconds. */
  readonly idempotencyTtlMs?: number;
}

/** Contract consumed by the Runtime layer. */
export interface ConnectorProvider {
  invoke(invocation: ConnectorInvocation): Promise<ToolResult>;
  /** Registers a tool. A local environment and a test use this. */
  register(name: string, handler: ToolHandler): void;
  readonly endpoint: string;
}

const DEFAULT_IDEMPOTENCY_TTL_MS = 300_000;

interface StoredResult {
  readonly result: ToolResult;
  readonly expiresAt: number;
}

/** Reference connector provider: in-memory tools, in-memory idempotency ledger. */
export class ReferenceConnectorProvider implements ConnectorProvider {
  readonly endpoint: string;
  readonly #handlers = new Map<string, ToolHandler>();
  readonly #ledger = new Map<string, StoredResult>();
  readonly #ttlMs: number;

  constructor(config: ConnectorProviderConfig) {
    this.endpoint = config.endpoint;
    this.#ttlMs = config.idempotencyTtlMs ?? DEFAULT_IDEMPOTENCY_TTL_MS;
  }

  register(name: string, handler: ToolHandler): void {
    this.#handlers.set(name, handler);
  }

  async invoke(invocation: ConnectorInvocation): Promise<ToolResult> {
    if (invocation.idempotencyKey === '') {
      return {
        tool: invocation.name,
        status: 'failed',
        output: { error: 'idempotency_key_missing' },
        degraded: false,
      };
    }

    const key = `${invocation.name}:${invocation.idempotencyKey}`;
    const stored = this.#ledger.get(key);
    if (stored !== undefined && stored.expiresAt > Date.now()) {
      return stored.result;
    }

    const handler = this.#handlers.get(invocation.name);
    if (handler === undefined) {
      // Fail closed: an unregistered tool is never reported as a success.
      return {
        tool: invocation.name,
        status: 'failed',
        output: { error: 'tool_not_registered', tool: invocation.name },
        degraded: false,
      };
    }

    try {
      const output = await handler(invocation.arguments);
      const result: ToolResult = {
        tool: invocation.name,
        status: 'succeeded',
        output,
        degraded: false,
      };
      this.#ledger.set(key, { result, expiresAt: Date.now() + this.#ttlMs });
      return result;
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      const result: ToolResult = {
        tool: invocation.name,
        status: 'failed',
        output: { error: message },
        degraded: false,
      };
      this.#ledger.set(key, { result, expiresAt: Date.now() + this.#ttlMs });
      return result;
    }
  }
}

/** Builds the connector provider from its configuration. */
export function createConnectorProvider(config: ConnectorProviderConfig): ConnectorProvider {
  return new ReferenceConnectorProvider(config);
}
