---
title: Governance Extractor Source Map
path: docs/governance/GOVERNANCE_EXTRACTOR_SOURCE_MAP.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# Governance Extractor Source Map

## Required include map

```txt
docs/*.md
docs/*.json
docs/prisma/**/*.md
docs/sync/**/*.md
docs/architecture/**/*.md
docs/governance/**/*.md
docs/ai/**/*.md
docs/control-center/**/*.md
docs/productization/PRISMA_AI_READY_SUPPORT_CONTRACT.md
docs/productization/PRISMA_SUPPORT_AI_FUTURE_PLAYBOOK.md
docs/design/PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y.md
shared/tri-db/status.latest.json
products/pc/app/src/server/prisma/client.ts
products/pc/app/app/api/sync/export/catalog-delta/route.ts
products/pc/app/src/server/services/catalog-delta-export.service.ts
products/tablet/app/app/api/pos/sync/pull/route.ts
products/tablet/app/src/server/sync/catalog-pull.ts
prisma-control-center/internal/config/*.json
prisma-control-center/internal/py/*.py
```

## Exclusions

Do not include secrets or heavy runtime artifacts by default:

```txt
.env*
*.db
*.sqlite
*.sqlite3
node_modules/
.next/
dist/
build/
out/
*.zip
```

If DB metadata is required, include a sanitized report, not the DB itself.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
