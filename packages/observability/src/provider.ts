/**
 * Telemetry provider: spans, run events and metrics.
 *
 * Layer: Service. The provider is injected at the composition root. It redacts
 * payload fields before export and never raises into a caller: telemetry must
 * not fail a run.
 */

/** One span. A span is ended exactly once, in a `finally` block. */
export interface Span {
  readonly name: string;
  readonly traceId: string;
  setAttribute(key: string, value: unknown): void;
  recordError(error: Error): void;
  end(): void;
}

/** One telemetry event. */
export interface RunEvent {
  readonly name: string;
  readonly traceId: string;
  readonly runId: string;
  readonly fields: Readonly<Record<string, unknown>>;
}

/** Sink contract. The runtime injects a real exporter. */
export interface TelemetrySink {
  write(record: Readonly<Record<string, unknown>>): void;
}

/** Provider contract consumed by every layer. */
export interface TelemetryProvider {
  startSpan(name: string, attributes?: Readonly<Record<string, unknown>>): Span;
  emit(event: RunEvent): void;
  metric(name: string, value: number, labels?: Readonly<Record<string, string>>): void;
  /** Returns the names of the fields this provider redacts. */
  redactedFields(): readonly string[];
}

/**
 * Fields whose value is replaced before export. A prompt, a tool result and a
 * retrieved document can all hold personal data or a secret.
 */
export const DEFAULT_REDACTED_FIELDS: readonly string[] = [
  'prompt',
  'content',
  'document',
  'arguments',
  'output',
  'authorization',
  'token',
  'secret',
];

/** Configuration for the reference provider. */
export interface TelemetryConfig {
  readonly serviceName: string;
  /** Collector endpoint. The reference provider records it; it does not post. */
  readonly endpoint: string;
  readonly redactedFields?: readonly string[];
  /** Defaults to a sink that drops every record. */
  readonly sink?: TelemetrySink;
}

/** A sink that drops every record. Used when no exporter is configured. */
export const NULL_SINK: TelemetrySink = {
  write: (): void => {
    // Intentionally empty: a run must not fail because telemetry is unavailable.
  },
};

let traceCounter = 0;

/** Builds a trace identifier. Unique in shape and in practice. */
function nextTraceId(): string {
  traceCounter += 1;
  return `trace-${Date.now().toString(36)}-${traceCounter.toString(36)}`;
}

/** Reference provider: redacts, then writes to the sink. */
export class ReferenceTelemetryProvider implements TelemetryProvider {
  readonly #serviceName: string;
  readonly #endpoint: string;
  readonly #redacted: readonly string[];
  readonly #sink: TelemetrySink;

  constructor(config: TelemetryConfig) {
    this.#serviceName = config.serviceName;
    this.#endpoint = config.endpoint;
    this.#redacted = config.redactedFields ?? DEFAULT_REDACTED_FIELDS;
    this.#sink = config.sink ?? NULL_SINK;
  }

  get serviceName(): string {
    return this.#serviceName;
  }

  get endpoint(): string {
    return this.#endpoint;
  }

  redactedFields(): readonly string[] {
    return this.#redacted;
  }

  startSpan(name: string, attributes?: Readonly<Record<string, unknown>>): Span {
    const traceId = nextTraceId();
    const startedAt = Date.now();
    let ended = false;

    const write = (record: Readonly<Record<string, unknown>>): void => {
      try {
        this.#sink.write({
          time: new Date().toISOString(),
          service: this.#serviceName,
          trace_id: traceId,
          ...record,
        });
      } catch {
        // A telemetry failure must never fail a run. The record is dropped.
      }
    };

    write({ span: name, phase: 'start', ...this.#redact(attributes ?? {}) });

    return {
      name,
      traceId,
      setAttribute: (key, value) => {
        write({ span: name, attribute: key, value: this.#redact({ [key]: value })[key] });
      },
      recordError: (error) => {
        write({ span: name, error: error.message, error_name: error.name });
      },
      end: () => {
        if (ended) {
          return;
        }
        ended = true;
        write({ span: name, phase: 'end', duration_ms: Date.now() - startedAt });
      },
    };
  }

  emit(event: RunEvent): void {
    try {
      this.#sink.write({
        time: new Date().toISOString(),
        service: this.#serviceName,
        event: event.name,
        trace_id: event.traceId,
        run_id: event.runId,
        ...this.#redact(event.fields),
      });
    } catch {
      // Dropped, as above.
    }
  }

  metric(name: string, value: number, labels?: Readonly<Record<string, string>>): void {
    try {
      this.#sink.write({
        time: new Date().toISOString(),
        service: this.#serviceName,
        metric: name,
        value,
        labels: labels ?? {},
      });
    } catch {
      // Dropped, as above.
    }
  }

  #redact(fields: Readonly<Record<string, unknown>>): Record<string, unknown> {
    const output: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(fields)) {
      output[key] = this.#redacted.includes(key) ? '[redacted]' : value;
    }
    return output;
  }
}

/** Builds the reference telemetry provider from its configuration. */
export function createTelemetryProvider(config: TelemetryConfig): TelemetryProvider {
  return new ReferenceTelemetryProvider(config);
}
