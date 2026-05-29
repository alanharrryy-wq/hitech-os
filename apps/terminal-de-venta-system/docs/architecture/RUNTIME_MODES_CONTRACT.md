---
title: Runtime Modes Contract
path: docs/architecture/RUNTIME_MODES_CONTRACT.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# Runtime Modes Contract

## Runtime mode labels

| Mode | Meaning |
|---|---|
| `local_full` | Local machine, full diagnostic capability. |
| `public_redacted` | Public/tunnel/cloud-safe view with sensitive data redacted. |
| `demo` | Demonstration mode; must be clearly labeled. |
| `shadow` | Realistic validation without production mutation. |
| `planned` | Design documented, not implemented. |
| `stub_guard` | Endpoint exists but intentionally blocks work. |
| `runtime_live` | Live local service. Requires fresh verification. |

## Rules

- Public output must be sanitized.
- Demo/stub data must not masquerade as production.
- Shadow or lifecycle modes must tag generated data.
- Control Center may expose full detail only in local/full mode.
- Gemini may read sanitized evidence in v1; it must not execute runtime changes.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
