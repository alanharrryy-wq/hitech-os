---
title: PRISMA Gemini Copilot Scope v1
path: docs/ai/PRISMA_GEMINI_COPILOT_SCOPE_V1.md
status: PLANNED
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Gemini Copilot Scope v1

## Status

`PLANNED`: Gemini Copilot was not found as implemented code in the inspected source package. This document defines scope only.

## Purpose

PRISMA Gemini Copilot reads sanitized documentation and evidence, answers questions, explains failures and cites sources.

## It may do

- read docs and manifests
- search current authority docs
- explain sync, DB, Control Center, Chart Lab and runtime status
- summarize support bundles
- explain Data Lifecycle reports when that module exists
- produce next-action suggestions
- cite evidence paths

## It must not do in v1

- execute commands
- mutate DBs
- run Clear/seed/reset
- change licenses
- deploy
- touch production
- upload secrets or raw DBs
- answer from legacy docs without warning

## Memory layers

| Layer | Use | Gemini mechanism |
|---|---|---|
| Stable knowledge | Current docs and contracts | File Search Store or equivalent. |
| Temporary evidence | ZIPs, logs, support bundles | Files API / temporary upload. |
| Current state | `PRISMA_CURRENT_STATE.md/json` | Highest priority context. |

## Required answer style

Every answer about project state must classify claims:

```txt
Confirmed by current doc
Confirmed by source code
Historical evidence only
Planned, not implemented
Unknown without live check
```

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
