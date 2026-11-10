---
name: sync-docs
description: Keep the knowledge base consistent with the code in the same pull request.
---

# Sync Docs

Run this skill when a change alters behavior, structure, contracts or operations.

## Steps

1. Map the change to the documents that describe it:

   | Change | Document to update |
   | --- | --- |
   | Layer or module boundary | `ARCHITECTURE.md`, `docs/architecture/dependency-rules.md`, an ADR |
   | Public contract | `schemas/`, `docs/architecture/index.md` |
   | Product behavior | `docs/product-specs/` |
   | Runtime behavior, SLO, runbook | `docs/operations/` |
   | Security control | `docs/security/` |
   | Index of a directory | the `index.md` of that directory |

2. Update the affected document in the same commit as the code.
3. Add or update the index entry. An unindexed document is invisible to agents.
4. Regenerate `docs/generated/` instead of editing it by hand.
5. Run `python scripts/check-doc-links.py` and paste the real output.
6. Mark an obsolete document `Deprecated` instead of deleting it.

## Rules

- A document that contradicts the code is a defect. Report it.
- Do not restate code in prose. Describe intent, constraints and reasons.
- Keep every document reachable from an index. No orphan files.
