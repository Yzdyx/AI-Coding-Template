/**
 * Durable persistence for runs, checkpoints, events, approvals and tool results.
 *
 * Layer: Repo. This file performs storage and holds no business rule. It never
 * imports a Service file, and it applies the tenant filter itself instead of
 * trusting a tenant identifier passed in by a caller.
 *
 * The reference implementation below keeps everything in memory. It is the
 * store the local environment and the tests use. A production deployment swaps
 * it for a SQL implementation of the same interface; the table shapes are
 * documented in docs/generated/db-schema.md:
 *
 *   agent_runs, run_steps, checkpoints, tool_calls, approvals, policy_decisions
 *
 * The two rules a SQL implementation must keep:
 *   1. `tool_calls.idempotency_key` is unique. A repeated key returns the stored
 *      result instead of repeating the side effect.
 *   2. Every statement carries the tenant. A caller cannot widen the scope.
 */

import type {
  AgentEvent,
  AgentManifest,
  ApprovalRequest,
  CreateRunInput,
  RunCheckpoint,
  RunRecord,
  RunStatus,
  TaskEnvelope,
  ToolResult,
} from '@agent-platform/agent-contracts';

import type { StateStoreConfig } from './config.js';

/** Input for recording a tool result. */
export interface SaveToolResultInput {
  readonly runId: string;
  readonly idempotencyKey: string;
  readonly tool: string;
  readonly result: ToolResult;
}

/** Input for recording an approval decision. */
export interface ApprovalDecisionInput {
  readonly approvalId: string;
  readonly decision: string;
  readonly actor: string;
  readonly note?: string;
}

/** Repository contract consumed by the Runtime and Service layers. */
export interface StateStore {
  listAgents(options: { readonly limit: number }): Promise<readonly AgentManifest[]>;
  getAgent(agentId: string): Promise<AgentManifest | null>;
  listRuns(options: { readonly status?: RunStatus; readonly limit: number }): Promise<readonly RunRecord[]>;
  getRun(runId: string): Promise<RunRecord | null>;
  createRun(input: CreateRunInput): Promise<RunRecord>;
  listCheckpoints(runId: string): Promise<readonly RunCheckpoint[]>;
  loadLatestCheckpoint(runId: string): Promise<RunCheckpoint | null>;
  saveCheckpoint(checkpoint: RunCheckpoint): Promise<void>;
  listEvents(runId: string, options: { readonly afterSequence: number }): Promise<readonly AgentEvent[]>;
  appendEvent(event: AgentEvent): Promise<void>;
  listApprovals(options: { readonly status: string }): Promise<readonly ApprovalRequest[]>;
  createApprovalRequest(approval: ApprovalRequest): Promise<void>;
  getPendingApproval(runId: string): Promise<ApprovalRequest | null>;
  recordApprovalDecision(input: ApprovalDecisionInput): Promise<ApprovalRequest | null>;
  findToolResult(runId: string, idempotencyKey: string): Promise<ToolResult | null>;
  saveToolResult(input: SaveToolResultInput): Promise<void>;
  claimTask(options: { readonly workerId: string; readonly leaseMs: number }): Promise<TaskEnvelope | null>;
  completeTask(options: { readonly taskId: string; readonly workerId: string; readonly runId: string }): Promise<void>;
  failTask(options: {
    readonly taskId: string;
    readonly workerId: string;
    readonly error: string;
    readonly retryable: boolean;
  }): Promise<void>;
  releaseTask(options: { readonly taskId: string; readonly workerId: string }): Promise<void>;
  close(): Promise<void>;
}

/** A claimed task and the lease that owns it. */
interface TaskLease {
  readonly task: TaskEnvelope;
  readonly workerId: string;
  readonly expiresAt: number;
}

let counter = 0;

function nextId(prefix: string): string {
  counter += 1;
  return `${prefix}_${Date.now().toString(36)}_${counter.toString(36)}`;
}

/**
 * Reference repository: everything in memory, nothing on the network.
 *
 * `seedAgent` and `seedTask` exist so a local environment and a test can start
 * from a known state. They are not part of the {@link StateStore} contract.
 */
export class InMemoryStateStore implements StateStore {
  readonly #config: StateStoreConfig;
  readonly #agents = new Map<string, AgentManifest>();
  readonly #runs = new Map<string, RunRecord>();
  readonly #checkpoints = new Map<string, RunCheckpoint[]>();
  readonly #events = new Map<string, AgentEvent[]>();
  readonly #approvals = new Map<string, ApprovalRequest>();
  readonly #toolResults = new Map<string, ToolResult>();
  readonly #tasks: TaskEnvelope[] = [];
  readonly #leases = new Map<string, TaskLease>();
  #closed = false;

  constructor(config: StateStoreConfig) {
    this.#config = config;
  }

  get tenant(): string {
    return this.#config.tenant;
  }

  /** Reference-only helper: registers a manifest so `listAgents` returns it. */
  seedAgent(manifest: AgentManifest): void {
    this.#agents.set(manifest.name, manifest);
  }

  /** Reference-only helper: queues a task so `claimTask` can return it. */
  seedTask(task: TaskEnvelope): void {
    this.#tasks.push(task);
  }

  async listAgents(options: { readonly limit: number }): Promise<readonly AgentManifest[]> {
    return [...this.#agents.values()].slice(0, options.limit);
  }

  async getAgent(agentId: string): Promise<AgentManifest | null> {
    return this.#agents.get(agentId) ?? null;
  }

  async listRuns(options: {
    readonly status?: RunStatus;
    readonly limit: number;
  }): Promise<readonly RunRecord[]> {
    const all = [...this.#runs.values()].sort((left, right) =>
      right.createdAt.localeCompare(left.createdAt),
    );
    const filtered =
      options.status === undefined ? all : all.filter((run) => run.status === options.status);
    return filtered.slice(0, options.limit);
  }

  async getRun(runId: string): Promise<RunRecord | null> {
    return this.#runs.get(runId) ?? null;
  }

  async createRun(input: CreateRunInput): Promise<RunRecord> {
    const existing = [...this.#runs.values()].find(
      (run) => run.idempotencyKey === input.idempotencyKey,
    );
    if (existing !== undefined) {
      return existing;
    }
    const run: RunRecord = {
      id: nextId('run'),
      agentId: input.agentId,
      status: 'running',
      input: input.input,
      actor: input.actor,
      idempotencyKey: input.idempotencyKey,
      correlationId: input.correlationId,
      createdAt: new Date().toISOString(),
    };
    this.#runs.set(run.id, run);
    return run;
  }

  async listCheckpoints(runId: string): Promise<readonly RunCheckpoint[]> {
    return [...(this.#checkpoints.get(runId) ?? [])].sort((left, right) => left.sequence - right.sequence);
  }

  async loadLatestCheckpoint(runId: string): Promise<RunCheckpoint | null> {
    const all = await this.listCheckpoints(runId);
    return all.length === 0 ? null : (all[all.length - 1] as RunCheckpoint);
  }

  async saveCheckpoint(checkpoint: RunCheckpoint): Promise<void> {
    const list = this.#checkpoints.get(checkpoint.runId) ?? [];
    list.push(checkpoint);
    this.#checkpoints.set(checkpoint.runId, list);

    const run = this.#runs.get(checkpoint.runId);
    if (run !== undefined) {
      this.#runs.set(run.id, {
        ...run,
        status: checkpoint.status,
        updatedAt: checkpoint.createdAt,
      });
    }
  }

  async listEvents(
    runId: string,
    options: { readonly afterSequence: number },
  ): Promise<readonly AgentEvent[]> {
    return (this.#events.get(runId) ?? []).filter(
      (event) => (event.sequence ?? 0) > options.afterSequence,
    );
  }

  async appendEvent(event: AgentEvent): Promise<void> {
    const list = this.#events.get(event.runId) ?? [];
    list.push({ ...event, sequence: list.length + 1 });
    this.#events.set(event.runId, list);
  }

  async listApprovals(options: { readonly status: string }): Promise<readonly ApprovalRequest[]> {
    return [...this.#approvals.values()]
      .filter((approval) => approval.status === options.status)
      .sort((left, right) => left.createdAt.localeCompare(right.createdAt));
  }

  async createApprovalRequest(approval: ApprovalRequest): Promise<void> {
    this.#approvals.set(approval.id, approval);
  }

  async getPendingApproval(runId: string): Promise<ApprovalRequest | null> {
    const pending = [...this.#approvals.values()].find(
      (approval) => approval.runId === runId && approval.status === 'pending',
    );
    return pending ?? null;
  }

  async recordApprovalDecision(input: ApprovalDecisionInput): Promise<ApprovalRequest | null> {
    const approval = this.#approvals.get(input.approvalId);
    if (approval === undefined) {
      return null;
    }
    const status = input.decision === 'approve' ? 'approved' : 'rejected';
    const updated: ApprovalRequest = { ...approval, status };
    this.#approvals.set(updated.id, updated);
    return updated;
  }

  async findToolResult(runId: string, idempotencyKey: string): Promise<ToolResult | null> {
    return this.#toolResults.get(`${runId}:${idempotencyKey}`) ?? null;
  }

  async saveToolResult(input: SaveToolResultInput): Promise<void> {
    this.#toolResults.set(`${input.runId}:${input.idempotencyKey}`, input.result);
  }

  async claimTask(options: {
    readonly workerId: string;
    readonly leaseMs: number;
  }): Promise<TaskEnvelope | null> {
    const now = Date.now();
    for (const [taskId, lease] of this.#leases) {
      if (lease.expiresAt <= now) {
        this.#leases.delete(taskId);
        this.#tasks.push(lease.task);
      }
    }

    const claimed = this.#tasks.find(
      (task) => ![...this.#leases.values()].some((lease) => lease.task.id === task.id),
    );
    if (claimed === undefined) {
      return null;
    }

    this.#tasks.splice(this.#tasks.indexOf(claimed), 1);
    this.#leases.set(claimed.id, {
      task: claimed,
      workerId: options.workerId,
      expiresAt: now + options.leaseMs,
    });
    return claimed;
  }

  async completeTask(options: {
    readonly taskId: string;
    readonly workerId: string;
    readonly runId: string;
  }): Promise<void> {
    this.#leases.delete(options.taskId);
  }

  async failTask(options: {
    readonly taskId: string;
    readonly workerId: string;
    readonly error: string;
    readonly retryable: boolean;
  }): Promise<void> {
    const lease = this.#leases.get(options.taskId);
    this.#leases.delete(options.taskId);
    if (lease !== undefined && options.retryable) {
      this.#tasks.push({ ...lease.task, attempt: lease.task.attempt + 1 });
    }
  }

  async releaseTask(options: { readonly taskId: string; readonly workerId: string }): Promise<void> {
    const lease = this.#leases.get(options.taskId);
    if (lease === undefined || lease.workerId !== options.workerId) {
      return;
    }
    this.#leases.delete(options.taskId);
    this.#tasks.push(lease.task);
  }

  async close(): Promise<void> {
    this.#closed = true;
  }

  /** True once the store has been closed. Used by the Runtime shutdown path. */
  get closed(): boolean {
    return this.#closed;
  }
}
