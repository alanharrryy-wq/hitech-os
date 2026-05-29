---
title: Governance Package Scope Rules
path: docs/governance/GOVERNANCE_PACKAGE_SCOPE_RULES.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# Governance Package Scope Rules

## Problem solved

Previous Government packages were useful but incomplete as a single state authority because they could leave root docs and source authority files unmapped.

## Required scope

A Government package must include:

- root docs: `docs/*.md`, `docs/*.json`
- current authority docs under `docs/prisma`, `docs/sync`, `docs/architecture`, `docs/governance`, `docs/ai`, `docs/control-center`
- runtime resolver source files named by current authority docs
- `shared/tri-db/status.latest.json` if present
- Control Center service config files
- staleness report
- unmapped file list
- legacy doc index

## Required metadata

Every package must emit:

```json
{
  "stale_analysis_enabled": true,
  "docs_root_included": true,
  "authority_sources_included": true,
  "legacy_index_included": true,
  "unmapped_count": 0
}
```

`unmapped_count` may be nonzero, but then the report must explain why files are intentionally outside scope.

## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
