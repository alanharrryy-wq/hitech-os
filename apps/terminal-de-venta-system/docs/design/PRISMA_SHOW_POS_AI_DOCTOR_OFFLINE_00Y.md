---
title: PRISMA Show POS AI Doctor Offline 00Y
path: docs/design/PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Show POS AI Doctor Offline 00Y

## Status

`CURRENT`: This is a design boundary for offline/support-style AI Doctor behavior. It is not Gemini implementation.

## Policy

```json
{
  "defaultProvider": "none",
  "apiCost": "none",
  "allowRuntimeMutation": false,
  "allowRepoMutation": false
}
```

## Role

AI Doctor may interpret reports and provide human-readable support explanations. It does not close sales, change stock, mutate runtime, change licenses or rewrite repo files.

## Relationship to Gemini Copilot

Gemini Copilot may extend this concept with managed file/search context, but must preserve the same first principle:

```txt
Read/explain first. Mutate never in v1.
```

## Recommended UI copy

```txt
AI Doctor can explain what happened and what to inspect next.
It cannot change your sale, stock, license or database.
```

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
