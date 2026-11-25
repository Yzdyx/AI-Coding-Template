# DOCS-0002: Complete the GitHub repository presence

## Task metadata

```yaml
task_id: DOCS-0002
title: Complete the GitHub repository presence with verified community and CI assets
owner_team: "@Yzdyx"
status: active
scope:
  paths:
    - AGENTS.md
    - CODEOWNERS
    - CONTRIBUTING.md
    - CODE_OF_CONDUCT.md
    - SUPPORT.md
    - SECURITY.md
    - README.md
    - README.zh.md
    - agents/research-agent/agent.yaml
    - agents/research-agent/prompts/system.md
    - agents/support-agent/agent.yaml
    - agents/support-agent/prompts/system.md
    - .github/ISSUE_TEMPLATE/bug_report.yml
    - .github/ISSUE_TEMPLATE/feature_request.yml
    - .github/ISSUE_TEMPLATE/config.yml
    - .github/workflows/pull-request.yml
    - docs/assets/repository-hero.svg
    - docs/assets/social-preview.png
    - docs/index.md
    - docs/repository-map.md
    - docs/exec-plans/active/DOCS-0002-complete-github-presence.md
    - docs/exec-plans/completed/DOCS-0002-complete-github-presence.md
    - scripts/check-agent-manifests.py
    - tests/contracts/test_agent_manifest_contract.py
  related_contracts:
    - schemas/agent-manifest.schema.json
acceptance:
  - The repository homepage presents a visual identity, live workflow status, purpose, architecture, quick start, repository areas, community routes, security route and template limits.
  - The English and Chinese READMEs link directly to each other and describe the same current project.
  - GitHub issue forms and community health files are valid, contain no fake contact details, and route security reports away from public issues.
  - CODEOWNERS resolves to a real repository owner and records where template adopters replace the owner.
  - The main branch runs the same repository gates as pull requests and exposes exact required-check names.
  - Every added or changed publishable path has a purpose in the repository catalog and a navigation route.
  - Required local checks, TypeScript checks and Python tests pass with recorded real output.
  - The verified commit is pushed directly to the existing main branch.
  - Remote About metadata, workflow status, community files, social preview and branch protection are verified after publication.
  - No open-source license grant is invented; the workspace remains UNLICENSED unless the owner supplies a license decision.
risk:
  level: low
  production_write: false
validation:
  - python scripts/check-architecture.py
  - python scripts/check-agent-manifests.py
  - python scripts/check-doc-links.py
  - python .agents/skills/verify-change/scripts/verify.py --root . --json
  - pnpm install --frozen-lockfile
  - pnpm -r typecheck
  - pnpm -r lint
  - pnpm -r test
  - python -m unittest discover -s agents/research-agent/tests -t agents/research-agent -p "test_*.py"
  - python -m unittest discover -s agents/support-agent/tests -t agents/support-agent -p "test_*.py"
  - python -m unittest discover -s tests/contracts -p "test_*.py"
  - python -m unittest discover -s tests/end-to-end -p "test_*.py"
  - Validate YAML syntax, SVG/PNG assets, catalog coverage, README parity and GitHub community profile.
not_applicable:
  - Infrastructure deployment, release promotion and production authentication: no infrastructure or runtime environment changes.
  - License selection: granting rights is an owner decision; UNLICENSED remains explicit.
```

## 1. Background

The published repository already has a strong documentation tree, About
description and topics. Its homepage still opens with a text-heavy README,
does not expose workflow status or a clear template path, and provides no
repository-level community health files or issue forms.

The pull-request workflow runs only for pull requests. The protected-branch
view therefore has no check record produced by ordinary commits to `main`.
CODEOWNERS also names organization teams that do not exist in this personal
repository. These are repository-governance defects, not presentation issues
alone.

## 2. Scope and contracts

This task changes presentation, repository governance and deterministic checks.
It does not change runtime code, shared schemas, provider contracts,
infrastructure or production state.

The English README remains the primary GitHub landing page. `README.zh.md`
remains its complete Chinese counterpart. Detailed engineering rules stay in
the existing indexed documents so root instructions remain short and stable.

## 3. Work

1. Add a native vector hero and social-preview asset.
2. Rework both README files around purpose, status, architecture, template use,
   validation, repository navigation, support, security and known limits.
3. Add contribution, conduct, support and security entry points, plus GitHub
   issue forms.
4. Replace fictional CODEOWNERS teams with the actual repository owner while
   documenting the replacement point for template adopters.
5. Run repository checks on pushes to `main` and pull requests.
6. Update progressive-disclosure navigation and the complete repository
   catalog.
7. Run local repository, TypeScript and Python checks; inspect rendered assets.
8. Publish to `main`, then configure and verify repository settings and branch
   protection against the resulting check names.

## 4. Decisions and failure handling

| Date | Decision | Alternatives | Reason | Impact |
| --- | --- | --- | --- | --- |
| 2026-11-25 | Keep `UNLICENSED` until the owner chooses a license | Choose MIT or another license without instruction | A license grants legal rights and cannot be inferred from a request for documentation | The community profile may show the license item as absent; the limitation is explicit |
| 2026-11-25 | Use a tracked SVG hero and a rendering-compatible PNG social preview | External image host or decorative raster hero | Native repository assets render in GitHub, remain reviewable and avoid remote dependencies | Both assets require catalog entries and visual verification |
| 2026-11-25 | Use GitHub-native issue forms and documented security routing | Mailbox address invented for the template | No real private contact was supplied; GitHub's reporting routes avoid publishing a fake address | The issue forms direct vulnerability reports to the repository Security route |
| 2026-11-25 | Keep role labels in engineering guidance but make CODEOWNERS valid now | Keep fictional team handles as examples | Invalid owners do not route reviews and make required-review settings unsafe to enable | The personal owner covers all paths until adopters replace it |
| 2026-11-25 | Normalize CODEOWNERS and manifest owner comparison by case and use `yzdyx` in manifests | Change the schema to allow uppercase personal handles | GitHub account handles are case-insensitive and the existing manifest pattern remains stable | Manifest ownership resolves against `@Yzdyx` without weakening schema validation |
| 2026-11-25 | Let `pnpm/action-setup@v4` read the exact version from `package.json` | Repeat `version: 9` in the workflow | The action rejects two version sources in a push run | CI uses the single declared `pnpm@9.12.0`, matching local and lockfile behavior |

If the remote branch changes during implementation, inspect and reconcile before
pushing. If a check fails, diagnose the actual failure and fix it or report the
unresolved boundary; do not relabel a failed or skipped check as a pass.

## 5. Assumptions and risks

| Type | Detail | Handling |
| --- | --- | --- |
| Assumption | The actual GitHub account is `@Yzdyx`, as returned by GitHub's repository API | Use it as the only owner and re-verify after publication |
| Risk | External badges may be unavailable temporarily | Keep the core README informative without badge images |
| Risk | Required checks cannot be selected until they have run on `main` | Push the workflow change first, wait for successful runs, then configure protection |
| Risk | GitHub personal repositories may not support every branch-protection option | Enable only options accepted by the repository's current plan and verify the saved state |
| Limit | `UNLICENSED` gives no open-source reuse grant | State it plainly in the README and final report |

## 6. Validation

Run every applicable command in the task metadata. Record the actual output,
the tested commit, the remote commit after push, the completed Actions run and
the saved repository settings. Validate the SVG and social-preview PNG by
rendering or direct visual inspection.

## 7. Archive

After acceptance and publication, change status to `completed`, move this file
to `docs/exec-plans/completed/`, update its catalog row and knowledge-index link,
rerun the repository gates, and commit the archive as a normal successor.
