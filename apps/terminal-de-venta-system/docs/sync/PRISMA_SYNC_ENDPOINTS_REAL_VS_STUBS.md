---
title: PRISMA Sync Endpoints Real vs Stubs
path: docs/sync/PRISMA_SYNC_ENDPOINTS_REAL_VS_STUBS.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Sync Endpoints: Real vs Stubs

## Current real/active sync paths

| Endpoint | Surface | Classification | Notes |
|---|---|---|---|
| `/api/backoffice/sync/ingest` | PC | Real ingest | Tablet → PC payload receiver. |
| `/api/sync/export/catalog-delta` | PC | Real/current catalog export | PC → Tablet catalog delta/bootstrap authority. |
| `/api/pos/sync/pull` | Tablet | Real/current pull | Tablet pulls PC catalog data. |
| `/api/pos/sync/dispatch` | Tablet | Real/gated dispatch | Sends Tablet outbox to PC. |
| `/api/pos/events/outbox` | Tablet | Real/local evidence | Outbox inspection/actions. |

## Stub/guard paths

| Endpoint | Surface | Classification | Notes |
|---|---|---|---|
| `/api/backoffice/sync/export-pc-to-tablet` | PC | Stub/guard | Not current PC → Tablet authority. |
| `/api/backoffice/demo/seed` | PC | Stub/guard | Mutation intentionally blocked until safe lifecycle exists. |
| `/api/backoffice/demo/purge` | PC | Stub/guard | Mutation intentionally blocked. |
| `/api/backoffice/demo/reset` | PC | Stub/guard | Mutation intentionally blocked. |

## Documentation rule

Any report that lists endpoints must include this classification. Otherwise the repo ends up with “route exists” and “route works” wearing the same sombrero.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
