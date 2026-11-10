/**
 * Public surface of @agent-platform/state-store.
 */

export type { StateStoreConfig, StateStoreConfigInput } from './config.js';
export { ConfigurationError, loadStateStoreConfig } from './config.js';

export type { ApprovalDecisionInput, SaveToolResultInput, StateStore } from './repository.js';
export { InMemoryStateStore } from './repository.js';

import { loadStateStoreConfig } from './config.js';
import type { StateStoreConfig, StateStoreConfigInput } from './config.js';
import { InMemoryStateStore } from './repository.js';
import type { StateStore } from './repository.js';

/**
 * Builds the store the Runtime uses.
 *
 * The reference build is in memory, so a local environment runs without a
 * database. A production build returns a SQL implementation of the same
 * interface; the composition root does not change.
 */
export function createStateStore(config: StateStoreConfig): StateStore {
  return new InMemoryStateStore(config);
}

/** Builds a store from partial input, filling the defaults. */
export function createStateStoreFromInput(input: StateStoreConfigInput): StateStore {
  return createStateStore(loadStateStoreConfig(input));
}
