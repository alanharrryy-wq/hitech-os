---
title: PC Tablet Operational Contract
path: docs/architecture/PC_TABLET_OPERATIONAL_CONTRACT.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PC Tablet Operational Contract

## Roles

| Surface | Role | Can operate alone? |
|---|---|---|
| Tablet | Sell, shift, local catalog, outbox, offline evidence | Yes |
| PC | Backoffice, catalog governance, stock, purchasing, audit, reconciliation | Yes for backoffice, not required for Tablet checkout |

## Contract

1. Tablet owns immediate sale completion.
2. Tablet records evidence and outbox events.
3. PC ingests Tablet events when available.
4. PC governs catalog/inventory/master data where configured.
5. Tablet can pull PC catalog deltas/bootstrap.
6. Conflicts must be explainable in business language.
7. AI must not mutate these flows in v1.

## Unsupported assumptions

- “PC canonical DB inside source tree is active because it exists.” False.
- “PC → Tablet is missing because one old backoffice route is stubbed.” False.
- “Mobile is POS.” False.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
