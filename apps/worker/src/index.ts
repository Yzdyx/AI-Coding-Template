/**
 * Background worker Runtime entry point.
 *
 * Layer: Runtime. The worker claims a task from the shared queue, drives one
 * agent run, writes a checkpoint after every step, and releases the task lock.
 *
 * Two invariants shape this file:
 *
 *   1. Idempotency. Every side-effecting step carries a deterministic
 *      idempotency key. Before invoking a tool the worker consults the
 *      operation log; a hit means the effect already happened, so the stored
 *      result is reused instead of repeating a payment, a send, or a delete.
 *   2. Human approval. A step the policy engine classifies as high-risk stops
 *      at an approval checkpoint. The worker records the request, checkpoints
 *      the run, and returns without performing the side effect.
 */

import { randomUUID } from 'node:crypto';
import { pathToFileURL } from 'node:url';

import type {
  AgentEvent,
  ApprovalRequest,
  RunCheckpoint,
  TaskEnvelope,
  ToolInvocation,
  ToolResult,
} from '@agent-platform/agent-contracts';
import type { Span, TelemetryProvider } from '@agent-platform/observability';
import { createTelemetryProvider } from '@agent-platform/observability';
import type { PolicyDecision, PolicyEngine } from '@agent-platform/policy-engine';
import { createPolicyEngine } from '@agent-platform/policy-engine';
import type { StateStore } from '@agent-platform/state-store';
import { createStateStore, loadStateStoreConfig } from '@agent-platform/state-store';
import type { ConnectorProvider, ModelCompletion, ModelProvider } from '@agent-platform/tool-adapters';
import { createConnectorProvider, createModelProvider } from '@agent-platform/tool-adapters';

/** Logical service name used in logs, metrics, and traces. */
export const SERVICE_NAME = 'worker';

/** Fallback telemetry endpoint used when no collector is configured. */
const DEFAULT_TELEMETRY_ENDPOINT = 'https://telemetry.example.com';

/** Default idle delay between claim attempts, in milliseconds. */
const DEFAULT_POLL_INTERVAL_MS = 1_000;

/** Default task lease, in milliseconds. */
const DEFAULT_LEASE_MS = 60_000;

/** Default attempts allowed before a task is parked as failed. */
const DEFAULT_MAX_ATTEMPTS = 3;

/** Default drain window for the task in flight, in milliseconds. */
const DEFAULT_SHUTDOWN_TIMEOUT_MS = 30_000;

/** Runtime configuration consumed by the worker. */
export interface WorkerConfig {
  readonly workerId: string;
  readonly pollIntervalMs: number;
  readonly leaseMs: number;
  readonly maxAttempts: number;
  readonly shutdownTimeoutMs: number;
  readonly stateStoreUrl: string;
  readonly modelProviderUrl: string;
  readonly connectorEndpoint: string;
  readonly policyBundle: string;
}

/** Minimal logging contract. The Runtime owns logging at its own edge. */
export interface WorkerLogger {
  info(message: string, fields?: Record<string, unknown>): void;
  warn(message: string, fields?: Record<string, unknown>): void;
  error(message: string, fields?: Record<string, unknown>): void;
}

/** Everything the worker may use. Assembled once, at start-up. */
export interface WorkerDependencies {
  readonly store: StateStore;
  readonly policy: PolicyEngine;
  readonly telemetry: TelemetryProvider;
  readonly model: ModelProvider;
  readonly connectors: ConnectorProvider;
}

/** One planned step of a run. */
export interface PlanStep {
  readonly id: string;
  readonly tool: string;
  readonly arguments: Readonly<Record<string, unknown>>;
}

/** Result of processing a single task. */
export interface TaskOutcome {
  readonly taskId: string;
  readonly runId: string;
  readonly status: 'succeeded' | 'awaiting_approval';
  readonly completedSteps: number;
}

/** Writes JSON lines to stdout and stderr without pulling in a dependency. */
export function createConsoleLogger(service: string): WorkerLogger {
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
 * Loads and validates the worker configuration.
 *
 * The worker identity defaults to a host-and-pid label so two processes on the
 * same host never share a lease.
 */
export function loadWorkerConfig(
  env: Readonly<Record<string, string | undefined>> = process.env,
): WorkerConfig {
  return {
    workerId: env['WORKER_ID'] ?? `${SERVICE_NAME}-${process.pid}`,
    pollIntervalMs: readInt(env, 'WORKER_POLL_INTERVAL_MS', DEFAULT_POLL_INTERVAL_MS),
    leaseMs: readInt(env, 'WORKER_LEASE_MS', DEFAULT_LEASE_MS),
    maxAttempts: readInt(env, 'WORKER_MAX_ATTEMPTS', DEFAULT_MAX_ATTEMPTS),
    shutdownTimeoutMs: readInt(env, 'WORKER_SHUTDOWN_TIMEOUT_MS', DEFAULT_SHUTDOWN_TIMEOUT_MS),
    stateStoreUrl: readRequired(env, 'AGENT_STATE_STORE_URL'),
    modelProviderUrl: readRequired(env, 'AGENT_MODEL_PROVIDER_URL'),
    connectorEndpoint: readRequired(env, 'AGENT_CONNECTOR_ENDPOINT'),
    policyBundle: env['AGENT_POLICY_BUNDLE'] ?? 'default',
  };
}

/**
 * Builds the worker dependencies from configuration.
 *
 * Cross-cutting capabilities enter through their Provider interfaces, never
 * through a direct import of another package's internals.
 */
export function createWorkerDependencies(config: WorkerConfig): WorkerDependencies {
  return {
    store: createStateStore(loadStateStoreConfig({ url: config.stateStoreUrl })),
    policy: createPolicyEngine({ bundle: config.policyBundle }),
    telemetry: createTelemetryProvider({
      serviceName: SERVICE_NAME,
      endpoint: process.env['OTEL_EXPORTER_OTLP_ENDPOINT'] ?? DEFAULT_TELEMETRY_ENDPOINT,
    }),
    model: createModelProvider({ endpoint: config.modelProviderUrl }),
    connectors: createConnectorProvider({ endpoint: config.connectorEndpoint }),
  };
}

/** Returns the deterministic idempotency key for one step of a run. */
export function stepIdempotencyKey(runId: string, stepId: string): string {
  return `${runId}:${stepId}`;
}

/** Returns the deterministic idempotency key of the planning model call. */
export function planIdempotencyKey(runId: string): string {
  return `${runId}:plan`;
}

/**
 * Plans the run through the model provider.
 *
 * The planning call is keyed by the run identifier, so a resumed run derives
 * the same plan and completed steps stay comparable by idempotency key.
 */
export async function planRun(deps: WorkerDependencies, task: TaskEnvelope): Promise<readonly PlanStep[]> {
  const completion: ModelCompletion = await deps.model.complete({
    modelId: task.modelId,
    systemPrompt: task.systemPrompt,
    messages: [{ role: 'user', content: JSON.stringify(task.input) }],
    tools: task.allowedTools,
    idempotencyKey: planIdempotencyKey(task.runId),
  });

  return completion.toolInvocations.map((invocation: ToolInvocation, index: number): PlanStep => ({
    id: `step-${index + 1}`,
    tool: invocation.name,
    arguments: invocation.arguments,
  }));
}

/** Persists a checkpoint describing the current position of the run. */
async function writeCheckpoint(
  deps: WorkerDependencies,
  checkpoint: {
    readonly runId: string;
    readonly stepIndex: number;
    readonly status: RunCheckpoint['status'];
    readonly state: Record<string, unknown>;
  },
): Promise<void> {
  const record: RunCheckpoint = {
    runId: checkpoint.runId,
    sequence: checkpoint.stepIndex + 1,
    stepIndex: checkpoint.stepIndex,
    status: checkpoint.status,
    state: checkpoint.state,
    createdAt: new Date().toISOString(),
  };
  await deps.store.saveCheckpoint(record);
}

/** Appends a run event so the UI can follow progress without polling state. */
async function emitEvent(
  deps: WorkerDependencies,
  runId: string,
  type: string,
  payload: Record<string, unknown>,
): Promise<void> {
  const event: AgentEvent = {
    id: `evt_${randomUUID()}`,
    runId,
    type,
    payload,
    createdAt: new Date().toISOString(),
  };
  await deps.store.appendEvent(event);
}

/**
 * Processes one claimed task to a stopping point.
 *
 * Returns `succeeded` when every planned step finished, or
 * `awaiting_approval` when a step stopped at the human approval gate. In both
 * cases the caller is responsible for releasing the task lock.
 */
export async function processTask(
  deps: WorkerDependencies,
  config: WorkerConfig,
  task: TaskEnvelope,
  logger: WorkerLogger,
): Promise<TaskOutcome> {
  const span: Span = deps.telemetry.startSpan('worker.process_task', {
    taskId: task.id,
    runId: task.runId,
    agentId: task.agentId,
    attempt: task.attempt,
  });

  try {
    const checkpoint = await deps.store.loadLatestCheckpoint(task.runId);

    // A run parked on an approval must not be re-executed. The queue is not
    // supposed to offer it, and this guard makes the rule explicit.
    if (checkpoint !== null && checkpoint.status === 'awaiting_approval') {
      const pending = await deps.store.getPendingApproval(task.runId);
      if (pending !== null) {
        logger.info('run is paused for approval, releasing task', {
          runId: task.runId,
          approvalId: pending.id,
        });
        return {
          taskId: task.id,
          runId: task.runId,
          status: 'awaiting_approval',
          completedSteps: checkpoint.stepIndex,
        };
      }
    }

    const steps = await planRun(deps, task);
    let stepIndex = checkpoint === null ? 0 : checkpoint.stepIndex;

    if (checkpoint !== null) {
      logger.info('resuming run from checkpoint', { runId: task.runId, stepIndex });
    }

    while (stepIndex < steps.length) {
      const step = steps[stepIndex] as PlanStep;
      const idempotencyKey = stepIdempotencyKey(task.runId, step.id);

      // Idempotency: never repeat an effect that already happened.
      const recorded: ToolResult | null = await deps.store.findToolResult(task.runId, idempotencyKey);
      if (recorded !== null) {
        logger.info('step already applied, reusing recorded result', {
          runId: task.runId,
          stepId: step.id,
          idempotencyKey,
        });
        stepIndex += 1;
        continue;
      }

      const decision: PolicyDecision = await deps.policy.evaluateToolCall(
        {
          name: step.tool,
          arguments: step.arguments,
          runId: task.runId,
          agentId: task.agentId,
          actor: task.requestedBy,
        },
        { idempotencyKey, attempt: task.attempt },
      );

      if (decision.decision === 'deny') {
        throw new Error(`Tool "${step.tool}" denied by policy: ${decision.reason}`);
      }

      // Human approval checkpoint: record the request, checkpoint the run, and
      // return without performing the side effect.
      if (decision.decision === 'require_approval') {
        const approval: ApprovalRequest = {
          id: `apr_${randomUUID()}`,
          runId: task.runId,
          taskId: task.id,
          agentId: task.agentId,
          tool: step.tool,
          arguments: step.arguments,
          requestedBy: task.requestedBy,
          reason: decision.reason,
          status: 'pending',
          createdAt: new Date().toISOString(),
        };
        await deps.store.createApprovalRequest(approval);
        await writeCheckpoint(deps, {
          runId: task.runId,
          stepIndex,
          status: 'awaiting_approval',
          state: { completedSteps: stepIndex, pendingTool: step.tool, idempotencyKey, approvalId: approval.id },
        });
        await emitEvent(deps, task.runId, 'run.awaiting_approval', {
          approvalId: approval.id,
          tool: step.tool,
          stepId: step.id,
          reason: decision.reason,
        });
        logger.warn('run paused for human approval', {
          runId: task.runId,
          stepId: step.id,
          tool: step.tool,
          approvalId: approval.id,
        });
        return {
          taskId: task.id,
          runId: task.runId,
          status: 'awaiting_approval',
          completedSteps: stepIndex,
        };
      }

      const result: ToolResult = await deps.connectors.invoke({
        name: step.tool,
        arguments: step.arguments,
        idempotencyKey,
      });

      // The operation log is written before the checkpoint, so a crash between
      // the two replays the step as a no-op instead of repeating the effect.
      await deps.store.saveToolResult({
        runId: task.runId,
        idempotencyKey,
        tool: step.tool,
        result,
      });
      await writeCheckpoint(deps, {
        runId: task.runId,
        stepIndex: stepIndex + 1,
        status: 'running',
        state: { completedSteps: stepIndex + 1, lastTool: step.tool },
      });
      await emitEvent(deps, task.runId, 'run.step_completed', {
        stepId: step.id,
        tool: step.tool,
        idempotencyKey,
      });

      stepIndex += 1;
    }

    await writeCheckpoint(deps, {
      runId: task.runId,
      stepIndex: steps.length,
      status: 'succeeded',
      state: { completedSteps: steps.length },
    });
    await emitEvent(deps, task.runId, 'run.succeeded', {
      workerId: config.workerId,
      completedSteps: steps.length,
    });

    return { taskId: task.id, runId: task.runId, status: 'succeeded', completedSteps: steps.length };
  } catch (error) {
    span.recordError(error as Error);
    throw error;
  } finally {
    span.end();
  }
}

/** Resolves after the delay, or immediately when the signal is aborted. */
function sleep(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise<void>((resolve) => {
    if (signal.aborted) {
      resolve();
      return;
    }
    const timer = setTimeout(() => {
      signal.removeEventListener('abort', onAbort);
      resolve();
    }, ms);
    const onAbort = (): void => {
      clearTimeout(timer);
      resolve();
    };
    signal.addEventListener('abort', onAbort, { once: true });
  });
}

/**
 * Runs the claim-process-release loop until the signal is aborted.
 *
 * One task is in flight at a time. Scaling out means running more worker
 * processes, not raising the concurrency of a single process.
 */
export async function runWorkerLoop(
  config: WorkerConfig,
  deps: WorkerDependencies,
  logger: WorkerLogger,
  signal: AbortSignal,
): Promise<void> {
  logger.info('worker started', {
    workerId: config.workerId,
    pollIntervalMs: config.pollIntervalMs,
    leaseMs: config.leaseMs,
  });

  while (!signal.aborted) {
    const task = await deps.store.claimTask({ workerId: config.workerId, leaseMs: config.leaseMs });

    if (task === null) {
      await sleep(config.pollIntervalMs, signal);
      continue;
    }

    try {
      await emitEvent(deps, task.runId, 'run.claimed', {
        taskId: task.id,
        workerId: config.workerId,
        attempt: task.attempt,
      });

      const outcome = await processTask(deps, config, task, logger);

      if (outcome.status === 'succeeded') {
        await deps.store.completeTask({
          taskId: task.id,
          workerId: config.workerId,
          runId: task.runId,
        });
        logger.info('task completed', {
          taskId: task.id,
          runId: task.runId,
          completedSteps: outcome.completedSteps,
        });
      } else {
        logger.info('task handed back pending approval', {
          taskId: task.id,
          runId: task.runId,
        });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      logger.error('task failed', { taskId: task.id, runId: task.runId, error: message });
      await emitEvent(deps, task.runId, 'run.failed', { taskId: task.id, error: message });
      await deps.store.failTask({
        taskId: task.id,
        workerId: config.workerId,
        error: message,
        retryable: task.attempt < config.maxAttempts,
      });
    } finally {
      // Releasing is idempotent: a completed or failed task ignores the call.
      await deps.store.releaseTask({ taskId: task.id, workerId: config.workerId });
    }
  }

  logger.info('worker stopped', { workerId: config.workerId });
}

/** Process bootstrap. Kept separate so the pieces above stay importable. */
export async function main(): Promise<void> {
  const logger = createConsoleLogger(SERVICE_NAME);
  const config = loadWorkerConfig();
  const deps = createWorkerDependencies(config);
  const controller = new AbortController();

  const shutdown = (signal: string): void => {
    logger.info('shutdown requested', { signal, workerId: config.workerId });
    controller.abort();
    const timer = setTimeout(() => {
      logger.error('shutdown window exceeded, exiting', { timeoutMs: config.shutdownTimeoutMs });
      process.exit(1);
    }, config.shutdownTimeoutMs);
    timer.unref();
  };

  const signals: readonly NodeJS.Signals[] = ['SIGINT', 'SIGTERM'];
  for (const signal of signals) {
    process.on(signal, () => {
      shutdown(signal);
    });
  }

  await runWorkerLoop(config, deps, logger, controller.signal);
  await deps.store.close();
  logger.info('worker exited');
  process.exit(0);
}

const entryPoint = process.argv[1];
if (entryPoint !== undefined && import.meta.url === pathToFileURL(entryPoint).href) {
  main().catch((error: unknown) => {
    createConsoleLogger(SERVICE_NAME).error('worker failed to start', {
      error: error instanceof Error ? error.message : String(error),
    });
    process.exitCode = 1;
  });
}
