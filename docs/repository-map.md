# Repository Catalog

Status: Active. Owner: platform maintainers.

This catalog explains every publishable project directory and file, including
hidden project configuration. It excludes Git internals, dependencies, caches,
build outputs, credentials and personal overrides. Known local-only paths are
explained separately at the end.

Use [the knowledge index](index.md) to choose a task route first. Search this
catalog for a path or open the relevant area; then read the module's README,
applicable AGENTS.md and exact source files. Do not preload the whole catalog.

## Areas

- [Root files](#root-files)
- [Coding tools](#coding-tools)
- [Documentation](#documentation)
- [Business agents](#business-agents)
- [Applications](#applications)
- [Shared packages](#shared-packages)
- [Schemas](#schemas)
- [Evaluation](#evaluation)
- [Infrastructure](#infrastructure)
- [Validation and local tools](#validation-and-local-tools)
- [Local-only and excluded paths](#local-only-and-excluded-paths)
- [Maintenance](#maintenance)

Paths are relative to the repository root. Directory rows explain ownership;
file rows explain intent. A linked file is not an instruction to execute it.
Reference providers, example plans and baseline records are not production
acceptance evidence.

## Root files

| Path | Kind | Purpose |
| --- | --- | --- |
| [.gitignore](../.gitignore) | File | Version-control exclusions for dependencies, outputs, credentials and local state. |
| [.mcp.json](../.mcp.json) | File | MCP server templates for filesystem, GitHub, Postgres and fetch; credentials use environment placeholders. |
| [AGENTS.md](../AGENTS.md) | File | Root coding-agent constraints, progressive-disclosure routes and completion requirements. |
| [ARCHITECTURE.md](../ARCHITECTURE.md) | File | System boundaries, layers, Provider interfaces and runtime requirements. |
| [CODEOWNERS](../CODEOWNERS) | File | Path-based review ownership; team handles are template placeholders. |
| [package.json](../package.json) | File | Workspace metadata, Node/pnpm requirements and repository-level scripts. |
| [pnpm-lock.yaml](../pnpm-lock.yaml) | File | Locked JavaScript dependency resolution for pnpm. |
| [pnpm-workspace.yaml](../pnpm-workspace.yaml) | File | Workspace membership for apps and packages; Python agents are excluded. |
| [README.md](../README.md) | File | English project overview, navigation, setup and template limits. |
| [README.zh.md](../README.zh.md) | File | Chinese translation of the overview with a direct English language switch. |

## Coding tools

| Path | Kind | Purpose |
| --- | --- | --- |
| [.agents/](../.agents/) | Directory | Reusable coding-agent maintenance procedures. |
| [.agents/skills/](../.agents/skills/) | Directory | Skill entry points; load references and scripts only for a selected procedure. |
| [.agents/skills/deploy/](../.agents/skills/deploy/) | Directory | Deployment with evidence and rollback. Start at SKILL.md. |
| [.agents/skills/deploy/checklist.md](../.agents/skills/deploy/checklist.md) | File | Deployment evidence checklist and stop conditions. |
| [.agents/skills/deploy/SKILL.md](../.agents/skills/deploy/SKILL.md) | File | Procedure for deploying a verified artifact with approval and a rollback target. |
| [.agents/skills/impact-analysis/](../.agents/skills/impact-analysis/) | Directory | Change impact analysis. Start at SKILL.md. |
| [.agents/skills/impact-analysis/references/](../.agents/skills/impact-analysis/references/) | Directory | On-demand impact-analysis policy and evidence references. |
| [.agents/skills/impact-analysis/references/dependency-policy.md](../.agents/skills/impact-analysis/references/dependency-policy.md) | File | Reference for dependency rules and contract classification. |
| [.agents/skills/impact-analysis/scripts/](../.agents/skills/impact-analysis/scripts/) | Directory | Executable impact-analysis utilities selected by the skill procedure. |
| [.agents/skills/impact-analysis/scripts/impact_analysis.py](../.agents/skills/impact-analysis/scripts/impact_analysis.py) | File | Read-only consumer and affected-contract discovery utility. |
| [.agents/skills/impact-analysis/SKILL.md](../.agents/skills/impact-analysis/SKILL.md) | File | Procedure for identifying affected modules, consumers, owners and contracts. |
| [.agents/skills/release-check/](../.agents/skills/release-check/) | Directory | Evidence-based release decisions. Start at SKILL.md. |
| [.agents/skills/release-check/references/](../.agents/skills/release-check/references/) | Directory | On-demand release-check policy and evidence references. |
| [.agents/skills/release-check/references/release-gates.md](../.agents/skills/release-check/references/release-gates.md) | File | Required release evidence, owners and gate conditions. |
| [.agents/skills/release-check/SKILL.md](../.agents/skills/release-check/SKILL.md) | File | Procedure for deciding release eligibility from recorded evidence. |
| [.agents/skills/review-architecture/](../.agents/skills/review-architecture/) | Directory | Architecture review. Start at SKILL.md. |
| [.agents/skills/review-architecture/SKILL.md](../.agents/skills/review-architecture/SKILL.md) | File | Review procedure for layers, package boundaries and Provider contracts. |
| [.agents/skills/security-review/](../.agents/skills/security-review/) | Directory | Security defect review. Start at SKILL.md. |
| [.agents/skills/security-review/SKILL.md](../.agents/skills/security-review/SKILL.md) | File | Security review procedure across six fixed defect classes. |
| [.agents/skills/sync-docs/](../.agents/skills/sync-docs/) | Directory | Documentation consistency. Start at SKILL.md. |
| [.agents/skills/sync-docs/SKILL.md](../.agents/skills/sync-docs/SKILL.md) | File | Procedure for keeping documentation and navigation consistent with changes. |
| [.agents/skills/verify-change/](../.agents/skills/verify-change/) | Directory | Change verification. Start at SKILL.md. |
| [.agents/skills/verify-change/references/](../.agents/skills/verify-change/references/) | Directory | On-demand verify-change policy and evidence references. |
| [.agents/skills/verify-change/references/quality-gates.md](../.agents/skills/verify-change/references/quality-gates.md) | File | Gate commands, applicability, owners and evidence rules. |
| [.agents/skills/verify-change/scripts/](../.agents/skills/verify-change/scripts/) | Directory | Executable verify-change utilities selected by the skill procedure. |
| [.agents/skills/verify-change/scripts/verify.py](../.agents/skills/verify-change/scripts/verify.py) | File | Run architecture, manifest and documentation gates; report pass, fail or blocked. |
| [.agents/skills/verify-change/SKILL.md](../.agents/skills/verify-change/SKILL.md) | File | Procedure for selecting and reporting repository quality checks. |
| [.codex/](../.codex/) | Directory | Codex configuration and engineering procedures. |
| [.codex/agents/](../.codex/agents/) | Directory | Coding-agent review profiles and scope contracts. |
| [.codex/agents/pr-review.md](../.codex/agents/pr-review.md) | File | Read-only PR review profile, findings format and verdict contract. |
| [.codex/agents/security-review.md](../.codex/agents/security-review.md) | File | Security review profile and scope limits. |
| [.codex/commands/](../.codex/commands/) | Directory | Reusable coding-task procedures. |
| [.codex/commands/pr-review.md](../.codex/commands/pr-review.md) | File | Reusable PR review steps and findings format. |
| [.codex/commands/resolve-bug.md](../.codex/commands/resolve-bug.md) | File | Bug reproduction, diagnosis, minimal fix and verification steps. |
| [.codex/config.toml](../.codex/config.toml) | File | Codex defaults, sandbox/approval profiles and MCP templates; configuration is not human approval. |
| [.codex/hooks/](../.codex/hooks/) | Directory | Optional local edit-time automation. |
| [.codex/hooks/post-edit-lint.sh](../.codex/hooks/post-edit-lint.sh) | File | Optional Bash hook selecting fast checks by changed file type; separate from Python gates. |
| [.codex/rules/](../.codex/rules/) | Directory | Task- and language-specific coding rules. |
| [.codex/rules/http-api.md](../.codex/rules/http-api.md) | File | HTTP API contract, validation and idempotency rules. |
| [.codex/rules/tests.md](../.codex/rules/tests.md) | File | Test scope and assertion guidance for coding agents. |
| [.codex/rules/typescript.md](../.codex/rules/typescript.md) | File | TypeScript coding conventions and public package access. |
| [.codex/settings/](../.codex/settings/) | Directory | Shared repository settings; personal overrides stay local. |
| [.codex/settings/settings.json](../.codex/settings/settings.json) | File | Shared workspace protections, agent settings and validation commands. |
| [.github/](../.github/) | Directory | GitHub reviews, Copilot guidance and automation. |
| [.github/agents/](../.github/agents/) | Directory | Specialized review and documentation agent profiles. |
| [.github/agents/architecture-reviewer.md](../.github/agents/architecture-reviewer.md) | File | GitHub agent profile for architecture and dependency review. |
| [.github/agents/code-reviewer.md](../.github/agents/code-reviewer.md) | File | GitHub agent profile for correctness and scope review. |
| [.github/agents/docs-maintainer.md](../.github/agents/docs-maintainer.md) | File | GitHub agent profile for documentation consistency and progressive-disclosure navigation. |
| [.github/agents/security-auditor.md](../.github/agents/security-auditor.md) | File | GitHub agent profile for permissions, secrets and trust-boundary auditing. |
| [.github/copilot-instructions.md](../.github/copilot-instructions.md) | File | Copilot entry point aligned with root constraints and task-specific reading. |
| [.github/instructions/](../.github/instructions/) | Directory | Path-scoped Copilot rules. |
| [.github/instructions/docs.instructions.md](../.github/instructions/docs.instructions.md) | File | Documentation rules for English prose, indexes, links and lifecycle. |
| [.github/instructions/python.instructions.md](../.github/instructions/python.instructions.md) | File | Python-scoped implementation and test conventions. |
| [.github/instructions/typescript.instructions.md](../.github/instructions/typescript.instructions.md) | File | TypeScript-scoped module, type and dependency conventions. |
| [.github/PULL_REQUEST_TEMPLATE.md](../.github/PULL_REQUEST_TEMPLATE.md) | File | PR fields for scope, risks, contracts and verification evidence. |
| [.github/workflows/](../.github/workflows/) | Directory | CI, evaluation and release-gate workflows. |
| [.github/workflows/eval.yml](../.github/workflows/eval.yml) | File | PR, scheduled and manual evaluation workflow that records reports. |
| [.github/workflows/pull-request.yml](../.github/workflows/pull-request.yml) | File | PR repository gates, TypeScript checks and Python tests. |
| [.github/workflows/release.yml](../.github/workflows/release.yml) | File | Release evidence and environment approval workflow; deployment occurs separately. |

## Documentation

| Path | Kind | Purpose |
| --- | --- | --- |
| [docs/](./) | Directory | Engineering and product knowledge; begin at docs/index.md. |
| [docs/architecture/](architecture/) | Directory | Layer rules, system-boundary navigation and decisions. |
| [docs/architecture/adr/](architecture/adr/) | Directory | Architecture decision records with alternatives and status. |
| [docs/architecture/adr/0001-record-architecture-decisions.md](architecture/adr/0001-record-architecture-decisions.md) | File | ADR format, statuses and decision-record policy. |
| [docs/architecture/adr/0002-single-repository-modular-monorepo.md](architecture/adr/0002-single-repository-modular-monorepo.md) | File | Decision and tradeoffs for a modular monorepo. |
| [docs/architecture/dependency-rules.md](architecture/dependency-rules.md) | File | Permitted imports, forbidden edges and architecture-check rule codes. |
| [docs/architecture/index.md](architecture/index.md) | File | Architecture routes, layer summary, Provider ownership and ADR links. |
| [docs/design-docs/](design-docs/) | Directory | Design intent and engineering beliefs. |
| [docs/design-docs/core-beliefs.md](design-docs/core-beliefs.md) | File | Engineering beliefs motivating architecture and progressive context loading. |
| [docs/design-docs/index.md](design-docs/index.md) | File | Design intent, beliefs and role-specific reading routes. |
| [docs/DESIGN.md](DESIGN.md) | File | Engineering design principles and review criteria. |
| [docs/exec-plans/](exec-plans/) | Directory | Task scope, progress, decisions and technical debt. |
| [docs/exec-plans/active/](exec-plans/active/) | Directory | Open task plans and the canonical metadata example. |
| [docs/exec-plans/active/AGENT-1042-improve-retrieval-timeout.md](exec-plans/active/AGENT-1042-improve-retrieval-timeout.md) | File | Illustrative active retrieval-timeout plan and canonical metadata format; not current completion evidence. |
| [docs/exec-plans/completed/](exec-plans/completed/) | Directory | Archived plans with recorded decisions and evidence. |
| [docs/exec-plans/completed/AGENT-1001-tool-gateway-rollout.md](exec-plans/completed/AGENT-1001-tool-gateway-rollout.md) | File | Illustrative historical gateway rollout plan; not acceptance evidence for this checkout. |
| [docs/exec-plans/completed/DOCS-0001-progressive-disclosure.md](exec-plans/completed/DOCS-0001-progressive-disclosure.md) | File | Completed documentation and publication plan with decisions and real verification evidence. |
| [docs/exec-plans/tech-debt-tracker.md](exec-plans/tech-debt-tracker.md) | File | Technical debt register with owners and follow-up conditions. |
| [docs/FRONTEND.md](FRONTEND.md) | File | Frontend design, accessibility, state and component conventions. |
| [docs/generated/](generated/) | Directory | Generated-asset area; current schema template has no implemented generator. |
| [docs/generated/db-schema.md](generated/db-schema.md) | File | Database schema template; its planned generator is not implemented. |
| [docs/index.md](index.md) | File | Task-based knowledge entry point routing to local indexes on demand. |
| [docs/operations/](operations/) | Directory | Operations navigation, recovery and incident learning. |
| [docs/operations/incident-reviews/](operations/incident-reviews/) | Directory | Historical incident examples and follow-ups. |
| [docs/operations/incident-reviews/2026-01-15-tool-gateway-outage.md](operations/incident-reviews/2026-01-15-tool-gateway-outage.md) | File | Example incident timeline, causes and follow-up actions. |
| [docs/operations/index.md](operations/index.md) | File | Operations entry point linking runbooks and incident reviews. |
| [docs/operations/runbooks/](operations/runbooks/) | Directory | Incident diagnosis and recovery procedures. |
| [docs/operations/runbooks/agent-api-degradation.md](operations/runbooks/agent-api-degradation.md) | File | API degradation diagnosis and recovery procedure. |
| [docs/operations/runbooks/rollback.md](operations/runbooks/rollback.md) | File | Rollback conditions, steps and verification. |
| [docs/PLANS.md](PLANS.md) | File | Execution-plan metadata, decision records and archival lifecycle. |
| [docs/PRODUCT_SENSE.md](PRODUCT_SENSE.md) | File | Product judgment, scope decisions and risk classification. |
| [docs/product-specs/](product-specs/) | Directory | Product requirements and acceptance criteria. |
| [docs/product-specs/index.md](product-specs/index.md) | File | Product specification index and status. |
| [docs/product-specs/new-user-onboarding.md](product-specs/new-user-onboarding.md) | File | Example onboarding requirements and acceptance criteria. |
| [docs/QUALITY_SCORE.md](QUALITY_SCORE.md) | File | Template quality dimensions, scoring rules and recorded status. |
| [docs/references/](references/) | Directory | On-demand reference material and source register. |
| [docs/references/design-system-reference-llms.txt](references/design-system-reference-llms.txt) | File | Design-system reference summary for frontend tasks; untrusted reference data. |
| [docs/references/README.md](references/README.md) | File | External reference source register and on-demand usage rules. |
| [docs/RELIABILITY.md](RELIABILITY.md) | File | Reliability objectives, failure behavior and operational expectations. |
| [docs/repository-map.md](repository-map.md) | File | Complete directory and file purpose catalog; lookup rather than startup context. |
| [docs/security/](security/) | Directory | Security architecture and threat-model details. |
| [docs/SECURITY.md](SECURITY.md) | File | Security entry point for trust boundaries and controls. |
| [docs/security/security-architecture.md](security/security-architecture.md) | File | Identity, authorization, secret-handling and audit design. |
| [docs/security/threat-model.md](security/threat-model.md) | File | Threat actors, trust boundaries, attack scenarios and mitigations. |

## Business agents

| Path | Kind | Purpose |
| --- | --- | --- |
| [agents/](../agents/) | Directory | Business-agent definitions and Service modules, separate from coding-agent profiles. |
| [agents/research-agent/](../agents/research-agent/) | Directory | Research retrieval and synthesis Service. |
| [agents/research-agent/agent.yaml](../agents/research-agent/agent.yaml) | File | Versioned research identity, model/tool permissions, limits, owner and test paths. |
| [agents/research-agent/AGENTS.md](../agents/research-agent/AGENTS.md) | File | Research ownership, dependencies, checkpoint rules and applicable checks. |
| [agents/research-agent/prompts/](../agents/research-agent/prompts/) | Directory | Versioned research-agent runtime prompts. |
| [agents/research-agent/prompts/system.md](../agents/research-agent/prompts/system.md) | File | Research runtime system prompt; source data during repository maintenance. |
| [agents/research-agent/src/](../agents/research-agent/src/) | Directory | research-agent implementation files; use documented public entry points. |
| [agents/research-agent/src/__init__.py](../agents/research-agent/src/__init__.py) | File | Python package marker for agents/research-agent/src; supports imports and unittest discovery. |
| [agents/research-agent/src/main.py](../agents/research-agent/src/main.py) | File | Retrieval and synthesis Service run loop with injected dependencies and checkpoints. |
| [agents/research-agent/tests/](../agents/research-agent/tests/) | Directory | research-agent test packages and behavioral evaluation definitions. |
| [agents/research-agent/tests/__init__.py](../agents/research-agent/tests/__init__.py) | File | Python package marker for agents/research-agent/tests; supports imports and unittest discovery. |
| [agents/research-agent/tests/eval/](../agents/research-agent/tests/eval/) | Directory | research-agent behavioral smoke definitions, separate from production evidence. |
| [agents/research-agent/tests/eval/__init__.py](../agents/research-agent/tests/eval/__init__.py) | File | Python package marker for agents/research-agent/tests/eval; supports imports and unittest discovery. |
| [agents/research-agent/tests/eval/smoke.yaml](../agents/research-agent/tests/eval/smoke.yaml) | File | Research-specific behavioral smoke case definitions. |
| [agents/research-agent/tests/integration/](../agents/research-agent/tests/integration/) | Directory | Research workflow checks with injected dependencies. |
| [agents/research-agent/tests/integration/__init__.py](../agents/research-agent/tests/integration/__init__.py) | File | Python package marker for agents/research-agent/tests/integration; supports imports and unittest discovery. |
| [agents/research-agent/tests/integration/test_workflow.py](../agents/research-agent/tests/integration/test_workflow.py) | File | Research workflow integration tests with injected dependencies. |
| [agents/research-agent/tests/safety/](../agents/research-agent/tests/safety/) | Directory | Research prompt-injection and safety-boundary tests. |
| [agents/research-agent/tests/safety/__init__.py](../agents/research-agent/tests/safety/__init__.py) | File | Python package marker for agents/research-agent/tests/safety; supports imports and unittest discovery. |
| [agents/research-agent/tests/safety/test_prompt_injection.py](../agents/research-agent/tests/safety/test_prompt_injection.py) | File | Tests for untrusted retrieved instructions and research safety boundaries. |
| [agents/research-agent/tests/unit/](../agents/research-agent/tests/unit/) | Directory | research-agent deterministic Service unit tests. |
| [agents/research-agent/tests/unit/__init__.py](../agents/research-agent/tests/unit/__init__.py) | File | Python package marker for agents/research-agent/tests/unit; supports imports and unittest discovery. |
| [agents/research-agent/tests/unit/test_main.py](../agents/research-agent/tests/unit/test_main.py) | File | Research run-loop unit tests, bounds, checkpoints and recovery. |
| [agents/research-agent/tools/](../agents/research-agent/tools/) | Directory | research-agent-owned tools and input validation. |
| [agents/research-agent/tools/search_tool.py](../agents/research-agent/tools/search_tool.py) | File | Validated offline search over an injected document corpus. |
| [agents/research-agent/workflows/](../agents/research-agent/workflows/) | Directory | Research orchestration descriptions beside the Service implementation. |
| [agents/research-agent/workflows/retrieval.yaml](../agents/research-agent/workflows/retrieval.yaml) | File | Descriptive retrieval graph, bounds and degradation; not executed by the runtime. |
| [agents/support-agent/](../agents/support-agent/) | Directory | Support knowledge-base answering and human-reviewed drafting Service. |
| [agents/support-agent/agent.yaml](../agents/support-agent/agent.yaml) | File | Versioned support identity, allowed tools, limits, owner and tests. |
| [agents/support-agent/AGENTS.md](../agents/support-agent/AGENTS.md) | File | Support ownership, approval rules and prohibition on sending replies. |
| [agents/support-agent/prompts/](../agents/support-agent/prompts/) | Directory | Versioned support-agent runtime prompts. |
| [agents/support-agent/prompts/system.md](../agents/support-agent/prompts/system.md) | File | Support runtime prompt for grounded answers and human-reviewed drafts. |
| [agents/support-agent/src/](../agents/support-agent/src/) | Directory | support-agent implementation files; use documented public entry points. |
| [agents/support-agent/src/__init__.py](../agents/support-agent/src/__init__.py) | File | Python package marker for agents/support-agent/src; supports imports and unittest discovery. |
| [agents/support-agent/src/main.py](../agents/support-agent/src/main.py) | File | Knowledge-base answering and reply-drafting Service with injected dependencies. |
| [agents/support-agent/tests/](../agents/support-agent/tests/) | Directory | support-agent test packages and behavioral evaluation definitions. |
| [agents/support-agent/tests/__init__.py](../agents/support-agent/tests/__init__.py) | File | Python package marker for agents/support-agent/tests; supports imports and unittest discovery. |
| [agents/support-agent/tests/eval/](../agents/support-agent/tests/eval/) | Directory | support-agent behavioral smoke definitions, separate from production evidence. |
| [agents/support-agent/tests/eval/__init__.py](../agents/support-agent/tests/eval/__init__.py) | File | Python package marker for agents/support-agent/tests/eval; supports imports and unittest discovery. |
| [agents/support-agent/tests/eval/smoke.yaml](../agents/support-agent/tests/eval/smoke.yaml) | File | Support-specific behavioral smoke case definitions. |
| [agents/support-agent/tests/unit/](../agents/support-agent/tests/unit/) | Directory | support-agent deterministic Service unit tests. |
| [agents/support-agent/tests/unit/__init__.py](../agents/support-agent/tests/unit/__init__.py) | File | Python package marker for agents/support-agent/tests/unit; supports imports and unittest discovery. |
| [agents/support-agent/tests/unit/test_main.py](../agents/support-agent/tests/unit/test_main.py) | File | Support drafting, tool-control and approval unit tests. |
| [agents/support-agent/tools/](../agents/support-agent/tools/) | Directory | support-agent-owned tools and input validation. |
| [agents/support-agent/tools/ticket_tool.py](../agents/support-agent/tools/ticket_tool.py) | File | Validated knowledge-base lookup and high-risk reply drafts; never sends replies. |

## Applications

| Path | Kind | Purpose |
| --- | --- | --- |
| [apps/](../apps/) | Directory | Application composition roots and operator UI. |
| [apps/admin-console/](../apps/admin-console/) | Directory | Operator UI for run state and human approval requests. |
| [apps/admin-console/AGENTS.md](../apps/admin-console/AGENTS.md) | File | Console UI boundaries, applicable checks and accessibility rules. |
| [apps/admin-console/package.json](../apps/admin-console/package.json) | File | admin-console package identity, dependencies, public exports where declared, and build/check scripts. |
| [apps/admin-console/README.md](../apps/admin-console/README.md) | File | Console responsibilities, Runtime interface and module setup. |
| [apps/admin-console/src/](../apps/admin-console/src/) | Directory | admin-console implementation files; use documented public entry points. |
| [apps/admin-console/src/index.tsx](../apps/admin-console/src/index.tsx) | File | Operator UI and injected Runtime interface for run and approval views. |
| [apps/admin-console/tsconfig.json](../apps/admin-console/tsconfig.json) | File | admin-console TypeScript options, source scope and build output settings. |
| [apps/agent-api/](../apps/agent-api/) | Directory | HTTP API Runtime composition root. |
| [apps/agent-api/AGENTS.md](../apps/agent-api/AGENTS.md) | File | API composition-root rules, authorization and transport contract requirements. |
| [apps/agent-api/package.json](../apps/agent-api/package.json) | File | agent-api package identity, dependencies, public exports where declared, and build/check scripts. |
| [apps/agent-api/README.md](../apps/agent-api/README.md) | File | HTTP routes, lifecycle, configuration and module commands. |
| [apps/agent-api/src/](../apps/agent-api/src/) | Directory | agent-api implementation files; use documented public entry points. |
| [apps/agent-api/src/index.ts](../apps/agent-api/src/index.ts) | File | API Runtime composition root, configuration, Provider assembly and lifecycle. |
| [apps/agent-api/src/server.ts](../apps/agent-api/src/server.ts) | File | HTTP handler types, route table, validation and transport concerns. |
| [apps/agent-api/tsconfig.json](../apps/agent-api/tsconfig.json) | File | agent-api TypeScript options, source scope and build output settings. |
| [apps/worker/](../apps/worker/) | Directory | Background execution Runtime composition root. |
| [apps/worker/AGENTS.md](../apps/worker/AGENTS.md) | File | Worker task leases, idempotency, checkpoints and approval rules. |
| [apps/worker/package.json](../apps/worker/package.json) | File | worker package identity, dependencies, public exports where declared, and build/check scripts. |
| [apps/worker/README.md](../apps/worker/README.md) | File | Worker task lifecycle, failure properties, configuration and commands. |
| [apps/worker/src/](../apps/worker/src/) | Directory | worker implementation files; use documented public entry points. |
| [apps/worker/src/index.ts](../apps/worker/src/index.ts) | File | Worker Runtime composition root, task claiming, execution and checkpoint recovery. |
| [apps/worker/tsconfig.json](../apps/worker/tsconfig.json) | File | worker TypeScript options, source scope and build output settings. |

## Shared packages

| Path | Kind | Purpose |
| --- | --- | --- |
| [packages/](../packages/) | Directory | Shared platform packages accessed through public exports. |
| [packages/agent-contracts/](../packages/agent-contracts/) | Directory | Shared Types contracts. |
| [packages/agent-contracts/package.json](../packages/agent-contracts/package.json) | File | agent-contracts package identity, dependencies, public exports where declared, and build/check scripts. |
| [packages/agent-contracts/README.md](../packages/agent-contracts/README.md) | File | Shared Types package ownership and compatibility rules. |
| [packages/agent-contracts/src/](../packages/agent-contracts/src/) | Directory | agent-contracts implementation files; use documented public entry points. |
| [packages/agent-contracts/src/index.ts](../packages/agent-contracts/src/index.ts) | File | Public exports of shared types. |
| [packages/agent-contracts/src/types.ts](../packages/agent-contracts/src/types.ts) | File | Shared TypeScript shapes for manifests, runs, tools, policy, checkpoints and approvals. |
| [packages/agent-contracts/tsconfig.json](../packages/agent-contracts/tsconfig.json) | File | agent-contracts TypeScript options, source scope and build output settings. |
| [packages/eval-kit/](../packages/eval-kit/) | Directory | Evaluation harness with injected runners. |
| [packages/eval-kit/package.json](../packages/eval-kit/package.json) | File | eval-kit package identity, dependencies, public exports where declared, and build/check scripts. |
| [packages/eval-kit/README.md](../packages/eval-kit/README.md) | File | Evaluation harness responsibilities and evidence boundaries. |
| [packages/eval-kit/src/](../packages/eval-kit/src/) | Directory | eval-kit implementation files; use documented public entry points. |
| [packages/eval-kit/src/index.ts](../packages/eval-kit/src/index.ts) | File | Injected-runner evaluation types and result aggregation; does not authorize release. |
| [packages/eval-kit/tsconfig.json](../packages/eval-kit/tsconfig.json) | File | eval-kit TypeScript options, source scope and build output settings. |
| [packages/observability/](../packages/observability/) | Directory | Telemetry interfaces and reference provider. |
| [packages/observability/package.json](../packages/observability/package.json) | File | observability package identity, dependencies, public exports where declared, and build/check scripts. |
| [packages/observability/README.md](../packages/observability/README.md) | File | Telemetry responsibilities, provider injection and redaction rules. |
| [packages/observability/src/](../packages/observability/src/) | Directory | observability implementation files; use documented public entry points. |
| [packages/observability/src/index.ts](../packages/observability/src/index.ts) | File | Public telemetry provider exports. |
| [packages/observability/src/provider.ts](../packages/observability/src/provider.ts) | File | Telemetry interfaces and reference spans, events and metrics with redaction. |
| [packages/observability/tsconfig.json](../packages/observability/tsconfig.json) | File | observability TypeScript options, source scope and build output settings. |
| [packages/policy-engine/](../packages/policy-engine/) | Directory | Policy decisions and feature flags. |
| [packages/policy-engine/package.json](../packages/policy-engine/package.json) | File | policy-engine package identity, dependencies, public exports where declared, and build/check scripts. |
| [packages/policy-engine/README.md](../packages/policy-engine/README.md) | File | Policy and feature-flag responsibilities and decision semantics. |
| [packages/policy-engine/src/](../packages/policy-engine/src/) | Directory | policy-engine implementation files; use documented public entry points. |
| [packages/policy-engine/src/engine.ts](../packages/policy-engine/src/engine.ts) | File | Tool permission evaluation and high-risk approval decisions. |
| [packages/policy-engine/src/flags.ts](../packages/policy-engine/src/flags.ts) | File | Feature-flag interface and reference implementation with explicit defaults. |
| [packages/policy-engine/src/index.ts](../packages/policy-engine/src/index.ts) | File | Public policy and feature-flag exports. |
| [packages/policy-engine/tsconfig.json](../packages/policy-engine/tsconfig.json) | File | policy-engine TypeScript options, source scope and build output settings. |
| [packages/state-store/](../packages/state-store/) | Directory | Configuration and storage API with an in-memory reference. |
| [packages/state-store/package.json](../packages/state-store/package.json) | File | state-store package identity, dependencies, public exports where declared, and build/check scripts. |
| [packages/state-store/README.md](../packages/state-store/README.md) | File | Storage API, layer separation and reference implementation limits. |
| [packages/state-store/src/](../packages/state-store/src/) | Directory | state-store implementation files; use documented public entry points. |
| [packages/state-store/src/config.ts](../packages/state-store/src/config.ts) | File | State-store configuration loading, defaults and validation. |
| [packages/state-store/src/index.ts](../packages/state-store/src/index.ts) | File | Public storage exports and factories; reference storage is in memory. |
| [packages/state-store/src/repository.ts](../packages/state-store/src/repository.ts) | File | Storage interface and in-memory runs, checkpoints, tool results and approvals. |
| [packages/state-store/tsconfig.json](../packages/state-store/tsconfig.json) | File | state-store TypeScript options, source scope and build output settings. |
| [packages/tool-adapters/](../packages/tool-adapters/) | Directory | Model, identity and connector interfaces and reference adapters. |
| [packages/tool-adapters/package.json](../packages/tool-adapters/package.json) | File | tool-adapters package identity, dependencies, public exports where declared, and build/check scripts. |
| [packages/tool-adapters/README.md](../packages/tool-adapters/README.md) | File | Model, identity and connector APIs and reference adapter limits. |
| [packages/tool-adapters/src/](../packages/tool-adapters/src/) | Directory | tool-adapters implementation files; use documented public entry points. |
| [packages/tool-adapters/src/connector.ts](../packages/tool-adapters/src/connector.ts) | File | Connector interface and reference invocation with idempotency handling. |
| [packages/tool-adapters/src/identity.ts](../packages/tool-adapters/src/identity.ts) | File | Identity interface and reference verifier; development verifier is not production authentication. |
| [packages/tool-adapters/src/index.ts](../packages/tool-adapters/src/index.ts) | File | Public Provider types, reference adapters and factories. |
| [packages/tool-adapters/src/model.ts](../packages/tool-adapters/src/model.ts) | File | Model interface and deterministic offline planning reference with injectable transport. |
| [packages/tool-adapters/tsconfig.json](../packages/tool-adapters/tsconfig.json) | File | tool-adapters TypeScript options, source scope and build output settings. |

## Schemas

| Path | Kind | Purpose |
| --- | --- | --- |
| [schemas/](../schemas/) | Directory | Cross-language JSON contracts; changes require architecture review. |
| [schemas/agent-manifest.schema.json](../schemas/agent-manifest.schema.json) | File | Cross-language agent manifest contract for ownership, tools and limits. |
| [schemas/events/](../schemas/events/) | Directory | Runtime event-envelope contracts. |
| [schemas/events/agent-event.schema.json](../schemas/events/agent-event.schema.json) | File | Versioned runtime event envelope and metadata. |
| [schemas/tool-contracts/](../schemas/tool-contracts/) | Directory | Tool inputs, outputs and risk contracts. |
| [schemas/tool-contracts/draft_reply.schema.json](../schemas/tool-contracts/draft_reply.schema.json) | File | Support reply-draft contract and high-risk semantics. |
| [schemas/tool-contracts/fetch_document.schema.json](../schemas/tool-contracts/fetch_document.schema.json) | File | Read-only research document retrieval contract. |
| [schemas/tool-contracts/kb_lookup.schema.json](../schemas/tool-contracts/kb_lookup.schema.json) | File | Read-only support knowledge-base lookup contract. |
| [schemas/tool-contracts/search.schema.json](../schemas/tool-contracts/search.schema.json) | File | Versioned search input/output and degradation contract. |

## Evaluation

| Path | Kind | Purpose |
| --- | --- | --- |
| [evals/](../evals/) | Directory | Versioned evaluation assets and example baselines. |
| [evals/baselines/](../evals/baselines/) | Directory | Example baseline versions, thresholds and evidence fields. |
| [evals/baselines/baseline-2026-01.json](../evals/baselines/baseline-2026-01.json) | File | Example baseline versions, thresholds and release fields; not fresh evaluation evidence. |
| [evals/README.md](../evals/README.md) | File | Evaluation levels, asset ownership and evidence rules. |
| [evals/regression/](../evals/regression/) | Directory | Regression suite definitions. |
| [evals/regression/smoke.yaml](../evals/regression/smoke.yaml) | File | Cross-agent regression smoke suite definition. |
| [evals/safety/](../evals/safety/) | Directory | Adversarial and safety suite definitions. |
| [evals/safety/prompt-injection.yaml](../evals/safety/prompt-injection.yaml) | File | Adversarial prompt-injection evaluation case definitions. |
| [evals/shared-datasets/](../evals/shared-datasets/) | Directory | Datasets reused across agent evaluations. |
| [evals/shared-datasets/README.md](../evals/shared-datasets/README.md) | File | Shared dataset scope, format and maintenance rules. |
| [evals/shared-datasets/retrieval-smoke.jsonl](../evals/shared-datasets/retrieval-smoke.jsonl) | File | Versioned retrieval dataset for offline smoke evaluation. |

## Infrastructure

| Path | Kind | Purpose |
| --- | --- | --- |
| [infra/](../infra/) | Directory | Infrastructure references and policies; publishing files does not apply them. |
| [infra/environments/](../infra/environments/) | Directory | Environment compositions and promotion boundaries. |
| [infra/environments/dev/](../infra/environments/dev/) | Directory | Development composition example. |
| [infra/environments/dev/main.tf](../infra/environments/dev/main.tf) | File | Development module composition example; not applied by this task. |
| [infra/environments/prod/](../infra/environments/prod/) | Directory | Protected production composition requiring approval before change or apply. |
| [infra/environments/prod/main.tf](../infra/environments/prod/main.tf) | File | Protected production composition example; applying it requires explicit human approval. |
| [infra/environments/staging/](../infra/environments/staging/) | Directory | Staging composition example. |
| [infra/environments/staging/main.tf](../infra/environments/staging/main.tf) | File | Staging module composition example in the promotion path. |
| [infra/modules/](../infra/modules/) | Directory | Reusable Terraform structural reference modules. |
| [infra/modules/agent-runtime/](../infra/modules/agent-runtime/) | Directory | Isolated per-agent resource layout and inputs. |
| [infra/modules/agent-runtime/main.tf](../infra/modules/agent-runtime/main.tf) | File | Structural per-agent runtime, queue and gateway-route resource examples. |
| [infra/modules/agent-runtime/README.md](../infra/modules/agent-runtime/README.md) | File | Per-agent isolation module responsibilities, inputs and outputs. |
| [infra/modules/agent-runtime/variables.tf](../infra/modules/agent-runtime/variables.tf) | File | Per-agent runtime input declarations and validation. |
| [infra/modules/platform/](../infra/modules/platform/) | Directory | Shared platform resource layout and inputs. |
| [infra/modules/platform/main.tf](../infra/modules/platform/main.tf) | File | Structural API, worker, queue, storage, gateway and telemetry resource examples. |
| [infra/modules/platform/README.md](../infra/modules/platform/README.md) | File | Platform resource inputs, outputs and reference-only limits. |
| [infra/modules/platform/variables.tf](../infra/modules/platform/variables.tf) | File | Platform module input declarations and validation. |
| [infra/modules/README.md](../infra/modules/README.md) | File | Reusable Terraform module ownership and composition rules. |
| [infra/policies/](../infra/policies/) | Directory | Authorization bundles and review guidance. |
| [infra/policies/agent-policy.yaml](../infra/policies/agent-policy.yaml) | File | Declarative agent/tool permission bundle. |
| [infra/policies/agent-tool-access.rego](../infra/policies/agent-tool-access.rego) | File | OPA/Rego authorization reference aligned with the policy engine. |
| [infra/policies/README.md](../infra/policies/README.md) | File | Authorization bundle ownership, review and evaluation instructions. |
| [infra/README.md](../infra/README.md) | File | Infrastructure areas, promotion workflow and approval requirements. |

## Validation and local tools

| Path | Kind | Purpose |
| --- | --- | --- |
| [scripts/](../scripts/) | Directory | Repository-level deterministic checks. |
| [scripts/check-agent-manifests.py](../scripts/check-agent-manifests.py) | File | Standard-library manifest/schema, ownership and referenced-path validation. |
| [scripts/check-architecture.py](../scripts/check-architecture.py) | File | Static checks for layers, package boundaries and Provider assembly. |
| [scripts/check-doc-links.py](../scripts/check-doc-links.py) | File | Relative Markdown target and incoming-link checks for documentation. |
| [tests/](../tests/) | Directory | Cross-module compatibility and offline system checks. |
| [tests/contracts/](../tests/contracts/) | Directory | Manifest and public-contract compatibility assertions. |
| [tests/contracts/README.md](../tests/contracts/README.md) | File | Public-interface compatibility test scope and commands. |
| [tests/contracts/test_agent_manifest_contract.py](../tests/contracts/test_agent_manifest_contract.py) | File | Contract assertions against real manifests and their schema. |
| [tests/end-to-end/](../tests/end-to-end/) | Directory | Offline system and workflow smoke tests; not deployed acceptance. |
| [tests/end-to-end/test_platform_smoke.py](../tests/end-to-end/test_platform_smoke.py) | File | Offline repository consistency and security-baseline smoke assertions. |
| [tests/end-to-end/test_research_agent_e2e.py](../tests/end-to-end/test_research_agent_e2e.py) | File | Offline research run-loop tests with stub model, memory store and telemetry. |
| [tooling/](../tooling/) | Directory | Local development support and task wrappers. |
| [tooling/local-dev/](../tooling/local-dev/) | Directory | Disposable container services and development instructions. |
| [tooling/local-dev/docker-compose.yml](../tooling/local-dev/docker-compose.yml) | File | Disposable local service stack; not production infrastructure. |
| [tooling/local-dev/otel-collector.yaml](../tooling/local-dev/otel-collector.yaml) | File | Local OpenTelemetry receiver and debug export configuration. |
| [tooling/local-dev/README.md](../tooling/local-dev/README.md) | File | Local container prerequisites, startup and offline-agent development instructions. |
| [tooling/task-runner/](../tooling/task-runner/) | Directory | go-task wrappers and planned-tooling records. |
| [tooling/task-runner/README.md](../tooling/task-runner/README.md) | File | Task wrapper usage and planned generators. |
| [tooling/task-runner/Taskfile.yml](../tooling/task-runner/Taskfile.yml) | File | go-task wrappers for repository checks and development commands. |

## Local-only and excluded paths

These entries describe local state; they are not published or linked as remote
files. Do not read their contents to complete a documentation task.

| Path or pattern | Purpose | Handling |
| --- | --- | --- |
| `.git/` | Git objects, refs, index and local repository configuration | Git internals; not a project file |
| `.claude/` | Optional personal Claude workspace settings | Its current local override is ignored; no directory is published |
| `.claude/settings.local.json` | Personal tool permissions and machine-specific settings | Keep local; excluded by .gitignore |
| `.codex/settings/settings.local.json` | Personal Codex workspace overrides | Keep local; excluded by .gitignore |
| `.env`, `.env.*`, `*.pem`, `*.key`, `secrets/` | Runtime secrets and private material | Never commit; only a sanitized `.env.example` may be shared |
| `node_modules/`, `.venv/`, `venv/` | Installed dependencies | Recreate locally; ignored |
| `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | Python interpreter and tool caches | Recreate locally; ignored |
| `dist/`, `build/`, `coverage/`, `*.tsbuildinfo` | Compilation outputs and reports | Generated locally; ignored |
| `.npm/`, `.pnpm-store/` | Package-manager caches | Machine-local; ignored |
| `.terraform/`, `*.tfstate*`, `*.tfvars` | Terraform working state and environment values | Keep state/private values out of Git; sanitized tfvars examples may be shared |
| `.agent-state/`, `logs/`, `tmp/`, `scratch/` | Runtime state, logs and scratch work | Keep local; ignored |
| `.idea/`, `.vscode/`, OS metadata | Editor and machine state | Ignore local state; explicitly allowed shared VS Code files may be added intentionally |

## Maintenance

1. Add, rename, move or remove a path and its purpose row in the same change.
   Document every ancestor directory, including hidden project directories.
2. Keep the nearest index or README current. Put a detailed rule at one source
   and link to it from summaries. New areas start from [docs/index.md](index.md).
3. Review the candidate file list using `git ls-files --cached --others --exclude-standard`.
   Exclude Git internals, credentials and machine-local state. After a plan is
   archived, update its catalog row and index link to the completed location.
4. Run `python scripts/check-doc-links.py` and the
   [verification procedure](../.agents/skills/verify-change/SKILL.md).
   Link checking checks existence and incoming links; it does not prove a
   purpose description, Markdown anchor or production claim is correct.
5. Compare catalog rows with the candidate file list and its ancestor directories
   during review. There is no permanent catalog-coverage checker yet; do not
   claim automatic coverage enforcement.
