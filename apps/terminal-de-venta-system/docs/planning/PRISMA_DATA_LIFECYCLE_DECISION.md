---
title: PRISMA Data Lifecycle Decision
path: docs/planning/PRISMA_DATA_LIFECYCLE_DECISION.md
status: PLANNED
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Data Lifecycle Decision

## Status

`PLANNED`: This is an approved design direction, not implemented code in the inspected packages.

## Location decision

```txt
prisma-control-center
└── New tab: PRISMA Data Lifecycle
```

## UI visible

| Zone | Control |
|---|---|
| Inject data | Dropdown: `Ligera`, `Pesada`, `Pasada de longaniza` + button `Inyectar` |
| Clear | Single `Clear` button |
| Dashboard | Current counts by domain |

## Internal domains

```txt
Sales
Cash
Inventory
Catalog
Suppliers
Purchasing
Sync
Devices
Identity
Tenant
License
Audit
Chart Lab
All
```

## Provenance tags

Generated records should carry:

```txt
source = prisma_data_lifecycle
batch_id = lifecycle_YYYYMMDD_HHMMSS
seed_mode = light | heavy | longaniza
```

## Clear rules

- PIN 6 digits
- default proposal: `030303`
- backup required
- evidence report required
- clear by domain/provenance, not table wipe
- no raw production cleanup without tags

## Relationship to Gemini

Gemini may later read Data Lifecycle reports. Gemini must not run Clear or inject data.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
