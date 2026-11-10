# Module: agent-runtime

Provisions the runtime of one business agent: its service, its task queue and its
gateway route. Called once per agent, so two agents never share a queue or a
lease.

## Inputs

See [`variables.tf`](variables.tf). Required: `project`, `environment`, `owner`,
`agent_name`, `image`, `state_store_name`, `gateway_name`, `telemetry_sink_name`.

## Outputs

| Output | Meaning |
| --- | --- |
| `agent_name` | The agent this runtime serves |
| `queue_name` | This agent's task queue |
| `route_name` | This agent's gateway route |

## Why one queue per agent

A shared queue lets one slow agent starve another, and it breaks the lease
accounting of the worker: two workers could claim the same task. One queue per
agent keeps the failure domain inside one agent.

## Consistency rule

`max_steps` and `timeout_seconds` here must equal `limits.max_steps` and
`limits.timeout_seconds` in `agents/<agent_name>/agent.yaml`. `allowed_tools`
must equal the `tools` list of the same manifest. A mismatch means the platform
stops a run at a different point than the agent expects.

## Usage

```hcl
module "agent_runtime" {
  source   = "../../modules/agent-runtime"
  for_each = toset(var.agent_names)

  project            = "agent-platform"
  environment        = "staging"
  owner              = "sre-team"
  agent_name         = each.value
  image              = var.agent_image
  state_store_name   = module.platform.state_store_name
  gateway_name       = module.platform.gateway_name
  telemetry_sink_name = module.platform.telemetry_sink_name
  approval_required  = true
}
```
