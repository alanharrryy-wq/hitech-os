---
title: PRISMA AI Evidence Ingestion Rules
path: docs/ai/PRISMA_AI_EVIDENCE_INGESTION_RULES.md
status: PLANNED
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA AI Evidence Ingestion Rules

## Allowed by default

```txt
docs/**/*.md
docs/**/*.json
sanitized support bundles
sanitized logs
manifest files
status summaries
no-leak reports
health reports
staleness reports
```

## Blocked by default

```txt
.env*
API keys
tokens
raw DBs
customer PII
passwords
private certs
unredacted logs
payment data
```

## Sanitization rules

| Sensitive item | Replacement |
|---|---|
| local absolute path | `PRISMA_LOCAL_PATH_REDACTED` if public/external |
| token/key | `SECRET_REDACTED` |
| raw customer identifier | `CUSTOMER_REDACTED` when not required |
| raw DB | never upload; use sanitized metadata/report |

## Gemini source priority

1. Current-state docs
2. Current authority docs
3. Sanitized evidence reports
4. Historical docs with status warning
5. Legacy docs only for history

## Output requirement

AI-generated diagnostics must include:

- claim
- confidence label
- source path
- whether live verification is required

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
