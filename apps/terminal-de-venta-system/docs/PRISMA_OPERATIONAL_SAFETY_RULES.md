---
title: PRISMA Operational Safety Rules
path: docs/PRISMA_OPERATIONAL_SAFETY_RULES.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Operational Safety Rules

This document defines safety boundaries for docs, tooling, AI, seed/reset, Clear, sync, backups and public output.

## Non-negotiable rules

1. Production data must never be mutated by test tooling unless an explicit production-safe workflow exists.
2. Any seed/reset/clear action must be backed by provenance tags, backup, evidence and rollback strategy.
3. AI v1 is read-only. It can explain and suggest; it cannot mutate.
4. Secrets, tokens, `.env`, raw DBs, customer PII and credentials must not be uploaded to external AI providers.
5. Public bundles must run no-leak scanning before deploy or sharing.
6. Tablet must preserve offline sale capability and must not require PC, Mobile, Chart Lab or AI to sell.
7. PC may govern when present, but it cannot retroactively corrupt Tablet evidence.
8. Chart Lab public output must remain public-safe.
9. Control Center public mode must be redacted.
10. Legacy docs cannot override current docs.

## Backup rule

For SQLite databases that may be live, use a consistent backup method. Do not assume a raw file copy is safe during writes.

## AI rule

Gemini Copilot may read sanitized docs/reports and cite sources. It must not receive raw secrets or operate system commands. No “robot with admin keys” carnival, gracias.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
