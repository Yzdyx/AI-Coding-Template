/**
 * Shared platform types.
 *
 * Layer: Types. Declarations only. No behaviour, no I/O, no import from any
 * other layer. A change to a type in this file is a contract change: review it
 * against docs/architecture/dependency-rules.md section 6.
 */

/** Lifecycle state of one agent run. */
export type RunStatus =
  | 'running'
  | 'awaiting_approval'
  | 'degraded'
  | 'succeeded'
  | 'failed'
  | 'cancelled';

/** Risk classification of a tool. `high` requires human approval. */
export type RiskLevel = 'low' | 'medium' | 'high';

/** Policy outcome. A policy engine that cannot decide returns `deny`. */
export type PolicyEffect = 'allow' | 'deny' | 'require_approval';

/** Decision on one approval request. */
export type ApprovalStatus = 'pending' | 'approved' | 'rejected';

/** Manifest contract. The schema is schemas/agent-manifest.schema.json. */
export interface AgentManifest {
  readonly name: string;
  readonly version: string;
  readonly owner: string;
  readonly description: string;
  readonly model: {
    readonly provider: string;
    readonly name: string;
    readonly temperature: number;
  };
  readonly tools: readonly string[];
  readonly limits: {
    readonly maxSteps: number;
    readonly timeoutSeconds: number;
  };
  readonly tests?: readonly string[];
}

/**
 * Compact run projection used by listings and the operator console.
 *
 * It is a view of a run, not the stored record: it carries the step count and
 * the degradation flag so a list view needs no second query.
 */
export interface AgentRunSummary {
  readonly runId: string;
  readonly agent: string;
  readonly status: RunStatus;
  readonly steps: number;
  readonly degraded?: boolean;
  readonly traceId: string;
  readonly createdAt: string;
}

/** One run, as recorded by the state store. */
export interface RunRecord {
  readonly id: string;
  readonly agentId: string;
  readonly status: RunStatus;
  readonly input: unknown;
  readonly actor: string;
  readonly idempotencyKey: string;
  readonly correlationId: string;
  readonly createdAt: string;
  readonly updatedAt?: string;
}

/** Input for RunRecord creation. */
export interface CreateRunInput {
  readonly agentId: string;
  readonly input: unknown;
  readonly actor: string;
  readonly idempotencyKey: string;
  readonly correlationId: string;
}

/**
 * One durable position of a run.
 *
 * `sequence` increases by one per checkpoint. A resumed run loads the checkpoint
 * with the highest sequence and continues from `stepIndex`.
 */
export interface RunCheckpoint {
  readonly runId: string;
  readonly sequence: number;
  readonly stepIndex: number;
  readonly status: RunStatus;
  readonly state: Readonly<Record<string, unknown>>;
  readonly createdAt: string;
}

/** One event of a run. The store assigns `sequence` when it appends the event. */
export interface AgentEvent {
  readonly id: string;
  readonly runId: string;
  readonly type: string;
  readonly payload: Readonly<Record<string, unknown>>;
  readonly createdAt: string;
  readonly sequence?: number;
}

/** A pending human approval for one high-risk tool call. */
export interface ApprovalRequest {
  readonly id: string;
  readonly runId: string;
  readonly taskId: string;
  readonly agentId: string;
  readonly tool: string;
  readonly arguments: Readonly<Record<string, unknown>>;
  readonly requestedBy: string;
  readonly reason: string;
  readonly status: ApprovalStatus;
  readonly createdAt: string;
  /** Present when the requester knows the risk class of the tool. */
  readonly risk?: RiskLevel;
}

/** One task claimed by a worker. */
export interface TaskEnvelope {
  readonly id: string;
  readonly runId: string;
  readonly agentId: string;
  readonly modelId: string;
  readonly systemPrompt: string;
  readonly input: unknown;
  readonly allowedTools: readonly string[];
  readonly requestedBy: string;
  readonly attempt: number;
}

/** One tool call proposed by a model completion. */
export interface ToolInvocation {
  readonly name: string;
  readonly arguments: Readonly<Record<string, unknown>>;
}

/** Result of one executed tool call. */
export interface ToolResult {
  readonly tool: string;
  readonly status: 'succeeded' | 'failed' | 'degraded';
  readonly output: unknown;
  readonly degraded: boolean;
}

/** Authorization decision returned by the policy engine. */
export interface PolicyDecision {
  readonly decision: PolicyEffect;
  readonly reason: string;
  readonly policyId: string;
}

/** One message in a model conversation. */
export interface ModelMessage {
  readonly role: 'system' | 'user' | 'assistant' | 'tool';
  readonly content: string;
}

/** A run is degraded when any step returned a partial result. */
export function isDegraded(status: RunStatus): boolean {
  return status === 'degraded';
}
