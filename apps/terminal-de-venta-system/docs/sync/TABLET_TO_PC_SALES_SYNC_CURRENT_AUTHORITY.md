---
title: Tablet to PC Sales Sync Current Authority
path: docs/sync/TABLET_TO_PC_SALES_SYNC_CURRENT_AUTHORITY.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# Tablet → PC Sales Sync Current Authority

## Status

`CURRENT`: Tablet → PC sync has source code evidence for dispatcher/outbox behavior and PC ingest. Runtime enablement may depend on environment/config.

## Authority files

```txt
products/tablet/app/src/server/sync/dispatcher.ts
products/tablet/app/app/api/pos/sync/dispatch/route.ts
products/tablet/app/app/api/pos/events/outbox/route.ts
products/pc/app/app/api/backoffice/sync/ingest/route.ts
```

## Expected behavior

1. Tablet records local sale/evidence.
2. Tablet writes outbox events.
3. Dispatcher sends batches when enabled and PC endpoint is available.
4. PC ingest receives and persists/validates the payload.
5. ACK/conflict/rejected/failed states update outbox lifecycle.
6. Tablet must continue selling if PC is unavailable.

## Current caveat

This package does not run the dispatcher. Treat this as static code authority, not live PASS evidence.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
