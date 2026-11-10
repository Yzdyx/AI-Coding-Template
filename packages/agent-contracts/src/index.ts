/**
 * Public surface of @agent-platform/agent-contracts.
 *
 * Consumers import from the package name only. A deep import into this
 * package's src/ is rejected by scripts/check-architecture.py.
 */

export type {
  AgentEvent,
  AgentManifest,
  AgentRunSummary,
  ApprovalRequest,
  ApprovalStatus,
  CreateRunInput,
  ModelMessage,
  PolicyDecision,
  PolicyEffect,
  RiskLevel,
  RunCheckpoint,
  RunRecord,
  RunStatus,
  TaskEnvelope,
  ToolInvocation,
  ToolResult,
} from './types.js';

export { isDegraded } from './types.js';
