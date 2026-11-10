# Modules

Reusable Terraform modules. A module takes variables and returns outputs. It
never contains an environment-specific value.

## Index

| Module | Purpose | Owner |
| --- | --- | --- |
| [`platform/`](platform/) | Agent runtime platform: compute, queue, state store, tool gateway | `@sre-team` |
| [`agent-runtime/`](agent-runtime/) | One agent's own service, queue and gateway route | `@sre-team` |

## Rules

1. A module is versioned by the environment that consumes it. Bump the reference, then apply.
2. A module declares every input in `variables.tf`, with a description and a type.
3. A module fails closed: a missing required input is an error, not a default.
4. No secret value in a module. Pass a secret reference, not a secret.
5. A module change is reviewed by `@sre-team` and applies to `dev` first.
