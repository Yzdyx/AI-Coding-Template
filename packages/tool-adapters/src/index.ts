/**
 * Public surface of @agent-platform/tool-adapters.
 *
 * Consumers import provider interfaces and the factories from this entry point.
 * Cross-package imports must use the package name, never a deep relative path
 * into `src/`; `scripts/check-architecture.py` enforces that rule.
 *
 * This entry point is the one place outside the application composition roots
 * where a `Reference*` implementation is constructed. The composition root calls
 * these factories; business code never calls a constructor.
 */

export type {
  ConnectorInvocation,
  ConnectorProvider,
  ConnectorProviderConfig,
  ToolHandler,
} from './connector.js';
export { ReferenceConnectorProvider, createConnectorProvider } from './connector.js';

export type { CredentialVerifier, IdentityProvider, IdentityProviderConfig, Principal } from './identity.js';
export {
  INSECURE_DEVELOPMENT_VERIFIER,
  ReferenceIdentityProvider,
  createIdentityProvider,
} from './identity.js';

export type {
  ModelCompletion,
  ModelProvider,
  ModelProviderConfig,
  ModelRequest,
  ModelTransport,
} from './model.js';
export { ReferenceModelProvider, createModelProvider, planWithoutModel } from './model.js';
