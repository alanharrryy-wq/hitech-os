---
title: PRISMA Master Doc Index
path: docs/PRISMA_MASTER_DOC_INDEX.md
status: CURRENT
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: This document is a governance authority document. It does not claim minute-by-minute runtime state.
---

# PRISMA Master Doc Index

This index lists the current authority documents installed by the full governance refresh.

## Global authority

| Path | Status | Purpose |
|---|---|---|
| `docs/PRISMA_CURRENT_STATE.md` | CURRENT | Human-readable current state. |
| `docs/PRISMA_CURRENT_STATE.json` | CURRENT | Machine-readable current state for tooling/AI. |
| `docs/PRISMA_DOCUMENT_PRECEDENCE_RULES.md` | CURRENT | Resolves contradictions. |
| `docs/PRISMA_DOCS_STATUS_TAGS.md` | CURRENT | Defines document status tags. |
| `docs/PRISMA_LEGACY_DOCS_INDEX.md` | CURRENT | Index of historical docs no longer authoritative. |
| `docs/PRISMA_OPERATIONAL_SAFETY_RULES.md` | CURRENT | Safety boundaries. |
| `docs/PRISMA_CANONICAL_STATUS.md` | CURRENT_WITH_GAPS | Canonical status and caveats. |

## Architecture

| Path | Status | Purpose |
|---|---|---|
| `docs/architecture/PRISMA_ARQUITECTURA_FINAL_PC_TABLET.md` | CURRENT | PC/Tablet final architecture authority. |
| `docs/architecture/PC_TABLET_OPERATIONAL_CONTRACT.md` | CURRENT | Operation boundaries. |
| `docs/architecture/RUNTIME_MODES_CONTRACT.md` | CURRENT | Runtime/data mode definitions. |

## Database and data flow

| Path | Status | Purpose |
|---|---|---|
| `docs/prisma/PRISMA_DATABASE_AUTHORITY.md` | CURRENT | Active DB authority rules. |
| `docs/prisma/PRISMA_DATA_FLOW_AND_AUTHORITY.md` | CURRENT | Data ownership and flow. |
| `docs/prisma/PRISMA_SYNC_STANDARD.md` | CURRENT | Sync standard. |

## Sync

| Path | Status | Purpose |
|---|---|---|
| `docs/sync/PC_TABLET_SYNC_CURRENT_AUTHORITY.md` | CURRENT | Current PC/Tablet sync authority. |
| `docs/sync/TABLET_TO_PC_SALES_SYNC_CURRENT_AUTHORITY.md` | CURRENT | Tablet → PC sales authority. |
| `docs/sync/PC_TO_TABLET_CATALOG_DELTA_CLOSURE_01.md` | CURRENT | PC → Tablet catalog delta. |
| `docs/sync/PRISMA_SYNC_ENDPOINTS_REAL_VS_STUBS.md` | CURRENT | Real endpoints vs stubs. |

## Governance and AI

| Path | Status | Purpose |
|---|---|---|
| `docs/governance/GOVERNANCE_PACKAGE_SCOPE_RULES.md` | CURRENT | Government package scope. |
| `docs/governance/GOVERNANCE_EXTRACTOR_SOURCE_MAP.md` | CURRENT | Extractor source map. |
| `docs/governance/GOVERNANCE_STALENESS_POLICY.md` | CURRENT | Staleness policy. |
| `docs/ai/PRISMA_GEMINI_COPILOT_SCOPE_V1.md` | PLANNED | Gemini scope v1. |
| `docs/ai/PRISMA_AI_EVIDENCE_INGESTION_RULES.md` | PLANNED | AI evidence ingestion rules. |

## Productization and design AI docs

| Path | Status | Purpose |
|---|---|---|
| `docs/productization/PRISMA_AI_READY_SUPPORT_CONTRACT.md` | CURRENT | AI-ready support contract. |
| `docs/productization/PRISMA_SUPPORT_AI_FUTURE_PLAYBOOK.md` | CURRENT | Future AI support playbook. |
| `docs/design/PRISMA_SHOW_POS_AI_DOCTOR_OFFLINE_00Y.md` | CURRENT | Offline AI Doctor design boundary. |

## Control Center and planning

| Path | Status | Purpose |
|---|---|---|
| `docs/control-center/PRISMA_CONTROL_CENTER_CURRENT_STATE.md` | CURRENT | Control Center state. |
| `docs/planning/PRISMA_DATA_LIFECYCLE_DECISION.md` | PLANNED | Data Lifecycle decision. |

## Legacy

| Path | Status | Purpose |
|---|---|---|
| `docs/legacy/README.md` | CURRENT | Legacy folder policy. |
| `docs/legacy/sync/PRISMA_SYNC_CLOSURE_BUNDLE_20260521.md` | LEGACY | Historical sync closure. |
| `docs/legacy/sync/PRISMA_SYNC_CLOSURE_PATCH_20260518.md` | LEGACY | Historical sync patch. |


## Authority rules used by this document

1. Runtime resolver/configuration wins over filenames that merely look canonical.
2. `DATABASE_URL` and the application resolver win over discovered SQLite files.
3. Implemented endpoints win over older closure notes, but stubs must remain documented as stubs.
4. `PRISMA_CURRENT_STATE.md` and `PRISMA_CURRENT_STATE.json` are the first documents a future AI assistant should read.
5. Historical docs are preserved in `docs/legacy/**` and must not be treated as current operational authority.
6. This package excludes live repo execution; any “current” statement means current by static evidence as of the package inputs.
