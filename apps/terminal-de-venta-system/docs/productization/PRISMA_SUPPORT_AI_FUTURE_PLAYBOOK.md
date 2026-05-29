---
title: PRISMA Support AI Future Playbook
path: docs/productization/PRISMA_SUPPORT_AI_FUTURE_PLAYBOOK.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Support AI Future Playbook

## Goal

Use AI to reduce support friction while keeping PRISMA operationally safe.

## Recommended phases

### Phase 1: Evidence reader

- read docs
- read support bundles
- explain errors
- cite source files
- no mutations

### Phase 2: Guided diagnostics

- propose commands
- create draft runbooks
- generate investigation plans
- still no execution by AI

### Phase 3: Approved actions

Only after strict allowlist, confirmations, audit log, backup and rollback exist.

## Must integrate with

- `PRISMA_CURRENT_STATE.md/json`
- support bundles
- Control Center health reports
- Governance staleness reports
- no-leak scanner outputs

## Anti-patterns

- AI reads every repo file with no precedence.
- AI quotes legacy docs as current.
- AI receives raw `.env` or DBs.
- AI claims live status without live check.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
