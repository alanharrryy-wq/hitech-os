---
title: PRISMA Current State
path: docs/PRISMA_CURRENT_STATE.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Current State

This is the **single current-state entry point** for PRISMA documentation. It exists to stop old docs, stubs, snapshots, and discovered files from arguing like neighbors with three different water bills.

## Current-state verdict

PRISMA is an advanced multi-surface commerce system with real code across Tablet, PC, Mobile, Chart Lab and Control Center. It is not a blank prototype. It is also not certified here as fully live end-to-end, because this package does not execute the repo.

| Surface | Current static-evidence status | Notes |
|---|---|---|
| Tablet POS | `CONFIRMED_BY_CODE` | Local POS, checkout, sales completion, shift, catalog, outbox and sync dispatch code exist. |
| PC Backoffice | `CONFIRMED_BY_CODE_WITH_GAPS` | Backoffice routes and APIs exist; some mutation/demo endpoints intentionally remain blocked. |
| PC canonical DB | `RUNTIME_RESOLVED_AUTHORITY` | Do not infer active DB from `products/pc/app/data/canonical.db`. See DB authority docs. |
| Tablet → PC sales sync | `IMPLEMENTED_PARTIAL_OR_GATED` | Dispatcher and PC ingest exist; dispatch may be controlled by environment gate. |
| PC → Tablet catalog delta | `IMPLEMENTED_BY_CURRENT_ROUTE` | Current route is `/api/sync/export/catalog-delta`; the backoffice export route is a stub/guard. |
| Mobile | `SUPERVISION_SURFACE_CONFIRMED_BY_CODE` | Mobile APIs center on owner/supervision, not POS. |
| Chart Lab | `CONFIRMED_BY_CODE` | Runtime, ECharts, verification and Cloudflare static deployment scripts exist. |
| Control Center | `CONFIRMED_BY_CODE` | Python/web local control plane with health, quality, release, license and blackbox tooling. |
| Unified Shell Lab v3 | `SAFE_LAB_CONFIRMED_BY_CODE` | Separate lab shell around surfaces; not current Control Center authority. |
| Gemini Copilot | `PLANNED_NOT_IMPLEMENTED` | Scope is documented in this package; no Gemini SDK integration was found in the inspected code. |
| Data Lifecycle | `PLANNED_NOT_IMPLEMENTED` | Decision doc exists here; code was not present in inspected packages. |

## Mandatory precedence

When documents disagree, resolve in this order:

1. `docs/PRISMA_CURRENT_STATE.json`
2. `docs/PRISMA_CURRENT_STATE.md`
3. `docs/PRISMA_DOCUMENT_PRECEDENCE_RULES.md`
4. Runtime resolver source files named inside this package
5. Current authority docs under `docs/prisma`, `docs/sync`, `docs/architecture`, `docs/control-center`, `docs/ai`
6. Historical closure docs only when not contradicted by a current authority document
7. `docs/legacy/**` never wins over current authority

## Known contradictions resolved

### PC canonical database

`products/pc/app/data/canonical.db` was found by a static atlas and may be empty. That does **not** make it the active PC database.

The PC runtime authority is the resolver in:

```txt
products/pc/app/src/server/prisma/client.ts
```

Expected default PC runtime DB path:

```txt
F:epos\hitech-os	ools\_local\data	erminal-de-venta-system\canonical.db
```

If `DATABASE_URL` exists, it wins.

### PC → Tablet catalog sync

The old/stub route is:

```txt
/api/backoffice/sync/export-pc-to-tablet
```

The current implemented catalog delta route is:

```txt
/api/sync/export/catalog-delta
```

Tablet consumes through:

```txt
/api/pos/sync/pull
```

Do not conclude PC → Tablet is missing merely because the old backoffice export route returns `501`.

## State labels

| Label | Meaning |
|---|---|
| `CONFIRMED_BY_CODE` | Static source code exists and supports the claim. |
| `CONFIRMED_BY_DOC` | A current document supports the claim. |
| `CONFIRMED_BY_HISTORICAL_EVIDENCE` | Snapshot or status file supports the claim but may not be live. |
| `IMPLEMENTED_BY_CURRENT_ROUTE` | Current route/service is implemented. |
| `STUB_OR_GUARD` | Route/file exists intentionally blocked or placeholder. |
| `PLANNED_NOT_IMPLEMENTED` | Design decision exists; code not found. |
| `LEGACY_SUPERSEDED` | Historical doc retained but no longer authority. |
| `UNKNOWN_REQUIRES_LIVE_CHECK` | Needs runtime execution outside this package. |


## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
