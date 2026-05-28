---
title: PRISMA Legacy Docs Index
path: docs/PRISMA_LEGACY_DOCS_INDEX.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Legacy Docs Index

This index tracks documents preserved as history but removed from current authority.

## Legacy sync docs

| Legacy path | Previous path | Superseded by | Reason |
|---|---|---|---|
| `docs/legacy/sync/PRISMA_SYNC_CLOSURE_BUNDLE_20260521.md` | `docs/prisma/PRISMA_SYNC_CLOSURE_BUNDLE_20260521.md` | `docs/sync/PC_TABLET_SYNC_CURRENT_AUTHORITY.md` and `docs/sync/PC_TO_TABLET_CATALOG_DELTA_CLOSURE_01.md` | Its PC → Tablet gap statement is no longer the active authority. |
| `docs/legacy/sync/PRISMA_SYNC_CLOSURE_PATCH_20260518.md` | `docs/prisma/PRISMA_SYNC_CLOSURE_PATCH_20260518.md` | `docs/sync/PC_TABLET_SYNC_CURRENT_AUTHORITY.md` | Historical patch context only. |

## Legacy rule

Legacy docs may be quoted only with their status attached. A future AI assistant must not answer from legacy docs unless it also checks the current authority docs.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
