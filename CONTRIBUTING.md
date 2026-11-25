# Contributing

Thank you for helping improve AI Coding Template. This repository accepts
documentation fixes, defect reports, test improvements, and scoped code changes
that preserve its architecture and evidence rules.

## Before you start

1. Read [AGENTS.md](AGENTS.md) for repository-wide constraints.
2. Open [docs/index.md](docs/index.md) and follow only the task-specific route.
3. Read the affected module's `README.md`, nested `AGENTS.md`, and current tests.
4. For a cross-module change, create an execution plan under
   `docs/exec-plans/active/` before editing.
5. For a large behavior change or new shared contract, open an issue first so
   scope and ownership can be agreed.

Use [SUPPORT.md](SUPPORT.md) for usage questions. Report vulnerabilities through
[SECURITY.md](SECURITY.md), never through a public issue.

## Development workflow

1. Create a focused branch from `main`.
2. Make the smallest change that solves the stated problem.
3. Keep generated output, local state, credentials, and editor settings out of
   the commit.
4. Update the nearest index or `README.md` and
   [docs/repository-map.md](docs/repository-map.md) when a publishable path
   changes.
5. Run the checks relevant to the changed files.
6. Open a pull request using the repository template and paste real command
   output, including failures or skipped checks.

## Quality checks

Run commands from the repository root.

```powershell
python scripts/check-architecture.py
python scripts/check-agent-manifests.py
python scripts/check-doc-links.py
python .agents/skills/verify-change/scripts/verify.py --root .

pnpm install --frozen-lockfile
pnpm -r typecheck
pnpm -r lint
pnpm -r test
```

Python agents and cross-module tests use `unittest`. A skipped check is not a
pass. Do not weaken a test expectation to make a regression disappear.

## Code and documentation rules

- Follow `Types → Config → Repo → Service → Runtime → UI` dependency direction.
- Use public package interfaces and explicit Provider interfaces.
- Preserve human approval gates for high-risk and irreversible actions.
- Write code, commit messages, and new or edited technical prose in English.
- Keep [README.md](README.md) and [README.zh.md](README.zh.md) aligned; update
  both language links when either entry point changes.
- Keep root guidance short. Put detailed rules at their owning document and link
  to them through the progressive-disclosure indexes.
- State evidence, limits, and uncertainty. Do not claim production verification
  from offline tests or examples.

## Pull requests

A useful pull request explains:

- the user-visible or engineering problem;
- the behavior change and affected paths;
- contracts and migration impact;
- commands run and their actual results;
- risk, rollback, skipped checks, and unresolved boundaries.

Use the repository's
[pull request template](.github/PULL_REQUEST_TEMPLATE.md). Reviewers may request
a narrower scope when a change mixes unrelated concerns.

## Community standards

All participation is covered by the [Code of Conduct](CODE_OF_CONDUCT.md).
Harassment, discriminatory conduct, disclosure of private information, and
deliberate disruption are not accepted.

## Licensing

The workspace currently declares `UNLICENSED`. Open an issue before preparing an
external code contribution while no reuse license is selected. A contribution
does not change the repository's license status.
