/**
 * Identity provider.
 *
 * Layer: Repo. It resolves a credential into a principal. The reference
 * implementation performs no network call and no signature check, so it runs
 * offline. Read the warning below before you deploy it.
 *
 * WARNING: the default verifier accepts a token of the form
 * `<subject>.<tenant>` and trusts it. It exists so that a local environment and
 * the tests run without an identity service. A production composition root MUST
 * pass a real `verify` function that checks the signature, the issuer, the
 * audience and the expiry. Never deploy the default verifier.
 */

/** An authenticated caller. */
export interface Principal {
  readonly subject: string;
  readonly tenant: string;
  readonly scopes: readonly string[];
}

/** Verifies a credential and returns the principal it describes. */
export type CredentialVerifier = (credential: string) => Promise<Principal | null>;

/** Configuration for the reference identity provider. */
export interface IdentityProviderConfig {
  /** Expected issuer. Recorded for the audit trail. */
  readonly issuer: string;
  /** Real verifier. Required outside a local environment. */
  readonly verify?: CredentialVerifier;
  /** When true, a principal with no scopes is rejected. Defaults to false. */
  readonly requireScopes?: boolean;
}

/** Contract consumed by the Runtime layer. */
export interface IdentityProvider {
  /** Resolves the `Authorization` header. Returns null when it is not valid. */
  resolve(authorizationHeader: string | undefined): Promise<Principal | null>;
  /** The issuer this provider trusts. */
  readonly issuer: string;
}

const BEARER_PREFIX = 'Bearer ';

/**
 * The default verifier: parses `<subject>.<tenant>` and trusts it.
 *
 * It is a development stand-in, not a security control. It is exported so that
 * the risk is visible at the call site rather than hidden inside a default.
 */
export const INSECURE_DEVELOPMENT_VERIFIER: CredentialVerifier = async (credential) => {
  const parts = credential.split('.');
  if (parts.length !== 2) {
    return null;
  }
  const [subject, tenant] = parts as [string, string];
  if (subject === '' || tenant === '') {
    return null;
  }
  return { subject, tenant, scopes: [] };
};

/** Reference identity provider. */
export class ReferenceIdentityProvider implements IdentityProvider {
  readonly issuer: string;
  readonly #verify: CredentialVerifier;
  readonly #requireScopes: boolean;

  constructor(config: IdentityProviderConfig) {
    this.issuer = config.issuer;
    this.#verify = config.verify ?? INSECURE_DEVELOPMENT_VERIFIER;
    this.#requireScopes = config.requireScopes ?? false;
  }

  async resolve(authorizationHeader: string | undefined): Promise<Principal | null> {
    if (authorizationHeader === undefined || !authorizationHeader.startsWith(BEARER_PREFIX)) {
      return null;
    }
    const credential = authorizationHeader.slice(BEARER_PREFIX.length).trim();
    if (credential === '') {
      return null;
    }

    const principal = await this.#verify(credential);
    if (principal === null) {
      return null;
    }
    if (this.#requireScopes && principal.scopes.length === 0) {
      return null;
    }
    return principal;
  }
}

/** Builds the identity provider from its configuration. */
export function createIdentityProvider(config: IdentityProviderConfig): IdentityProvider {
  return new ReferenceIdentityProvider(config);
}
