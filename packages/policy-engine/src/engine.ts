/**
 * Authorization decisions.
 *
 * Layer: Service. The engine fails closed: a request it cannot evaluate is
 * denied. It is injected at the composition root; no layer constructs it.
 *
 * The decision logic mirrors infra/policies/agent-tool-access.rego. Keep the two
 * in step: a change to one is a change to the other, reviewed by @security-team.
 */

import type { PolicyDecision, PolicyEffect, RiskLevel } from '@agent-platform/agent-contracts';

/** One request to act on a resource, for example creating a run. */
export interface PolicyRequest {
  readonly action: string;
  readonly actor: string;
  readonly resource: {
    readonly type: string;
    readonly id: string;
  };
  readonly context?: Readonly<Record<string, unknown>>;
}

/** One tool call awaiting a decision. */
export interface ToolCallRequest {
  readonly name: string;
  readonly arguments: Readonly<Record<string, unknown>>;
  readonly runId: string;
  readonly agentId: string;
  readonly actor: string;
}

/** Facts about the attempt that the decision depends on. */
export interface ToolCallOptions {
  readonly idempotencyKey: string;
  readonly attempt: number;
}

/** Contract implemented by the reference engine and by a policy-bundle engine. */
export interface PolicyEngine {
  /** Decides a resource action. Never throws on a malformed request: it denies. */
  evaluate(request: PolicyRequest): Promise<PolicyDecision>;
  /** Decides a tool call. Never throws on a malformed request: it denies. */
  evaluateToolCall(request: ToolCallRequest, options: ToolCallOptions): Promise<PolicyDecision>;
}

/** Configuration for the reference engine. */
export interface PolicyEngineConfig {
  /** Policy bundle name. It must exist under infra/policies/. */
  readonly bundle: string;
  /** Tools that need human approval regardless of the bundle. */
  readonly highRiskTools?: readonly string[];
  /** Tools that are denied outright, whatever the manifest declares. */
  readonly deniedTools?: readonly string[];
}

/** Stable identifiers for the reasons this engine reports. */
export const DENY_ACTOR_MISSING = 'actor_missing';
export const DENY_TOOL_DENIED = 'tool_denied_by_bundle';
export const DENY_IDEMPOTENCY_KEY_MISSING = 'idempotency_key_missing';
export const REQUIRE_APPROVAL_HIGH_RISK = 'high_risk_requires_approval';
export const ALLOW_PERMITTED = 'action_permitted_by_bundle';

/**
 * Reference policy engine.
 *
 * It has no knowledge of tool risk metadata: the risk class arrives through the
 * bundle configuration. A tool that is not listed as high risk is allowed when
 * it carries an idempotency key, because the operation log can then replay it
 * instead of repeating the effect.
 */
export class ReferencePolicyEngine implements PolicyEngine {
  readonly #bundle: string;
  readonly #highRisk: readonly string[];
  readonly #denied: readonly string[];

  constructor(config: PolicyEngineConfig) {
    this.#bundle = config.bundle;
    this.#highRisk = config.highRiskTools ?? [];
    this.#denied = config.deniedTools ?? [];
  }

  get bundle(): string {
    return this.#bundle;
  }

  #decision(effect: PolicyEffect, reason: string): PolicyDecision {
    return { decision: effect, reason, policyId: this.#bundle };
  }

  async evaluate(request: PolicyRequest): Promise<PolicyDecision> {
    if (request.actor === '' || request.actor === 'anonymous') {
      return this.#decision('deny', DENY_ACTOR_MISSING);
    }
    return this.#decision('allow', ALLOW_PERMITTED);
  }

  async evaluateToolCall(
    request: ToolCallRequest,
    options: ToolCallOptions,
  ): Promise<PolicyDecision> {
    if (request.actor === '' || request.actor === 'anonymous') {
      return this.#decision('deny', DENY_ACTOR_MISSING);
    }

    if (this.#denied.includes(request.name)) {
      return this.#decision('deny', DENY_TOOL_DENIED);
    }

    if (options.idempotencyKey === '') {
      return this.#decision('deny', DENY_IDEMPOTENCY_KEY_MISSING);
    }

    if (this.#highRisk.includes(request.name)) {
      return this.#decision('require_approval', REQUIRE_APPROVAL_HIGH_RISK);
    }

    return this.#decision('allow', ALLOW_PERMITTED);
  }
}

/** Builds the reference policy engine from its configuration. */
export function createPolicyEngine(config: PolicyEngineConfig): PolicyEngine {
  return new ReferencePolicyEngine(config);
}

/** Convenience helper for callers that hold a risk level instead of a bundle. */
export function isHighRisk(risk: RiskLevel): boolean {
  return risk === 'high';
}
