---
title: PRISMA Document Precedence Rules
path: docs/PRISMA_DOCUMENT_PRECEDENCE_RULES.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Document Precedence Rules

This document resolves contradictions between docs, code, generated atlases and historical closure bundles.

## Precedence ladder

1. `PRISMA_CURRENT_STATE.json`
2. `PRISMA_CURRENT_STATE.md`
3. This document
4. Runtime resolver/config source files named by current authority docs
5. Current domain docs
6. Generated status files with timestamps
7. Historical docs
8. Legacy docs

## Resolution examples

### Example: PC DB

If `products/pc/app/data/canonical.db` exists but the resolver points elsewhere, the resolver wins.

### Example: sync endpoint

If `/api/backoffice/sync/export-pc-to-tablet` returns `501` but `/api/sync/export/catalog-delta` is implemented and current docs name it as authority, the real route wins and the backoffice route is classified as stub.

### Example: old closure doc

If a 2026-05-21 closure doc says PC → Tablet is future work but a later `PC_TO_TABLET_CATALOG_DELTA_CLOSURE_01.md` and source code show implementation, the later authority wins.

## No silent downgrade

A document may be moved to legacy but must not be deleted without an explicit migration note. Historical context is useful; uncontrolled authority is the problem.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
