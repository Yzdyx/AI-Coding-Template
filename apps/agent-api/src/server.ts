/**
 * HTTP routing layer for the agent API.
 *
 * Layer: Runtime. This module owns transport concerns only: it parses the
 * request, resolves the caller, dispatches to a typed handler, and serialises
 * the response. Every business rule lives behind an injected dependency, so
 * the routing layer can be exercised without a network or a database.
 */

import { randomUUID } from 'node:crypto';
import { createServer } from 'node:http';
import type { IncomingMessage, Server, ServerResponse } from 'node:http';

import type {
  AgentEvent,
  AgentManifest,
  ApprovalRequest,
  RunCheckpoint,
  RunRecord,
  RunStatus,
} from '@agent-platform/agent-contracts';
import type { Span, TelemetryProvider } from '@agent-platform/observability';
import { createTelemetryProvider } from '@agent-platform/observability';
import type { PolicyDecision, PolicyEngine } from '@agent-platform/policy-engine';
import { createPolicyEngine } from '@agent-platform/policy-engine';
import type { StateStore } from '@agent-platform/state-store';
import { createStateStore, loadStateStoreConfig } from '@agent-platform/state-store';
import type { IdentityProvider, Principal } from '@agent-platform/tool-adapters';
import { createIdentityProvider } from '@agent-platform/tool-adapters';

/** Maximum accepted request body, in bytes. Larger bodies are rejected. */
const MAX_BODY_BYTES = 256 * 1024;

/** Fallback endpoint used when no telemetry collector is configured. */
const DEFAULT_TELEMETRY_ENDPOINT = 'https://telemetry.example.com';

/** Fallback identity issuer used when none is configured. */
const DEFAULT_IDENTITY_ISSUER = 'https://identity.example.com';

/** HTTP methods this service answers. */
export type HttpMethod = 'GET' | 'POST';

/** Runtime configuration consumed by the routing layer. */
export interface AgentApiConfig {
  readonly serviceName: string;
  readonly host: string;
  readonly port: number;
  readonly basePath: string;
  readonly stateStoreUrl: string;
  readonly modelProviderUrl: string;
  readonly policyBundle: string;
  readonly shutdownTimeoutMs: number;
  readonly requireAuth: boolean;
}

/** Minimal logging contract. The Runtime owns logging at its own edge. */
export interface AgentApiLogger {
  info(message: string, fields?: Record<string, unknown>): void;
  warn(message: string, fields?: Record<string, unknown>): void;
  error(message: string, fields?: Record<string, unknown>): void;
}

/** Everything a handler may use. Assembled once, at start-up. */
export interface AgentApiDependencies {
  readonly store: StateStore;
  readonly policy: PolicyEngine;
  readonly telemetry: TelemetryProvider;
  readonly identity: IdentityProvider;
}

/** Per-request input handed to a route handler. */
export interface RequestContext {
  readonly request: IncomingMessage;
  readonly url: URL;
  readonly params: Readonly<Record<string, string>>;
  readonly correlationId: string;
  readonly principal: Principal | null;
  readonly body: unknown;
}

/** Per-request output produced by a route handler. */
export interface RouteResult {
  readonly status: number;
  readonly body: unknown;
  readonly headers?: Readonly<Record<string, string>>;
}

/** Explicit handler type. Every route is a function of exactly this shape. */
export type RouteHandler = (context: RequestContext) => Promise<RouteResult>;

/** One routable endpoint. */
export interface RouteDefinition {
  readonly method: HttpMethod;
  readonly path: string;
  readonly requiresAuth: boolean;
  readonly handler: RouteHandler;
}

/** Lifecycle handle returned to the Runtime entry point. */
export interface AgentApiServer {
  readonly address: string;
  listen(): Promise<void>;
  close(): Promise<void>;
}

/** Raised by a handler to produce a structured error response. */
export class HttpError extends Error {
  readonly status: number;
  readonly code: string;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
    this.code = code;
  }
}

interface RouteMatch {
  readonly route: RouteDefinition;
  readonly params: Readonly<Record<string, string>>;
}

interface CreateRunInput {
  readonly agentId: string;
  readonly input: Record<string, unknown>;
  readonly idempotencyKey: string;
}

interface ApprovalDecisionInput {
  readonly decision: 'approved' | 'rejected';
  readonly note: string;
}

/** Splits a path into its non-empty segments. */
function segmentsOf(path: string): readonly string[] {
  return path.split('/').filter((segment) => segment.length > 0);
}

/**
 * Matches a route pattern against a concrete path.
 *
 * Returns the extracted path parameters, or `null` when the path does not
 * match. A segment written as `:name` captures the corresponding value.
 */
function matchPath(pattern: string, path: string): Record<string, string> | null {
  const patternParts = segmentsOf(pattern);
  const pathParts = segmentsOf(path);
  if (patternParts.length !== pathParts.length) {
    return null;
  }
  const params: Record<string, string> = {};
  for (let index = 0; index < patternParts.length; index += 1) {
    const expected = patternParts[index] as string;
    const actual = pathParts[index] as string;
    if (expected.startsWith(':')) {
      params[expected.slice(1)] = decodeURIComponent(actual);
    } else if (expected !== actual) {
      return null;
    }
  }
  return params;
}

/** Finds the first route matching the method and path. */
function findRoute(routes: readonly RouteDefinition[], method: HttpMethod, path: string): RouteMatch | null {
  for (const route of routes) {
    if (route.method !== method) {
      continue;
    }
    const params = matchPath(route.path, path);
    if (params !== null) {
      return { route, params };
    }
  }
  return null;
}

/** Reads a bounded integer query parameter. */
function readQueryInt(url: URL, key: string, fallback: number, min: number, max: number): number {
  const raw = url.searchParams.get(key);
  if (raw === null || raw.trim() === '') {
    return fallback;
  }
  const parsed = Number.parseInt(raw, 10);
  if (Number.isNaN(parsed)) {
    throw new HttpError(400, 'invalid_query', `Query parameter "${key}" must be an integer`);
  }
  if (parsed < min || parsed > max) {
    throw new HttpError(400, 'invalid_query', `Query parameter "${key}" must be between ${min} and ${max}`);
  }
  return parsed;
}

/** Validates and narrows the body of a create-run request. */
function parseCreateRunInput(body: unknown): CreateRunInput {
  if (typeof body !== 'object' || body === null || Array.isArray(body)) {
    throw new HttpError(400, 'invalid_body', 'A JSON object body is required');
  }
  const record = body as Record<string, unknown>;

  const agentId = record['agentId'];
  if (typeof agentId !== 'string' || agentId.trim() === '') {
    throw new HttpError(400, 'invalid_agent_id', 'Field "agentId" must be a non-empty string');
  }

  const idempotencyKey = record['idempotencyKey'];
  if (typeof idempotencyKey !== 'string' || idempotencyKey.trim() === '') {
    throw new HttpError(400, 'invalid_idempotency_key', 'Field "idempotencyKey" must be a non-empty string');
  }

  const rawInput = record['input'];
  if (rawInput !== undefined && (typeof rawInput !== 'object' || rawInput === null || Array.isArray(rawInput))) {
    throw new HttpError(400, 'invalid_input', 'Field "input" must be a JSON object when present');
  }

  return {
    agentId,
    idempotencyKey,
    input: (rawInput as Record<string, unknown> | undefined) ?? {},
  };
}

/** Validates and narrows the body of an approval decision request. */
function parseApprovalDecision(body: unknown): ApprovalDecisionInput {
  if (typeof body !== 'object' || body === null || Array.isArray(body)) {
    throw new HttpError(400, 'invalid_body', 'A JSON object body is required');
  }
  const record = body as Record<string, unknown>;

  const decision = record['decision'];
  if (decision !== 'approved' && decision !== 'rejected') {
    throw new HttpError(400, 'invalid_decision', 'Field "decision" must be "approved" or "rejected"');
  }

  const rawNote = record['note'];
  if (rawNote !== undefined && typeof rawNote !== 'string') {
    throw new HttpError(400, 'invalid_note', 'Field "note" must be a string when present');
  }

  return { decision, note: rawNote ?? '' };
}

/** Reads the whole request body and parses it as JSON. */
async function readJsonBody(request: IncomingMessage, limitBytes: number): Promise<unknown> {
  const chunks: Buffer[] = [];
  let total = 0;
  for await (const chunk of request) {
    const buffer = chunk as Buffer;
    total += buffer.length;
    if (total > limitBytes) {
      throw new HttpError(413, 'payload_too_large', `Request body exceeds ${limitBytes} bytes`);
    }
    chunks.push(buffer);
  }
  if (total === 0) {
    return null;
  }
  const text = Buffer.concat(chunks).toString('utf8');
  try {
    return JSON.parse(text) as unknown;
  } catch {
    throw new HttpError(400, 'invalid_json', 'Request body is not valid JSON');
  }
}

/** Builds the standard error envelope. */
function errorBody(code: string, message: string, correlationId: string): Record<string, unknown> {
  return { error: { code, message, correlationId } };
}

/** Writes a JSON response, including the correlation identifier. */
function writeJson(response: ServerResponse, result: RouteResult, correlationId: string): void {
  response.statusCode = result.status;
  response.setHeader('content-type', 'application/json; charset=utf-8');
  response.setHeader('x-correlation-id', correlationId);
  for (const [key, value] of Object.entries(result.headers ?? {})) {
    response.setHeader(key, value);
  }
  response.end(JSON.stringify(result.body));
}

/**
 * Builds the route table.
 *
 * Handlers receive the request context and return a `RouteResult`. They never
 * touch the socket directly, so they remain unit-testable.
 */
function createRoutes(deps: AgentApiDependencies, config: AgentApiConfig): readonly RouteDefinition[] {
  const { store, policy } = deps;

  const health: RouteHandler = async (): Promise<RouteResult> => ({
    status: 200,
    body: { status: 'ok', service: config.serviceName, time: new Date().toISOString() },
  });

  const listAgents: RouteHandler = async ({ url }): Promise<RouteResult> => {
    const limit = readQueryInt(url, 'limit', 50, 1, 200);
    const manifests: readonly AgentManifest[] = await store.listAgents({ limit });
    return { status: 200, body: { items: manifests, count: manifests.length } };
  };

  const getAgent: RouteHandler = async ({ params }): Promise<RouteResult> => {
    const agentId = params['agentId'] ?? '';
    const manifest = await store.getAgent(agentId);
    if (manifest === null) {
      throw new HttpError(404, 'agent_not_found', `Unknown agent "${agentId}"`);
    }
    return { status: 200, body: manifest };
  };

  const listRuns: RouteHandler = async ({ url }): Promise<RouteResult> => {
    const statusParam = url.searchParams.get('status');
    const status = statusParam === null ? undefined : (statusParam as RunStatus);
    const limit = readQueryInt(url, 'limit', 50, 1, 200);
    const runs: readonly RunRecord[] = await store.listRuns({ status, limit });
    return { status: 200, body: { items: runs, count: runs.length } };
  };

  const getRun: RouteHandler = async ({ params }): Promise<RouteResult> => {
    const runId = params['runId'] ?? '';
    const run = await store.getRun(runId);
    if (run === null) {
      throw new HttpError(404, 'run_not_found', `Unknown run "${runId}"`);
    }
    const checkpoints: readonly RunCheckpoint[] = await store.listCheckpoints(runId);
    return { status: 200, body: { run, checkpoints } };
  };

  const listRunEvents: RouteHandler = async ({ params, url }): Promise<RouteResult> => {
    const runId = params['runId'] ?? '';
    const after = readQueryInt(url, 'after', 0, 0, Number.MAX_SAFE_INTEGER);
    const events: readonly AgentEvent[] = await store.listEvents(runId, { afterSequence: after });
    return { status: 200, body: { items: events, count: events.length } };
  };

  const createRun: RouteHandler = async ({ body, principal, correlationId }): Promise<RouteResult> => {
    const input = parseCreateRunInput(body);
    const actor = principal?.subject ?? 'anonymous';

    const decision: PolicyDecision = await policy.evaluate({
      action: 'run:create',
      actor,
      resource: { type: 'agent', id: input.agentId },
      context: { correlationId },
    });
    if (decision.decision === 'deny') {
      throw new HttpError(403, 'policy_denied', decision.reason);
    }

    const run = await store.createRun({
      agentId: input.agentId,
      input: input.input,
      actor,
      idempotencyKey: input.idempotencyKey,
      correlationId,
    });
    return {
      status: 202,
      body: run,
      headers: { location: `${config.basePath}/runs/${run.id}` },
    };
  };

  const listApprovals: RouteHandler = async ({ url }): Promise<RouteResult> => {
    const status = url.searchParams.get('status') ?? 'pending';
    const approvals: readonly ApprovalRequest[] = await store.listApprovals({ status });
    return { status: 200, body: { items: approvals, count: approvals.length } };
  };

  const decideApproval: RouteHandler = async ({ params, body, principal }): Promise<RouteResult> => {
    const approvalId = params['approvalId'] ?? '';
    const parsed = parseApprovalDecision(body);
    const actor = principal?.subject ?? 'anonymous';

    const decision: PolicyDecision = await policy.evaluate({
      action: 'approval:decide',
      actor,
      resource: { type: 'approval', id: approvalId },
    });
    if (decision.decision === 'deny') {
      throw new HttpError(403, 'policy_denied', decision.reason);
    }

    const updated = await store.recordApprovalDecision({
      approvalId,
      decision: parsed.decision,
      actor,
      note: parsed.note,
    });
    if (updated === null) {
      throw new HttpError(404, 'approval_not_found', `Unknown approval "${approvalId}"`);
    }
    return { status: 200, body: updated };
  };

  return [
    { method: 'GET', path: '/healthz', requiresAuth: false, handler: health },
    { method: 'GET', path: '/agents', requiresAuth: true, handler: listAgents },
    { method: 'GET', path: '/agents/:agentId', requiresAuth: true, handler: getAgent },
    { method: 'GET', path: '/runs', requiresAuth: true, handler: listRuns },
    { method: 'POST', path: '/runs', requiresAuth: true, handler: createRun },
    { method: 'GET', path: '/runs/:runId', requiresAuth: true, handler: getRun },
    { method: 'GET', path: '/runs/:runId/events', requiresAuth: true, handler: listRunEvents },
    { method: 'GET', path: '/approvals', requiresAuth: true, handler: listApprovals },
    { method: 'POST', path: '/approvals/:approvalId/decision', requiresAuth: true, handler: decideApproval },
  ];
}

/**
 * Builds the dependencies from configuration.
 *
 * Cross-cutting capabilities enter through their Provider interfaces, never
 * through a direct import of another package's internals.
 */
export function createAgentApiDependencies(config: AgentApiConfig): AgentApiDependencies {
  return {
    store: createStateStore(loadStateStoreConfig({ url: config.stateStoreUrl })),
    policy: createPolicyEngine({ bundle: config.policyBundle }),
    telemetry: createTelemetryProvider({
      serviceName: config.serviceName,
      endpoint: process.env['OTEL_EXPORTER_OTLP_ENDPOINT'] ?? DEFAULT_TELEMETRY_ENDPOINT,
    }),
    identity: createIdentityProvider({
      issuer: process.env['AGENT_IDENTITY_ISSUER'] ?? DEFAULT_IDENTITY_ISSUER,
    }),
  };
}

/**
 * Creates the HTTP server.
 *
 * The returned handle exposes only `listen` and `close` so the Runtime entry
 * point cannot reach into the socket.
 */
export async function createAgentApiServer(
  config: AgentApiConfig,
  logger: AgentApiLogger,
): Promise<AgentApiServer> {
  const deps = createAgentApiDependencies(config);
  const routes = createRoutes(deps, config);

  const handle = async (request: IncomingMessage, response: ServerResponse): Promise<void> => {
    const correlationId = String(request.headers['x-correlation-id'] ?? randomUUID());
    const startedAt = Date.now();
    const rawUrl = request.url ?? '/';
    const host = request.headers.host ?? `${config.host}:${config.port}`;
    const url = new URL(rawUrl, `http://${host}`);
    const method = (request.method ?? 'GET').toUpperCase() as HttpMethod;
    const path = url.pathname.startsWith(config.basePath)
      ? url.pathname.slice(config.basePath.length) || '/'
      : url.pathname;

    const span: Span = deps.telemetry.startSpan('http.request', { method, route: path, correlationId });

    try {
      const match = findRoute(routes, method, path);
      if (match === null) {
        throw new HttpError(404, 'not_found', `No route for ${method} ${path}`);
      }

      const principal = config.requireAuth && match.route.requiresAuth
        ? await deps.identity.resolve(request.headers['authorization'])
        : null;
      if (config.requireAuth && match.route.requiresAuth && principal === null) {
        throw new HttpError(401, 'unauthenticated', 'A valid bearer credential is required');
      }

      const body = method === 'POST' ? await readJsonBody(request, MAX_BODY_BYTES) : null;
      const result = await match.route.handler({
        request,
        url,
        params: match.params,
        correlationId,
        principal,
        body,
      });

      writeJson(response, result, correlationId);
      if (result.status >= 400) {
        logger.warn('request rejected', { method, route: path, status: result.status, correlationId });
      }
    } catch (error) {
      const failure = error instanceof HttpError
        ? error
        : new HttpError(500, 'internal_error', 'The request could not be completed');
      if (!(error instanceof HttpError)) {
        span.recordError(error as Error);
        logger.error('request failed', {
          method,
          route: path,
          correlationId,
          error: error instanceof Error ? error.message : String(error),
        });
      }
      writeJson(response, { status: failure.status, body: errorBody(failure.code, failure.message, correlationId) }, correlationId);
    } finally {
      span.end();
      logger.info('request handled', {
        method,
        route: path,
        status: response.statusCode,
        correlationId,
        durationMs: Date.now() - startedAt,
      });
    }
  };

  const server: Server = createServer((request, response) => {
    void handle(request, response);
  });

  return {
    address: `${config.host}:${config.port}`,
    listen: (): Promise<void> =>
      new Promise<void>((resolve, reject) => {
        const onError = (error: Error): void => reject(error);
        server.once('error', onError);
        server.listen(config.port, config.host, () => {
          server.off('error', onError);
          resolve();
        });
      }),
    close: (): Promise<void> =>
      new Promise<void>((resolve, reject) => {
        server.close(async (error) => {
          await deps.store.close();
          if (error) {
            reject(error);
            return;
          }
          resolve();
        });
      }),
  };
}
