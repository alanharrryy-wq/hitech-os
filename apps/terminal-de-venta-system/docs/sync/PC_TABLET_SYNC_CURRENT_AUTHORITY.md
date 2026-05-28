---
title: PC Tablet Sync Current Authority
path: docs/sync/PC_TABLET_SYNC_CURRENT_AUTHORITY.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PC Tablet Sync Current Authority

## Current authority summary

| Flow | Status | Current authority |
|---|---|---|
| Tablet → PC sales/events | Implemented/gated | Tablet dispatcher + PC ingest. |
| PC → Tablet catalog delta | Implemented by current route | `/api/sync/export/catalog-delta` + `/api/pos/sync/pull`. |
| Backoffice export-pc-to-tablet | Stub/guard | Do not treat as current export authority. |

## Tablet → PC evidence paths

```txt
products/tablet/app/src/server/sync/dispatcher.ts
products/pc/app/app/api/backoffice/sync/ingest/route.ts
```

## PC → Tablet evidence paths

```txt
products/pc/app/app/api/sync/export/catalog-delta/route.ts
products/pc/app/src/server/services/catalog-delta-export.service.ts
products/tablet/app/app/api/pos/sync/pull/route.ts
products/tablet/app/src/server/sync/catalog-pull.ts
```

## Legacy closure docs

Historical closure docs live under `docs/legacy/sync`. They remain useful as history but no longer override this document.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
