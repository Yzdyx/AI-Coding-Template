# @agent-platform/observability

Tracing, metrics and structured logging. Layer: `Service`.

## Rules

1. **Redact before export.** Prompt text, model output and retrieved content are sensitive. They are redacted, never exported raw.
2. A run event always carries `trace_id` and `run_id`. An event without them is not diagnosable.
3. Never log a credential, a token, an authorization header or a full request body.
4. Telemetry must not fail a run. A sink failure is recorded and dropped, not raised into the caller.
5. The provider is injected at the composition root. No layer constructs it.

## Contents

| Symbol | Role |
| --- | --- |
| `TelemetryProvider` | Interface consumed by every layer |
| `RunEvent` | Event shape: name, trace id, run id, fields |
| `ReferenceTelemetryProvider` | Reference implementation with redaction |

## Related

- [`../../docs/operations/index.md`](../../docs/operations/index.md)
- [`../../docs/security/security-architecture.md`](../../docs/security/security-architecture.md)
