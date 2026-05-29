---
title: PRISMA Legacy Docs README
path: docs/legacy/README.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Legacy Docs

This folder preserves historical documents that should not be used as current authority.

## Rules

1. Legacy docs are not deleted.
2. Legacy docs must include a status/superseded banner.
3. Legacy docs may be used for history only.
4. Current authority lives outside `docs/legacy/**`.
5. Gemini must warn when citing legacy docs.

## Current legacy groups

```txt
docs/legacy/sync
```

## Why legacy exists

PRISMA has fast-moving docs. Moving retired docs here prevents old closures from fighting new source code like two señores arguing over whose extension cord is safer.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
