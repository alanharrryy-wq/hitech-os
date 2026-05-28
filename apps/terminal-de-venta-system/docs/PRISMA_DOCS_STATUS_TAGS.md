---
title: PRISMA Docs Status Tags
path: docs/PRISMA_DOCS_STATUS_TAGS.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Docs Status Tags

Every authority document must declare a status. Documents without a status header are readable history, not governance authority.

| Status | Meaning | Can Gemini trust it first? |
|---|---|---|
| `CURRENT` | Current authority for its scope. | Yes. |
| `CURRENT_WITH_GAPS` | Current but explicitly incomplete. | Yes, with caveats. |
| `PLANNED` | Design/decision not implemented. | Yes as plan, no as code state. |
| `DRAFT` | Work in progress. | No, unless cited as draft. |
| `HISTORICAL` | Preserved evidence. | No, unless no current doc exists. |
| `LEGACY` | Moved out of authority path. | No. |
| `SUPERSEDED` | Replaced by another doc. | No. |
| `UNKNOWN` | Not classified. | No. |

## Required header fields

```yaml
status: CURRENT
updated: YYYY-MM-DD
owner: PRISMA Governance
live_verification: false
supersedes: []
```

## AI interpretation rule

If an AI reads a `LEGACY`, `SUPERSEDED`, `HISTORICAL`, `DRAFT` or `UNKNOWN` document, it must say so before using it. Otherwise Gemini will happily quote a retired doc like it still owns the building.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
