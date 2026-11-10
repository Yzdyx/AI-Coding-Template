---
applyTo: "docs/**/*.md"
---

# Documentation Instructions

These rules apply to every Markdown document under `docs/`.

## Language

- Write new or edited technical prose in English. `README.zh.md` is the Chinese
  translation of `README.md`; keep their language links and shared instructions in sync.
- Existing Chinese reference documents remain available. Translate only the
  sections needed by an authorized change; do not rewrite unrelated documents.
- Keep code, commands, paths, identifiers and technical terms in English.
- One idea per sentence. Active voice. Present tense for a rule.

## Structure

- Start with `docs/index.md`, then the relevant local index or README, then the
  exact document. Do not require readers to load the whole knowledge base.
- Register a new document in the nearest index or README. If no local entry
  exists, use `docs/index.md`; add a local index when the area needs its own route.
- Record every added, moved, renamed or removed project path in
  `docs/repository-map.md`. Give directories and files distinct, concrete roles.
- A document that nothing links to is a defect. `scripts/check-doc-links.py` reports it.
- Link with a relative path, from the file that holds the link. The same script checks it.
- Keep a table of contents only when a document has more than six sections.

## Content rules

1. Describe intent, constraints and reasons. Do not restate code.
2. State every rule so that a reader can decide whether it is violated.
3. Give each rule a home: a check script, a policy file, a test or a manifest field.
   A rule with no home is a suggestion, and it does not belong in a normative document.
4. Record a decision with its alternatives and its reason. A decision without a
   reason is rewritten at the next review.
5. Never write a credential, a token, an internal hostname or a customer value.

## Generated content

- `docs/generated/` is produced by a generator. Never edit it by hand.
- When the generator does not exist, the file says so. Keep that statement true.

## Lifecycle

- Update the document in the same pull request as the code it describes.
- Mark an obsolete document `Deprecated`. Do not delete it.
- Bump the status field: `Draft`, `Active`, `Stable`, `Deprecated`.
