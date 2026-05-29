---
title: PRISMA AI Ready Support Contract
path: docs/productization/PRISMA_AI_READY_SUPPORT_CONTRACT.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA AI-Ready Support Contract

## Purpose

Prepare PRISMA support, diagnostics and evidence so a future AI assistant can help without becoming a production menace.

## Supported AI modes

| Mode | Meaning | Current allowed? |
|---|---|---|
| `read_only` | AI reads and explains. | Yes. |
| `suggest_actions` | AI recommends next steps. | Yes. |
| `draft_response` | AI drafts support copy. | Yes. |
| `execute_approved_actions` | AI executes after explicit approval. | Not v1. |

## Allowed context

- version
- plan/license tier labels, not secrets
- sanitized errors
- health status
- sync state
- outbox state
- support bundle metadata
- KPIs aggregated enough for support
- current-state docs

## Forbidden context

- passwords
- tokens
- private keys
- raw DBs
- unnecessary customer PII
- payment data
- arbitrary shell command output with secrets

## Support contract

AI may answer “what happened, why it matters, what to inspect next.” It may not decide destructive operations.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
