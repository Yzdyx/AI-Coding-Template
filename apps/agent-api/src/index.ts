/**
 * Runtime entry point for the agent API service.
 *
 * Layer: Runtime. It performs exactly three jobs: load and validate the
 * configuration, start the HTTP server, and shut the process down cleanly
 * when an operator or an orchestrator asks it to stop.
 */

import { pathToFileURL } from 'node:url';

import type { AgentApiConfig, AgentApiLogger, AgentApiServer } from './server.js';
import { createAgentApiServer } from './server.js';

/** Logical service name used in logs, metrics, and traces. */
export const SERVICE_NAME = 'agent-api';

/** Default TCP port when `AGENT_API_PORT` is not provided. */
const DEFAULT_PORT = 8080;

/** Default route prefix when `AGENT_API_BASE_PATH` is not provided. */
const DEFAULT_BASE_PATH = '/api/v1';

/** Default drain window, in milliseconds, before a forced exit. */
const DEFAULT_SHUTDOWN_TIMEOUT_MS = 10_000;

/** Logger contract used across the Runtime layer. */
export type RuntimeLogger = AgentApiLogger;

/** Writes JSON lines to stdout and stderr without pulling in a dependency. */
export function createConsoleLogger(service: string): AgentApiLogger {
  const emit = (
    write: (line: string) => void,
    level: 'info' | 'warn' | 'error',
    message: string,
    fields?: Record<string, unknown>,
  ): void => {
    const record: Record<string, unknown> = {
      time: new Date().toISOString(),
      level,
      service,
      message,
    };
    if (fields !== undefined) {
      for (const [key, value] of Object.entries(fields)) {
        record[key] = value;
      }
    }
    write(`${JSON.stringify(record)}\n`);
  };

  return {
    info: (message, fields) => emit((line) => process.stdout.write(line), 'info', message, fields),
    warn: (message, fields) => emit((line) => process.stderr.write(line), 'warn', message, fields),
    error: (message, fields) => emit((line) => process.stderr.write(line), 'error', message, fields),
  };
}

/** Reads an integer environment variable, falling back when it is absent. */
function readInt(
  env: Readonly<Record<string, string | undefined>>,
  key: string,
  fallback: number,
): number {
  const raw = env[key];
  if (raw === undefined || raw.trim() === '') {
    return fallback;
  }
  const parsed = Number.parseInt(raw, 10);
  if (Number.isNaN(parsed)) {
    throw new Error(`Environment variable ${key} must be an integer, received "${raw}"`);
  }
  return parsed;
}

/** Reads a required environment variable. Fails closed when it is missing. */
function readRequired(env: Readonly<Record<string, string | undefined>>, key: string): string {
  const raw = env[key];
  if (raw === undefined || raw.trim() === '') {
    throw new Error(`Environment variable ${key} is required`);
  }
  return raw;
}

/**
 * Loads and validates the Runtime configuration.
 *
 * Configuration is read once, at start-up. A missing or malformed value stops
 * the process instead of silently running with an unsafe default.
 */
export function loadAgentApiConfig(
  env: Readonly<Record<string, string | undefined>> = process.env,
): AgentApiConfig {
  return {
    serviceName: SERVICE_NAME,
    host: env['AGENT_API_HOST'] ?? '0.0.0.0',
    port: readInt(env, 'AGENT_API_PORT', DEFAULT_PORT),
    basePath: env['AGENT_API_BASE_PATH'] ?? DEFAULT_BASE_PATH,
    stateStoreUrl: readRequired(env, 'AGENT_STATE_STORE_URL'),
    modelProviderUrl: readRequired(env, 'AGENT_MODEL_PROVIDER_URL'),
    policyBundle: env['AGENT_POLICY_BUNDLE'] ?? 'default',
    shutdownTimeoutMs: readInt(env, 'AGENT_API_SHUTDOWN_TIMEOUT_MS', DEFAULT_SHUTDOWN_TIMEOUT_MS),
    requireAuth: (env['AGENT_API_REQUIRE_AUTH'] ?? 'true') !== 'false',
  };
}

/**
 * Starts the server and installs graceful shutdown handlers.
 *
 * The first stop signal begins a bounded drain. A second signal, or an
 * exhausted drain window, forces the exit so a stuck request cannot block a
 * deployment forever.
 */
export async function startAgentApi(
  config: AgentApiConfig,
  logger: AgentApiLogger,
): Promise<AgentApiServer> {
  const server = await createAgentApiServer(config, logger);
  await server.listen();
  logger.info('agent-api listening', { address: server.address, basePath: config.basePath });

  let shuttingDown = false;

  const shutdown = async (signal: string): Promise<void> => {
    if (shuttingDown) {
      logger.warn('second stop signal received, exiting immediately', { signal });
      process.exit(1);
    }
    shuttingDown = true;
    logger.info('shutdown requested', { signal, timeoutMs: config.shutdownTimeoutMs });

    const timer = setTimeout(() => {
      logger.error('shutdown window exceeded, exiting', { timeoutMs: config.shutdownTimeoutMs });
      process.exit(1);
    }, config.shutdownTimeoutMs);
    timer.unref();

    try {
      await server.close();
      clearTimeout(timer);
      logger.info('agent-api stopped');
      process.exit(0);
    } catch (error) {
      clearTimeout(timer);
      logger.error('shutdown failed', {
        error: error instanceof Error ? error.message : String(error),
      });
      process.exit(1);
    }
  };

  const signals: readonly NodeJS.Signals[] = ['SIGINT', 'SIGTERM'];
  for (const signal of signals) {
    process.on(signal, () => {
      void shutdown(signal);
    });
  }

  return server;
}

/** Process bootstrap. Kept separate so the pieces above stay importable. */
export async function main(): Promise<void> {
  const logger = createConsoleLogger(SERVICE_NAME);
  const config = loadAgentApiConfig();
  await startAgentApi(config, logger);
}

const entryPoint = process.argv[1];
if (entryPoint !== undefined && import.meta.url === pathToFileURL(entryPoint).href) {
  main().catch((error: unknown) => {
    createConsoleLogger(SERVICE_NAME).error('agent-api failed to start', {
      error: error instanceof Error ? error.message : String(error),
    });
    process.exitCode = 1;
  });
}
