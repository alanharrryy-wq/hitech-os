---
title: PRISMA Control Center Current State
path: docs/control-center/PRISMA_CONTROL_CENTER_CURRENT_STATE.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Control Center Current State

## Static evidence status

Control Center exists as a Python/web local control plane.

Evidence paths from inspected package:

```txt
prisma-control-center/internal/py/prisma_control_center.py
prisma-control-center/internal/py/panel_3150.py
prisma-control-center/internal/web/index.html
prisma-control-center/internal/config/services.json
```

## Port

```txt
3150
```

## Observed capabilities

- health
- local up / cloudflare up / all up
- panel
- doctor
- self-test
- export support bundle
- public redacted vs local full modes
- quality/release/license/blackbox endpoint families

## Services

Core configured services generally include:

| Surface | Port |
|---|---:|
| EIT/Web | 3110 |
| Tablet | 3120 |
| PC | 3130 |
| Mobile | 3140 |
| Chart Lab | 3000 in wrappers/lab context |
| Control Center | 3150 |

## Future fit

Control Center is the preferred future home for a read-only Gemini Evidence Reader panel, because it already understands local/full vs public/redacted boundaries.

## Not implemented here

- Data Lifecycle tab
- Gemini Copilot
- AI execution of operations

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
