# DOCS-0001: Document the repository with progressive disclosure

## Task metadata

```yaml
task_id: DOCS-0001
title: Document the repository with progressive disclosure
owner_team: platform
status: completed
scope:
  paths:
    - AGENTS.md
    - README.md
    - README.zh.md
    - .gitignore
    - .github/copilot-instructions.md
    - .github/agents/docs-maintainer.md
    - .github/instructions/docs.instructions.md
    - docs/index.md
    - docs/repository-map.md
    - docs/exec-plans/active/DOCS-0001-progressive-disclosure.md
    - docs/exec-plans/completed/DOCS-0001-progressive-disclosure.md
  related_contracts: []
acceptance:
  - Every publishable project directory and file has a purpose entry and a working link.
  - Root instructions route readers to task-specific indexes before detailed files.
  - English and Chinese READMEs link to each other and describe the same scope.
  - Local-only settings are excluded from the initial publication.
  - Required repository checks pass with recorded output.
  - The verified project replaces the remote README on the existing main branch.
risk:
  level: low
  production_write: false
validation:
  - python scripts/check-architecture.py
  - python scripts/check-agent-manifests.py
  - python scripts/check-doc-links.py
  - python .agents/skills/verify-change/scripts/verify.py --root . --json
  - Compare the inventory against Git publishable paths and ancestor directories.
  - Verify README language links and the remote commit and file tree after publication.
not_applicable:
  - Package lint and TypeScript checking: documentation and ignore rules only; no runtime or build behavior changes.
  - Agent and safety evaluation: no business prompts, manifests or tool changes.
  - Release and deployment checks: this is repository publication, not a production deployment.
```

## 1. Background and assumptions

The local repository has no commits. Its README explains top-level ownership,
but there is no complete file catalog. The user approved an English catalog,
an English README with a linked Chinese translation, and direct publication
to the existing remote `main` branch, replacing its README without a new branch.

The remote default branch was confirmed as `main`. Preserve its commit history
by importing the verified local tree as a normal successor commit. No force push
is needed. Do not publish Git internals, credentials, caches, or local overrides.

## 2. Scope and contracts

Change documentation navigation, language guidance and local-settings exclusions.
Do not change runtime code, shared contracts, infrastructure or existing example
execution plans. Existing Chinese reference documents remain readable; new or
edited technical prose uses English except `README.zh.md`.

## 3. Work

1. Inspect repository guidance, module documentation and publishable paths.
2. Define a short entry point, task routes and an on-demand complete catalog.
3. Update root guidance and both READMEs; align documentation instructions.
4. Check links, catalog coverage, bilingual parity and required quality gates.
5. Archive this plan with real validation evidence and publish the verified tree.

## 4. Decisions and failure handling

- Use existing module READMEs and nested AGENTS.md files as local entry points.
  Do not duplicate runtime rules in the global catalog.
- Keep detailed purpose entries in `docs/repository-map.md`; read only the relevant
  section when a task needs it. `docs/index.md` routes by task.
- If the remote contains unexpected files or changes during publication, inspect
  the difference before proceeding. Do not delete unrelated remote content.
- A connector authentication failure is not publication evidence. Use an
  authenticated Git transport if available and verify the resulting remote SHA.

## 5. Validation

Executed on 2026-11-10. Commands below are relative to the repository root;
the restricted shell used absolute script/root paths where necessary.

| Command | Actual output | Result |
| --- | --- | --- |
| `python scripts/check-architecture.py` | `violations=0 affected_files=0` | Pass |
| `python scripts/check-agent-manifests.py` | `manifests=2 violations=0 affected_files=0` | Pass |
| `python scripts/check-doc-links.py` | `documents=86 violations=0 affected_files=0` | Pass |
| `python .agents/skills/verify-change/scripts/verify.py --root . --json` | All three gates exit 0; `pass: 3 fail: 0 blocked: 0` | Pass |
| `python -m unittest discover -s agents/research-agent/tests -t agents/research-agent -p "test_*.py"` | `Ran 17 tests`; `OK` | Pass |
| `python -m unittest discover -s agents/support-agent/tests -t agents/support-agent -p "test_*.py"` | `Ran 8 tests`; `OK` | Pass |
| `python -m unittest discover -s tests/contracts -p "test_*.py"` | `Ran 11 tests`; `OK` | Pass |
| `python -m unittest discover -s tests/end-to-end -p "test_*.py"` | `Ran 14 tests`; `OK` | Pass |

Additional read-only Python checks executed directly in the shell, without
adding scratch scripts to the repository:

- Catalog versus Git candidate paths: `files=189 directories=100 missing=0 stale=0 duplicates=0`.
- README parity: reciprocal language links, 23 shared link targets and identical
  check commands verified. All fragment links in the new entry points resolve.
- The first catalog review flagged a terse console-directory description. It
  was expanded; the complete coverage and navigation review then passed.
- Both personal override files are excluded. Credential settings in the shared
  MCP templates are environment placeholders. Candidate credential-signature
  scan: `files=189 findings=0`; this bounded scan is not a full security audit.

The 50 existing Python tests are offline baseline checks. No deployed system,
live model, cloud infrastructure, TypeScript build or external evaluation was
tested. No runtime, schema or public API contract was changed.

## 6. Publication

The target is `https://github.com/Yzdyx/AI-Coding-Template`, branch `main`.
The fetched remote tree contains only `README.md`, at commit
`37518f2efadbfb5fd86d70b68d1d68e97ff1f9dc`. The user explicitly approved replacing
that README and publishing directly to the default branch. Retain the remote
commit as the parent and use a normal push; do not create a feature branch.

The verified project was published as commit
`69d5438011376cc8440c32cdd4e89ce8a47f4b32`, with the original remote commit as
its parent. `git push --dry-run origin main:main` succeeded, followed by
`git push --set-upstream origin main:main`. `git ls-remote origin refs/heads/main`
returned the same project commit SHA. The repository now tracks `origin/main`.

`git diff --cached --check` reported no whitespace errors. Git preparation
initially rejected a command-scoped `core.excludesFile=NUL` override; using an
empty command-scoped override resolved it without changing global settings.
The final project tree contains 189 files and excludes both personal overrides.

This plan is archived after the project publication. Its catalog row and knowledge
index link move with it. The archive update is verified with the same repository
gates and published as a normal follow-up commit. No runtime contracts changed,
no infrastructure was applied and no temporary scripts were retained.
