---
title: PRISMA Database Authority
path: docs/prisma/PRISMA_DATABASE_AUTHORITY.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Database Authority

This document resolves database authority for PRISMA.

## Rule mother

The authority is not the file with the prettiest name. The authority is the runtime resolver, explicit environment configuration, and timestamped evidence.

## PC

| Item | Classification |
|---|---|
| `DATABASE_URL` | Primary authority when present. |
| `products/pc/app/src/server/prisma/client.ts` | Resolver authority. |
| `F:
| `tools/_local/data/terminal-de-venta-system/canonical.db` | Expected default runtime DB path under repo-local tooling data. |
| `products/pc/app/data/canonical.db` | Discovered SQLite/source-tree candidate; not active authority by name alone. |

## Tablet

Tablet owns local/offline POS data and evidence needed to sell without PC.

Expected local DB candidates found in prior static analysis:

```txt
products/tablet/app/data/tablet-pos.db
products/tablet/app/prisma/data/tablet-pos.db
```

Runtime authority must still be resolved by Tablet config/source, not by filename alone.

## Chart Lab

Chart Lab may use public-safe runtime snapshots and governance DBs. Chart Lab data must not be treated as the operational PC or Tablet source of truth.

## Mobile

Mobile is supervision/summary surface. It should not become authority for sales, stock or catalog mutation.

## Control Center

Control Center observes, launches, diagnoses and reports. It is not the operational source of sales/inventory truth.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
