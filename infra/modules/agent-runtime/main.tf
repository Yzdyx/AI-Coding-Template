# Per-agent runtime module.
#
# Provisions the runtime of exactly one business agent: its own service, its own
# task queue, its own state namespace and its own gateway route. Isolation is the
# point: one agent cannot consume another agent's queue, lease or checkpoint.
#
# This is a structural reference. Replace the `platform_*` resource types with
# the ones your cloud account uses. The shape stays the same: inputs from
# variables.tf, outputs for the environment composition, no secret value here.

terraform {
  required_version = ">= 1.6.0"
}

locals {
  name_prefix = "${var.project}-${var.environment}-${var.agent_name}"
  common_tags = {
    project     = var.project
    environment = var.environment
    agent       = var.agent_name
    owner       = var.owner
    managed_by  = "terraform"
  }
}

# The agent runtime. The manifest limits become the process limits, so a runaway
# agent is stopped by the platform and not only by its own loop.
resource "platform_agent_runtime" "this" {
  name              = local.name_prefix
  image             = var.image
  replicas          = var.replicas
  max_steps         = var.max_steps
  timeout_seconds   = var.timeout_seconds
  state_store       = var.state_store_name
  gateway           = var.gateway_name
  telemetry_sink    = var.telemetry_sink_name
  approval_required = var.approval_required
  secret_refs       = var.secret_refs
  tags              = local.common_tags
}

# One queue per agent. A shared queue would let a slow agent starve a fast one,
# and it would break the lease accounting of the worker.
resource "platform_queue" "agent" {
  name                = "${local.name_prefix}-tasks"
  visibility_timeout  = var.queue_visibility_timeout_seconds
  dead_letter_enabled = true
  tags                = local.common_tags
}

# The gateway route for this agent. The policy bundle decides which tool the
# agent may call; the route only decides where the call goes.
resource "platform_gateway_route" "agent" {
  name          = "${local.name_prefix}-route"
  gateway       = var.gateway_name
  policy_bundle = var.policy_bundle
  allowed_tools = var.allowed_tools
  fail_closed   = true
  tags          = local.common_tags
}
