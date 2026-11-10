# Development environment. Lowest cost, no production data.
# Promotion order is dev -> staging -> prod.

terraform {
  required_version = ">= 1.6.0"

  backend "local" {}
}

variable "agent_api_image" {
  description = "Container image digest for agent-api."
  type        = string
  default     = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
}

variable "worker_image" {
  description = "Container image digest for worker."
  type        = string
  default     = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
}

variable "agents" {
  description = "Agents provisioned in this environment, with the tools each one may call."
  type = map(object({
    allowed_tools = list(string)
    replicas      = optional(number, 1)
  }))
  default = {
    research-agent = { allowed_tools = ["search", "fetch_document"] }
    support-agent  = { allowed_tools = ["kb_lookup", "draft_reply"] }
  }
}

variable "agent_image" {
  description = "Container image digest for the business agents."
  type        = string
  default     = "sha256:0000000000000000000000000000000000000000000000000000000000000000"
}

module "platform" {
  source = "../../modules/platform"

  project         = "agent-platform"
  environment     = "dev"
  owner           = "sre-team"
  agent_api_image = var.agent_api_image
  worker_image    = var.worker_image

  agent_api_replicas                = 1
  worker_replicas                   = 1
  state_store_backup_retention_days = 3
  telemetry_retention_days          = 7
  policy_bundle                     = "default"
}

module "agent_runtime" {
  source   = "../../modules/agent-runtime"
  for_each = var.agents

  project             = "agent-platform"
  environment         = "dev"
  owner               = "sre-team"
  agent_name          = each.key
  image               = var.agent_image
  replicas            = each.value.replicas
  approval_required   = false
  allowed_tools       = each.value.allowed_tools
  state_store_name    = module.platform.state_store_name
  gateway_name        = module.platform.gateway_name
  telemetry_sink_name = module.platform.telemetry_sink_name
  policy_bundle       = "default"
}

output "agent_api_name" {
  value = module.platform.agent_api_name
}

output "queue_name" {
  value = module.platform.queue_name
}
