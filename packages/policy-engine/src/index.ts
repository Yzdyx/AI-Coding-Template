/**
 * Public surface of @agent-platform/policy-engine.
 */

export type { FeatureFlagConfig, FeatureFlagProvider } from './flags.js';
export { ReferenceFeatureFlagProvider } from './flags.js';

export type {
  PolicyEngine,
  PolicyEngineConfig,
  PolicyRequest,
  ToolCallOptions,
  ToolCallRequest,
} from './engine.js';
export {
  ALLOW_PERMITTED,
  DENY_ACTOR_MISSING,
  DENY_IDEMPOTENCY_KEY_MISSING,
  DENY_TOOL_DENIED,
  REQUIRE_APPROVAL_HIGH_RISK,
  ReferencePolicyEngine,
  createPolicyEngine,
  isHighRisk,
} from './engine.js';

/** Re-exported so a consumer needs one import for a decision and its shape. */
export type { PolicyDecision, PolicyEffect } from '@agent-platform/agent-contracts';
