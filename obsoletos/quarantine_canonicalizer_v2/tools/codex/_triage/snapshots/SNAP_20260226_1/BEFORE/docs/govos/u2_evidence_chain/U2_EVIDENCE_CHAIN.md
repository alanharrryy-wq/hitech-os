---
doc_id: GOVOS_U2_EVIDENCE_CHAIN
title: U2 Evidence Chain Governance
doc_type: governance
status: active
version: 1.0.0
canonical_path: docs/govos/u2_evidence_chain/U2_EVIDENCE_CHAIN.md
universe: u2_evidence_chain
owners:
  - governance-core
last_updated: 2026-02-26
depends_on:
  - docs/govos/MASTER_INDEX.md
  - docs/govos/u3_policy_plane/U3_POLICY_PLANE.md
---

# U2 Evidence Chain Governance

## 1. Purpose

Define deterministic evidence generation, verification, and retention requirements for governance execution.

## 2. Scope

Covers provenance, attestations, status artifacts, debt logs, and blocker outputs used for governance decisions.

## 3. Authority

No governance decision is accepted without matching evidence artifacts.

## 4. Terms

- Evidence output: deterministic artifact proving an operation or decision.
- Provenance chain: ordered links from change intent to validation outcome.

## 5. Non-Negotiables

- Verification required.
- No silent pass.
- Evidence outputs are required for governance transitions.
- Provenance and signing policy references must remain explicit.

## 6. Anti-Patterns

- Trusting undocumented manual checks.
- Missing or mutable evidence records.
- Passing governance gates with partial artifacts.

## 7. Controls

- Schemas under `docs/govos/schemas` define minimum evidence contract.
- Deterministic file ordering for generated reports.
- Stable output formatting for machine checks.

## 8. Procedure

1. Generate evidence outputs for each governance run.
2. Validate outputs against canonical schemas.
3. Persist results under deterministic report paths.

## 9. Evidence Outputs

- `STATUS_SCHEMA.json`
- `BLOCKERS_SCHEMA.json`
- `DEBT_SCHEMA.json`
- `_reports/FINAL_REPORT.md`

## 10. Validation Gates

- Schema presence and parseability.
- Deterministic ordering of indexed docs.
- Explicit blocker and debt capture.

## 11. Exceptions and Escalation

If evidence is incomplete, mark BLOCKED and capture missing artifacts in final report.

## 12. Change Control

Evidence schema changes require version updates and manifest updates.
