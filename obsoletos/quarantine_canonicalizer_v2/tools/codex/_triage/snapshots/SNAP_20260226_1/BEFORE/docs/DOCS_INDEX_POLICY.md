# DOCS INDEX POLICY

Version: 1.0.0
Last Updated: 2026-02-23

## Purpose

Define deterministic generation rules for `docs/DOCS_INDEX.md`.

## Rules

1. Source of truth is the `docs/` tree (recursive), excluding `docs/DOCS_INDEX.md` itself.
2. File rows must be sorted lexicographically by relative path.
3. Each row must include file path, extracted title, line count, and byte count.
4. Generation command is `node tools/scripts/generate_docs_index.mjs`.
5. Regeneration is mandatory after any doc add/remove/rename/update.

## Enforcement

1. `pnpm run docs` must produce deterministic output with no unstable ordering.
2. `docs/DOCS_INDEX.md` must be committed with doc changes.
3. Governance docs (`CONTRACT`, `CONSTITUTION`) are first-class index entries.
