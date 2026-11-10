# AI Coding Template

**English** | [简体中文](README.zh.md)

A governed monorepo template for coding agents and enterprise agent applications.
The internal workspace name is `enterprise-agent-platform`. This repository
provides reference implementations and engineering procedures, not a complete
production service.

| System | Purpose | Main locations |
| --- | --- | --- |
| Coding-agent engineering | Help coding agents understand, change, verify and maintain the repository | `AGENTS.md`, `.agents/`, `.codex/`, `.github/`, `docs/`, `scripts/` |
| Runtime agent applications | Define business agents, applications and shared platform capabilities | `agents/`, `apps/`, `packages/`, `schemas/`, `evals/`, `infra/`, `tests/` |

`AGENTS.md` governs coding work. `agents/<name>/agent.yaml` defines a business
agent. Keep these responsibilities separate.

## Find what you need

Use progressive disclosure: overview → task index → module rules → exact files.
Read the entry point for your task, then follow its links as needed.

| Need | Start here |
| --- | --- |
| Work on this repository | [Agent instructions](AGENTS.md) |
| Select a task's documentation | [Knowledge index](docs/index.md) |
| Understand any directory or file | [Complete repository catalog](docs/repository-map.md) |
| Change module boundaries or dependencies | [Architecture](ARCHITECTURE.md) and [architecture index](docs/architecture/index.md) |
| Understand design or product intent | [Design index](docs/design-docs/index.md) and [product index](docs/product-specs/index.md) |
| Plan and track work | [Planning guide](docs/PLANS.md) |
| Investigate an incident or a security concern | [Operations](docs/operations/index.md) and [security](docs/SECURITY.md) |

The catalog gives each project directory and file a purpose. It is a lookup,
not required startup reading. Existing module READMEs and nested `AGENTS.md`
files hold local details; they remain the next step before editing a module.

## Repository areas

| Area | Owns | Detailed inventory |
| --- | --- | --- |
| `.agents/`, `.codex/`, `.github/` | Engineering skills, coding-agent configuration, reviews and CI | [Coding tools](docs/repository-map.md#coding-tools) |
| `docs/` | Architecture, product, design, plans, security and operations knowledge | [Documentation](docs/repository-map.md#documentation) |
| `agents/` | Research and support agent logic, prompts, tools and tests | [Business agents](docs/repository-map.md#business-agents) |
| `apps/` | Admin console, HTTP API and background worker | [Applications](docs/repository-map.md#applications) |
| `packages/` | Contracts, providers, policy, persistence, telemetry and evaluation helpers | [Shared packages](docs/repository-map.md#shared-packages) |
| `schemas/` | Manifest, event and tool JSON contracts | [Schemas](docs/repository-map.md#schemas) |
| `evals/` | Shared datasets, regression suites, safety cases and baselines | [Evaluation](docs/repository-map.md#evaluation) |
| `infra/` | Example Terraform compositions and authorization policies | [Infrastructure](docs/repository-map.md#infrastructure) |
| `scripts/`, `tests/`, `tooling/` | Repository checks, contract and offline system tests, local tools | [Validation and local tools](docs/repository-map.md#validation-and-local-tools) |

## Get started

Run commands from the repository root. The repository checks use Python 3.10+
and the standard library; they do not require a dependency installation.

```powershell
python scripts/check-architecture.py
python scripts/check-agent-manifests.py
python scripts/check-doc-links.py
python .agents/skills/verify-change/scripts/verify.py --root .
```

For TypeScript work, the workspace declares Node.js 22+ and pnpm 9.12.0 in
[package.json](package.json). Read the affected module's README before installing
dependencies or starting an application. Python agents are outside the pnpm
workspace and use `unittest`.

For the optional local container stack, follow the prerequisites and commands in
[local development](tooling/local-dev/README.md). Starting that stack is separate
from running the repository checks.

## Contribution rules

- Follow `Types → Config → Repo → Service → Runtime → UI`; use public package
  interfaces and explicit Providers for cross-cutting capabilities.
- Inspect applicable instructions and the affected module before editing. Write
  an execution plan for a cross-module change and keep its file scope explicit.
- Keep every project path documented in the catalog and reachable through the
  nearest index or README. Update navigation in the same change as a path change.
- Write code, commit messages and new or edited technical prose in English.
  Keep this file and [README.zh.md](README.zh.md) aligned. Existing Chinese
  reference documents remain available.
- Run the required checks and report real output. A skipped check is not a pass.
- Keep secrets and local overrides out of Git. Do not apply production
  infrastructure or perform high-risk actions without human approval.

The detailed workflow and security constraints are in [AGENTS.md](AGENTS.md).

## Template limits

- Reference providers include offline and in-memory implementations. They do not
  establish production durability or production authentication.
- Infrastructure environments, evaluation baselines, ownership handles and
  historical execution plans are examples that need project-specific review.
- [Database schema documentation](docs/generated/db-schema.md) is currently a
  template; its planned generator is not implemented. Do not hand-edit generated assets.
- The workspace declares `UNLICENSED`; no open-source license grant is included.

Choose the minimum structure that fits your risk and deployment needs. A small
team can start with instructions, documentation and engineering skills, then
adopt runtime and infrastructure areas as needed.
