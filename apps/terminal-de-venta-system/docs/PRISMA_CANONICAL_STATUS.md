---
title: PRISMA Canonical Status
path: docs/PRISMA_CANONICAL_STATUS.md
status: CURRENT_WITH_GAPS
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Canonical Status

## Status

`CURRENT_WITH_GAPS`: PRISMA has a canonical database strategy. This document establishes authority rules, but it does not claim a live read of the current database contents.

## PC canonical authority

PC canonical database authority is resolved by the PC runtime, not by static file discovery.

Priority:

1. `DATABASE_URL` if present.
2. Resolver code in `products/pc/app/src/server/prisma/client.ts`.
3. Default local runtime DB path:

```txt
F:epos\hitech-os	ools\_local\data	erminal-de-venta-system\canonical.db
```

## Not runtime authority by itself

```txt
products/pc/app/data/canonical.db
```

This file may exist and may be empty. It is not active authority unless runtime config/resolver says so.

## Historical evidence

`shared/tri-db/status.latest.json` may report a PC DB path and row counts. Treat it as historical evidence with its timestamp, not a live guarantee.

## Required future verifier

A runtime verifier should emit:

```json
{
  "pc_database_source": "DATABASE_URL | runtime_resolver | unknown",
  "resolved_path": "...",
  "exists": true,
  "schema_ok": true,
  "row_counts": {},
  "timestamp": "..."
}
```

Until then, docs must distinguish authority from live content.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
