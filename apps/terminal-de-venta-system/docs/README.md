---
title: PRISMA Docs README
path: docs/README.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Documentation

This folder is governed by `PRISMA_CURRENT_STATE.md`. New contributors, operators and future AI tooling must start there.

## Read order

1. `PRISMA_CURRENT_STATE.md`
2. `PRISMA_CURRENT_STATE.json`
3. `PRISMA_MASTER_DOC_INDEX.md`
4. `PRISMA_DOCUMENT_PRECEDENCE_RULES.md`
5. Domain authority docs:
   - `prisma/PRISMA_DATABASE_AUTHORITY.md`
   - `prisma/PRISMA_DATA_FLOW_AND_AUTHORITY.md`
   - `sync/PC_TABLET_SYNC_CURRENT_AUTHORITY.md`
   - `sync/PRISMA_SYNC_ENDPOINTS_REAL_VS_STUBS.md`
   - `control-center/PRISMA_CONTROL_CENTER_CURRENT_STATE.md`
   - `ai/PRISMA_GEMINI_COPILOT_SCOPE_V1.md`

## What changed in this governance refresh

- A current-state authority layer was added.
- Legacy sync closure docs were moved under `docs/legacy/sync`.
- The PC database contradiction was resolved by runtime authority.
- The PC → Tablet contradiction was resolved by distinguishing real route vs stub route.
- Gemini Copilot and Data Lifecycle were explicitly marked as planned, not implemented.
- Government package/extractor scope rules were documented.

## Hard rule

If a document lacks a status header, treat it as **non-authoritative until classified**. No more docs running around the repo like stray dogs with admin privileges.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
