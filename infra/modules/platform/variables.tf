# Inputs for the platform module. Every input is typed and described.
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

variable "agent_api_image" {
  description = "Container image digest for agent-api. Use a digest, never a floating tag."
  type        = string
}

variable "worker_image" {
  description = "Container image digest for worker. Use a digest, never a floating tag."
  type        = string
}

variable "agent_api_replicas" {
  description = "Replica count for agent-api."
  type        = number
  default     = 2
}

variable "worker_replicas" {
  description = "Replica count for worker."
  type        = number
  default     = 1
}

variable "agent_api_port" {
  description = "TCP port agent-api listens on."
  type        = number
  default     = 8080
}

variable "agent_api_cpu" {
  description = "CPU request for one agent-api replica."
  type        = string
  default     = "500m"
}

variable "agent_api_memory" {
  description = "Memory request for one agent-api replica."
  type        = string
  default     = "512Mi"
}

variable "worker_cpu" {
  description = "CPU request for one worker replica."
  type        = string
  default     = "1000m"
}

variable "worker_memory" {
  description = "Memory request for one worker replica."
  type        = string
  default     = "1Gi"
}

variable "queue_visibility_timeout_seconds" {
  description = "Queue visibility timeout. Must exceed the longest expected agent step."
  type        = number
  default     = 900
}

variable "state_store_engine" {
  description = "State store engine identifier."
  type        = string
  default     = "postgres"
}

variable "state_store_backup_retention_days" {
  description = "Backup retention for the state store, in days."
  type        = number
  default     = 14
}

variable "policy_bundle" {
  description = "Authorization policy bundle name consumed by the tool gateway."
  type        = string
  default     = "default"
}

variable "telemetry_retention_days" {
  description = "Telemetry retention, in days. Keep it aligned with the data policy."
  type        = number
  default     = 30
}

variable "secret_refs" {
  description = "References to secrets. Pass references, never secret values."
  type        = map(string)
  default     = {}
}
