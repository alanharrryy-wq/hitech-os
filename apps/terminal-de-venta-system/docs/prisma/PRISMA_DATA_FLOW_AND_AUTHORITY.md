---
title: PRISMA Data Flow and Authority
path: docs/prisma/PRISMA_DATA_FLOW_AND_AUTHORITY.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Data Flow and Authority

## Core operational model

```txt
Tablet sells locally.
PC governs backoffice when present.
Mobile supervises.
Chart Lab visualizes and experiments.
Control Center diagnoses and coordinates.
```

## Authority by domain

| Domain | Primary authority | Notes |
|---|---|---|
| Sales at POS | Tablet local runtime first | Must work offline. |
| Cash/shift at POS | Tablet local runtime first | PC may reconcile. |
| Catalog governance | PC when present | Tablet pulls deltas/bootstrap. |
| Inventory governance | PC/Canonical when present | Tablet may keep local snapshots for sale clarity. |
| Sync evidence | Shared contracts + Tablet/PC logs | Evidence must be append-only enough for audit. |
| Mobile summaries | Derived/read-only | No direct operational authority. |
| Chart Lab | Derived/public-safe/sandbox | Not production truth. |
| Control Center | Diagnostic/control plane | Not business data authority. |

## Flow summary

### Tablet → PC

Tablet creates local events/outbox. Dispatcher may send to PC ingest. PC validates, projects/reconciles and returns ACK/conflict/reject states.

### PC → Tablet

Current catalog delta authority uses:

```txt
PC: /api/sync/export/catalog-delta
Tablet: /api/pos/sync/pull
```

### Stubs

Any endpoint marked stub/guard must be documented as such and must not be used to conclude a whole flow is absent.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
