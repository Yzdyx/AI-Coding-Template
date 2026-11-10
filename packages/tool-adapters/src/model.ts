/**
 * Model provider.
 *
 * Layer: Repo. It turns a request into a completion. The reference
 * implementation is deterministic and offline: it derives a plan from the
 * request instead of calling a model, so a local environment and the tests run
 * without a model service.
 *
 * A production composition root injects a `transport` that calls the real
 * provider. The transport is the only place a network call belongs.
 */

import type { ModelMessage, ToolInvocation } from '@agent-platform/agent-contracts';

/** One request to a model. */
export interface ModelRequest {
  /** Model identifier, as the manifest declares it. */
  readonly modelId: string;
  readonly systemPrompt: string;
  readonly messages: readonly ModelMessage[];
  /** Tool names the model may propose. The manifest is the source of truth. */
  readonly tools: readonly string[];
  /** Deterministic key. A replayed request must return the same completion. */
  readonly idempotencyKey: string;
}

/** One completion. */
export interface ModelCompletion {
  readonly model: string;
  readonly content: string;
  readonly toolInvocations: readonly ToolInvocation[];
}

/** Calls the real model. The only component allowed to use the network. */
export type ModelTransport = (request: ModelRequest) => Promise<ModelCompletion>;

/** Configuration for the reference model provider. */
export interface ModelProviderConfig {
  /** Provider endpoint. Recorded for the audit trail; the reference build does not call it. */
  readonly endpoint: string;
  /** Real transport. Required outside a local environment. */
  readonly transport?: ModelTransport;
}

/** Contract consumed by the Runtime and Service layers. */
export interface ModelProvider {
  complete(request: ModelRequest): Promise<ModelCompletion>;
  readonly endpoint: string;
}

/** The last user message of a request, or an empty string. */
function lastUserMessage(request: ModelRequest): string {
  for (let index = request.messages.length - 1; index >= 0; index -= 1) {
    const message = request.messages[index];
    if (message !== undefined && message.role === 'user') {
      return message.content;
    }
  }
  return '';
}

/**
 * Reference planning rule.
 *
 * When the request allows a tool named `search`, the provider proposes exactly
 * one call to it, with the last user message as the query. Otherwise it proposes
 * nothing and says so. The rule is small on purpose: it makes a local run
 * reproducible, and it never invents a tool that the manifest does not declare.
 */
export function planWithoutModel(request: ModelRequest): ModelCompletion {
  const query = lastUserMessage(request);
  if (request.tools.includes('search') && query !== '') {
    return {
      model: request.modelId,
      content: '',
      toolInvocations: [{ name: 'search', arguments: { query } }],
    };
  }
  return {
    model: request.modelId,
    content:
      'The reference model provider could not derive a plan. Configure a transport to call a real model.',
    toolInvocations: [],
  };
}

/** Reference model provider: deterministic, offline, no network call. */
export class ReferenceModelProvider implements ModelProvider {
  readonly endpoint: string;
  readonly #transport: ModelTransport;

  constructor(config: ModelProviderConfig) {
    this.endpoint = config.endpoint;
    this.#transport = config.transport ?? (async (request) => planWithoutModel(request));
  }

  async complete(request: ModelRequest): Promise<ModelCompletion> {
    if (request.tools.length === 0) {
      throw new Error('a model request must declare at least one tool');
    }
    return this.#transport(request);
  }
}

/** Builds the model provider from its configuration. */
export function createModelProvider(config: ModelProviderConfig): ModelProvider {
  return new ReferenceModelProvider(config);
}
