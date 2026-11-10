# @agent-platform/tool-adapters

Provider interfaces and reference adapters for the three cross-domain
capabilities owned by this package. Business agents never talk to a model
vendor, an identity service, or an external system directly: they depend on the
interface and receive an implementation at process start.

| Capability | Interface | Module |
| --- | --- | --- |
| Model access | `ModelProvider` | `src/model.ts` |
| Identity | `IdentityProvider` | `src/identity.ts` |
| External connectors | `ConnectorProvider` | `src/connector.ts` |

This package owns the contracts and one working reference adapter per contract.
Vendor-specific adapters are added as further implementations of the same
interfaces. See `ARCHITECTURE.md`, section 3, for the provider table.

## Public API

### `src/model.ts` — model access

- `ModelProvider` — `complete(request, signal?)`.
- `ModelRequest`, `ModelMessage`, `ModelResponse`, `ModelUsage`, `ModelFinishReason`.
- `ReferenceModelProvider` — per-call timeout, bounded exponential backoff with
  jitter, and cumulative token accounting.
- `ModelTransport` — the wire boundary; `OpenAiCompatibleTransport` is a
  reference implementation that talks to any OpenAI-compatible endpoint.
- `TokenLedger`, `estimateTokenCount`, `DEFAULT_RETRY_POLICY`,
  `ModelProviderError`, `ModelProviderConfig`.

### `src/identity.ts` — authentication and authorization facts

- `IdentityProvider` — `verifyToken`, `getTenant`, `hasScope`, `authorize`.
- `Principal`, `Tenant`, `TokenClaims`, `AuthorizationRequirement`,
  `AuthorizationDecision`.
- `ReferenceIdentityProvider` — validates issuer, audience, and expiry (with
  clock skew), then maps verified claims onto a `Principal`.
- `TokenVerifier` — signature-verification contract, implemented per vendor.
- `InMemoryTokenVerifier` and `StaticTenantDirectory` — test doubles.
- `IdentityProviderConfig`, `IdentityError`, `parseScopeClaim`.

### `src/connector.ts` — external systems

- `ConnectorProvider` — `list`, `describe`, `call`.
- `ConnectorDescriptor`, `ConnectorOperation`, `ConnectorCallRequest`,
  `ConnectorCallResult`.
- `ReferenceConnectorProvider` — a typed connector registry with a
  schema-validated call path: scope check, JSON Schema input validation,
  idempotency replay, timeout, and JSON Schema output validation.
- `validateAgainstSchema` — dependency-free JSON Schema subset validator.
- `ConnectorRegistration`, `ConnectorError`, `ValidationIssue`.

### `src/index.ts` — factory

- `createToolAdapters(config)` — builds the three providers as one bundle.
- `createModelProvider`, `createIdentityProvider`, `createConnectorProvider` —
  per-provider factories.

## Usage

```ts
import {
  createToolAdapters,
  type ModelTransport,
  type TokenVerifier,
} from '@agent-platform/tool-adapters';

// Swap these two for real implementations. Tests inject fakes.
declare const modelTransport: ModelTransport;
declare const tokenVerifier: TokenVerifier;

const adapters = createToolAdapters({
  model: {
    config: {
      id: 'reference',
      endpoint: 'https://models.example.com/v1',
      apiKeyEnvVar: 'MODEL_API_KEY',
      defaultModel: 'example-large-1',
      defaultTimeoutMs: 30_000,
    },
    transport: modelTransport,
  },
  identity: {
    config: {
      id: 'reference',
      issuer: 'https://identity.example.com',
      audience: 'agent-platform',
      clockSkewSeconds: 30,
    },
    verifier: tokenVerifier,
    tenants: [
      {
        tenantId: 'acme',
        displayName: 'Acme Corporation',
        status: 'active',
        region: 'cn-north-1',
        plan: 'enterprise',
      },
    ],
  },
});

const principal = await adapters.identity.verifyToken(bearerToken);
const decision = adapters.identity.authorize(principal, {
  scopes: ['connectors:read'],
  mode: 'all',
});

if (!decision.allowed) {
  throw new Error(decision.reason);
}

const answer = await adapters.model.complete({
  requestId: 'req-0001',
  tenantId: principal.tenantId,
  model: 'example-large-1',
  messages: [{ role: 'user', content: 'Summarise the open support tickets.' }],
});

console.log(answer.output, adapters.model.usage);
```

## Environment variables

| Variable | Used by | Purpose |
| --- | --- | --- |
| `MODEL_API_KEY` | `ReferenceModelProvider` | Bearer credential for the model endpoint. Read by name, never logged. |
| `MODEL_ENDPOINT` | app wiring | Base URL of the model endpoint, e.g. `https://models.example.com/v1`. |
| `MODEL_DEFAULT_MODEL` | app wiring | Model used when a request does not pin one. |
| `MODEL_TIMEOUT_MS` | app wiring | Default per-call timeout in milliseconds. |
| `IDENTITY_ISSUER` | app wiring | Expected token issuer. |
| `IDENTITY_AUDIENCE` | app wiring | Expected token audience. |
| `IDENTITY_JWKS_URI` | `TokenVerifier` impls | JWKS endpoint used to verify signatures. |
| `IDENTITY_CLOCK_SKEW_SECONDS` | app wiring | Leeway applied to expiry checks. |
| `CONNECTOR_IDEMPOTENCY_TTL_MS` | app wiring | How long a completed idempotent connector call stays replayable. |

## Constraints

- Cross-package imports use the package name only; never a deep relative path
  into another package's `src/`.
- No credentials are stored in this package. Credentials are resolved from the
  environment by variable name at call time.
- Every exported symbol carries an explicit type.
