# Platform module: agent runtime compute, queue, state store and tool gateway.
#
# This is a structural reference, not a deployable production configuration.
# Replace the placeholder providers and resource types with the ones your cloud
# account uses. The shape stays the same: inputs from variables.tf, outputs for
# the environment composition, no secret value in the module.

terraform {
  required_version = ">= 1.6.0"
}

locals {
  name_prefix = "${var.project}-${var.environment}"
  common_tags = {
    project     = var.project
    environment = var.environment
    owner       = var.owner
    managed_by  = "terraform"
  }
}

# Agent runtime compute. One deployment per layer role.
resource "platform_service" "agent_api" {
  name          = "${local.name_prefix}-agent-api"
  image         = var.agent_api_image
  replicas      = var.agent_api_replicas
  port          = var.agent_api_port
  cpu           = var.agent_api_cpu
  memory        = var.agent_api_memory
  secret_refs   = var.secret_refs
  tags          = local.common_tags
}

resource "platform_service" "worker" {
  name        = "${local.name_prefix}-worker"
  image       = var.worker_image
  replicas    = var.worker_replicas
  cpu         = var.worker_cpu
  memory      = var.worker_memory
  secret_refs = var.secret_refs
  tags        = local.common_tags
}

# Task queue. The visibility timeout must exceed the longest expected step.
resource "platform_queue" "tasks" {
  name                = "${local.name_prefix}-tasks"
  visibility_timeout  = var.queue_visibility_timeout_seconds
  dead_letter_enabled = true
  tags                = local.common_tags
}

# Durable state for checkpoints and audit records.
resource "platform_state_store" "main" {
  name                    = "${local.name_prefix}-state"
  engine                  = var.state_store_engine
  backup_retention_days   = var.state_store_backup_retention_days
  point_in_time_recovery  = var.environment == "prod"
  tags                    = local.common_tags
}

# Tool gateway: the only path from an agent to an external tool.
resource "platform_gateway" "tools" {
  name                    = "${local.name_prefix}-tool-gateway"
  policy_bundle           = var.policy_bundle
  require_authorization   = true
  fail_closed             = true
  tags                    = local.common_tags
}

# Telemetry sink. Prompt and tool payloads are redacted before export.
resource "platform_telemetry_sink" "main" {
  name                  = "${local.name_prefix}-telemetry"
  redact_payloads       = true
  retention_days        = var.telemetry_retention_days
  tags                  = local.common_tags
}

# Outputs. The environment compositions consume these, and the per-agent module
# needs the state store, the gateway and the telemetry sink by name.
output "agent_api_name" {
  description = "Service name of agent-api."
  value       = platform_service.agent_api.name
}

output "worker_name" {
  description = "Service name of worker."
  value       = platform_service.worker.name
}

output "queue_name" {
  description = "Name of the shared task queue."
  value       = platform_queue.tasks.name
}

output "state_store_name" {
  description = "Name of the durable state store."
  value       = platform_state_store.main.name
}

output "gateway_name" {
  description = "Name of the tool gateway."
  value       = platform_gateway.tools.name
}

output "telemetry_sink_name" {
  description = "Name of the telemetry sink."
  value       = platform_telemetry_sink.main.name
}
