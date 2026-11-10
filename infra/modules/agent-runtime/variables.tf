# Inputs for the per-agent runtime module. Every input is typed and described.
# A missing required input is an error. The module never invents a value.

variable "project" {
  description = "Project slug used as a name prefix."
  type        = string
}

variable "environment" {
  description = "Environment name: dev, staging or prod."
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment must be one of dev, staging, prod."
  }
}

variable "owner" {
  description = "Owning team handle. Must appear in CODEOWNERS."
  type        = string
}

variable "agent_name" {
  description = "Agent identifier. Must equal the directory name under agents/."
  type        = string
}

variable "image" {
  description = "Container image digest for this agent. Use a digest, never a floating tag."
  type        = string
}

variable "replicas" {
  description = "Replica count for this agent runtime."
  type        = number
  default     = 1
}

variable "max_steps" {
  description = "Hard step limit for one run. Must match limits.max_steps in agent.yaml."
  type        = number
  default     = 24
}

variable "timeout_seconds" {
  description = "Hard wall-clock limit for one run. Must match limits.timeout_seconds in agent.yaml."
  type        = number
  default     = 600
}

variable "approval_required" {
  description = "When true, a high-risk tool call stops for human approval. Production keeps this true."
  type        = bool
  default     = true
}

variable "allowed_tools" {
  description = "Tool names the gateway accepts for this agent. Must match the tools list in agent.yaml."
  type        = list(string)
  default     = []
}

variable "policy_bundle" {
  description = "Authorization policy bundle name consumed by the gateway route."
  type        = string
  default     = "default"
}

variable "state_store_name" {
  description = "State store this agent writes its checkpoints to."
  type        = string
}

variable "gateway_name" {
  description = "Tool gateway this agent calls through."
  type        = string
}

variable "telemetry_sink_name" {
  description = "Telemetry sink for this agent's spans and run events."
  type        = string
}

variable "queue_visibility_timeout_seconds" {
  description = "Queue visibility timeout. Must exceed the longest expected step."
  type        = number
  default     = 900
}

variable "secret_refs" {
  description = "References to secrets. Pass references, never secret values."
  type        = map(string)
  default     = {}
}
