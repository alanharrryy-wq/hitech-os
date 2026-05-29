---
title: Governance Staleness Policy
path: docs/governance/GOVERNANCE_STALENESS_POLICY.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# Governance Staleness Policy

## Purpose

Detect documents that are older than current authority or contradict implementation evidence.

## Staleness signals

A document is stale when it:

- says a flow is missing but current route/source exists
- names a DB file as active without resolver evidence
- uses old endpoint names as authority
- describes a demo/stub as live runtime
- lacks status header while making operational claims
- contradicts `PRISMA_CURRENT_STATE.md/json`

## Required report fields

```json
{
  "path": "docs/...",
  "status": "STALE | CURRENT | LEGACY | UNKNOWN",
  "reason": "...",
  "superseded_by": "docs/...",
  "recommended_action": "keep | update | move_to_legacy"
}
```

## AI ingestion

Gemini must receive staleness metadata with docs. Without this, it may treat a closure note from last week like it just walked in with a royal decree.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
