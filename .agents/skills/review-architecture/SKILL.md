---
name: review-architecture
description: Review a change against the layering, dependency and contract rules before merge.
---

# Review Architecture

Run this skill on a pull request that changes a public interface, adds a module, or adds an import across a module boundary.

## Steps

1. Read the diff. List every new or changed import.
2. Rank each file by layer, using the table in
   [`docs/architecture/index.md`](../../../docs/architecture/index.md) section 3.
3. Reject an import that points upward in `Types -> Config -> Repo -> Service -> Runtime -> UI`.
4. Reject a deep import into another module's `src/`.
5. Reject a `new <ConcreteProvider>()` outside the composition root.
6. Check every changed contract against `schemas/`. Classify it `additive` or `breaking`.
7. Confirm an ADR exists for a breaking change, a new Provider, a new top-level directory or a new external dependency class.
8. Run `python scripts/check-architecture.py` and paste the real output.

## Output

| Severity | File:line | Rule violated | Required action |
| --- | --- | --- | --- |

## Rules

- A rule with no automated check is a suggestion. Report the missing check.
- Do not approve a change that weakens a check to make itself pass.
- State uncertainty. Do not guess the intent of an import.
