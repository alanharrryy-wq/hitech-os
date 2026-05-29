---
title: PRISMA Final PC Tablet Architecture
path: docs/architecture/PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Final PC + Tablet Architecture

## Decision

Tablet and PC are twin operational surfaces with different authority roles.

```txt
Tablet = local sale, offline resilience, POS evidence.
PC = canonical/backoffice governance when present.
```

## Boundaries

Tablet must sell without PC. PC must not be required for checkout. PC can later receive, validate and govern catalog, inventory, purchases, suppliers, reports and audit.

## Current implementation by static evidence

| Area | Status |
|---|---|
| Tablet POS local sale | Confirmed by code. |
| Tablet outbox/dispatcher | Confirmed by code, may be env-gated. |
| PC ingest | Confirmed by code. |
| PC catalog delta export | Confirmed by current route. |
| Backoffice export-pc-to-tablet | Stub/guard, not current authority. |
| PC seed/reset demo mutation | Intentionally blocked/stubbed until lifecycle safety exists. |

## Architecture rule

No document may claim Tablet depends on PC for sale. No document may claim PC → Tablet catalog is absent solely from the old stub route.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
