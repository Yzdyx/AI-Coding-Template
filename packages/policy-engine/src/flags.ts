/**
 * Feature flags.
 *
 * Layer: Service. Flags are injected at the composition root. A `Service` or an
 * agent receives this interface, never a concrete implementation.
 */

/** Flag values are booleans. A flag with no value falls back to its default. */
export interface FeatureFlagProvider {
  /** Returns the flag value, or the supplied default when the flag is unknown. */
  isEnabled(flag: string, fallback: boolean): boolean;
  /** Returns every flag and its resolved value. Used by the operator console. */
  snapshot(): Readonly<Record<string, boolean>>;
}

/** Configuration for the reference flag provider. */
export interface FeatureFlagConfig {
  readonly values: Readonly<Record<string, boolean>>;
  readonly source: string;
}

/**
 * Reference implementation backed by a static map.
 *
 * A flag that is absent resolves to the caller's fallback. A flag is never
 * invented, and an unreadable source is not treated as `true`.
 */
export class ReferenceFeatureFlagProvider implements FeatureFlagProvider {
  readonly #values: Readonly<Record<string, boolean>>;
  readonly #source: string;

  constructor(config: FeatureFlagConfig) {
    this.#values = Object.freeze({ ...config.values });
    this.#source = config.source;
  }

  get source(): string {
    return this.#source;
  }

  isEnabled(flag: string, fallback: boolean): boolean {
    const value = this.#values[flag];
    return value === undefined ? fallback : value;
  }

  snapshot(): Readonly<Record<string, boolean>> {
    return this.#values;
  }
}
