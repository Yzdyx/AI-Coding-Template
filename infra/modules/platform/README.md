# Module: platform

Provisions the agent runtime platform for one environment: compute, task queue,
durable state, the tool gateway and the telemetry sink.

## Inputs

See [`variables.tf`](variables.tf). Required inputs: `project`, `environment`,
`owner`, `agent_api_image`, `worker_image`.

## Outputs

| Output | Meaning |
| --- | --- |
| `agent_api_name` | Service name of agent-api |
| `worker_name` | Service name of worker |
| `queue_name` | Task queue name |
| `state_store_name` | State store name |
| `gateway_name` | Tool gateway name |
| `telemetry_sink_name` | Telemetry sink name |

## Security properties

1. The tool gateway sets `require_authorization` and `fail_closed`. A gateway that cannot reach the policy engine denies the call.
2. The telemetry sink redacts payloads. Prompt and tool content is not exported raw.
3. Secrets arrive as references through `secret_refs`. The module never holds a secret value.

## Usage

```hcl
module "platform" {
  source = "../../modules/platform"

  project          = "agent-platform"
  environment      = "dev"
  owner            = "sre-team"
  agent_api_image  = var.agent_api_image
  worker_image     = var.worker_image
}
```
