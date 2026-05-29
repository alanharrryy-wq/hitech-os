---
title: PC to Tablet Catalog Delta Closure 01
path: docs/sync/PC_TO_TABLET_CATALOG_DELTA_CLOSURE_01.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PC → Tablet Catalog Delta Closure 01

## Status

`CURRENT`: PC → Tablet catalog delta authority is implemented through the current sync/export route and Tablet pull route.

## Current endpoints

```txt
PC export:      /api/sync/export/catalog-delta
Tablet pull:    /api/pos/sync/pull
```

## Current source authority

```txt
products/pc/app/app/api/sync/export/catalog-delta/route.ts
products/pc/app/src/server/services/catalog-delta-export.service.ts
products/tablet/app/app/api/pos/sync/pull/route.ts
products/tablet/app/src/server/sync/catalog-pull.ts
```

## Not current authority

```txt
/api/backoffice/sync/export-pc-to-tablet
```

That route may exist as a stub/guard. It must not be used to claim PC → Tablet catalog sync is missing.

## Data families

The catalog delta family may include products, barcodes, prices, stock snapshots, supplier links and freshness/cursor data depending on runtime implementation.

## Evidence caveat

This document confirms static code authority. It does not claim a fresh live pull test.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
