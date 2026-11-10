/**
 * Evaluation harness.
 *
 * Layer: Service. The runner is injected, so this package performs no I/O and
 * holds no model client. It decides nothing about a release: it produces
 * evidence that a release gate reads.
 */

/** Outcome of one case. `blocked` is not `passed`. */
export type EvalOutcome = 'passed' | 'failed' | 'blocked';

/** One evaluation case. */
export interface EvalCase {
  readonly id: string;
  readonly input: string;
  readonly expect: {
    readonly status?: string;
    readonly tools?: readonly string[];
    readonly degradedAllowed?: boolean;
    readonly refused?: boolean;
  };
}

/** What the agent produced for one case. */
export interface EvalObservation {
  readonly status: string;
  readonly toolsCalled: readonly string[];
  readonly degraded: boolean;
  readonly refused: boolean;
}

/** Result of one case. */
export interface EvalResult {
  readonly id: string;
  readonly outcome: EvalOutcome;
  readonly reason: string;
  readonly expected?: unknown;
  readonly actual?: unknown;
}

/** Runs one case. Implemented by the caller, injected here. */
export interface EvalRunner {
  run(testCase: EvalCase): Promise<EvalObservation>;
}

/** Summary of a suite. */
export interface EvalSummary {
  readonly total: number;
  readonly passed: number;
  readonly failed: number;
  readonly blocked: number;
  readonly results: readonly EvalResult[];
}

/** Compares one observation against the expectation of a case. */
export function compare(testCase: EvalCase, observation: EvalObservation): EvalResult {
  const expected = testCase.expect;

  if (expected.status !== undefined && observation.status !== expected.status) {
    return {
      id: testCase.id,
      outcome: 'failed',
      reason: `status mismatch: expected ${expected.status}, actual ${observation.status}`,
      expected: expected.status,
      actual: observation.status,
    };
  }

  if (expected.refused === true && !observation.refused) {
    return {
      id: testCase.id,
      outcome: 'failed',
      reason: 'a refusal was required and none was produced',
      expected: true,
      actual: false,
    };
  }

  if (expected.tools !== undefined) {
    const missing = expected.tools.filter((tool) => !observation.toolsCalled.includes(tool));
    if (missing.length > 0) {
      return {
        id: testCase.id,
        outcome: 'failed',
        reason: `required tools were not called: ${missing.join(', ')}`,
        expected: expected.tools,
        actual: observation.toolsCalled,
      };
    }
    const unexpected = observation.toolsCalled.filter((tool) => !expected.tools?.includes(tool));
    if (unexpected.length > 0) {
      return {
        id: testCase.id,
        outcome: 'failed',
        reason: `unexpected tools were called: ${unexpected.join(', ')}`,
        expected: expected.tools,
        actual: observation.toolsCalled,
      };
    }
  }

  if (expected.degradedAllowed === false && observation.degraded) {
    return {
      id: testCase.id,
      outcome: 'failed',
      reason: 'a degraded result was produced where a complete result was required',
      expected: false,
      actual: true,
    };
  }

  return { id: testCase.id, outcome: 'passed', reason: 'expectation satisfied' };
}

/**
 * Runs every case and returns a summary.
 *
 * A runner that throws marks the case `blocked`, with the error text as the
 * reason. A blocked case is never counted as passed.
 */
export async function runSuite(
  cases: readonly EvalCase[],
  runner: EvalRunner,
): Promise<EvalSummary> {
  const results: EvalResult[] = [];

  for (const testCase of cases) {
    try {
      const observation = await runner.run(testCase);
      results.push(compare(testCase, observation));
    } catch (error) {
      results.push({
        id: testCase.id,
        outcome: 'blocked',
        reason: error instanceof Error ? error.message : String(error),
      });
    }
  }

  return {
    total: results.length,
    passed: results.filter((result) => result.outcome === 'passed').length,
    failed: results.filter((result) => result.outcome === 'failed').length,
    blocked: results.filter((result) => result.outcome === 'blocked').length,
    results,
  };
}
