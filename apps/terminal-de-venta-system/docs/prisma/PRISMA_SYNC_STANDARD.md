---
title: PRISMA Sync Standard
path: docs/prisma/PRISMA_SYNC_STANDARD.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Sync Standard

## Purpose

Standardize PRISMA sync language, states, routes and evidence.

## State vocabulary

| Technical state | User meaning |
|---|---|
| `received` | PC received a package. |
| `validated` | Package passed basic checks. |
| `accepted` | Package accepted for processing. |
| `projected` | Changes projected into target model. |
| `reconciled` | Sync completed successfully. |
| `conflict` | Needs conflict handling. |
| `rejected` | Package not accepted. |
| `failed` | Processing failed. |
| `dead_letter` | Requires manual/diagnostic attention. |

## Endpoint authority

See `docs/sync/PRISMA_SYNC_ENDPOINTS_REAL_VS_STUBS.md` for current endpoint status.

## Evidence requirement

Every sync closure must document:

- source surface
- target surface
- endpoint path
- payload family
- ACK/conflict behavior
- retry behavior
- timestamped evidence
- status: implemented, stub, gated, planned, or legacy

## User-facing copy

Do not expose `ingest`, `ack`, `delta`, `dispatcher` first. Translate to operational language, then provide technical detail behind an evidence drawer.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
