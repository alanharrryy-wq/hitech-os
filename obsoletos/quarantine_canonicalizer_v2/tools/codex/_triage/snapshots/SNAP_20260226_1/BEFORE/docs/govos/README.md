---
doc_id: GOVOS_ROOT_README
title: GOVOS Canonical Governance Root
doc_type: governance
status: active
version: 1.0.0
canonical_path: docs/govos/README.md
universe: cross
owners:
  - governance-core
last_updated: 2026-02-26
depends_on:
  - docs/govos/MASTER_INDEX.md
---

# GOVOS Canonical Governance Root

## 1. Purpose

Define the canonical governance root for HITECH OS and make `docs/govos/` the execution authority for governance operations.

## 2. Scope

Applies to governance documentation, convergence metadata, schemas, and deterministic doc-health checks.

## 3. Authority

`docs/govos/` is authoritative for governance decisions. Legacy docs outside this root are preserved but read-only in governance interpretation.

## 4. Terms

- Canonical: active governance source of truth.
- Legacy: historical governance material preserved for traceability.
- Convergence: deterministic mapping from legacy docs to canonical docs.

## 5. Non-Negotiables

- Determinism over convenience.
- No silent pass.
- Additive-first changes.
- Evidence before policy acceptance.
- Explicit escalation for blockers.

## 6. Anti-Patterns

- Implicit governance by scattered docs.
- Runtime-impacting edits inside governance runs.
- Deleting legacy records.
- Ambiguous ownership or unsigned policy changes.

## 7. Controls

- Canonical manifest (`MANIFEST.yaml`) must stay sorted.
- Unique `doc_id` across canonical governance docs.
- Governance docs must include valid front matter.

## 8. Procedure

1. Draft or update canonical docs under the proper universe folder.
2. Run `tools/ops/Docs-Doctor.ps1 --check`.
3. Resolve blockers before governance acceptance.

## 9. Evidence Outputs

- `docs/govos/_reports/LEGACY_MAP.md`
- `docs/govos/_reports/CONVERGENCE_LOG.md`
- `docs/govos/_reports/FINAL_REPORT.md`

## 10. Validation Gates

- Manifest exists and is sorted.
- No duplicate `doc_id`.
- Front matter is present and parseable.
- Canonical universe docs exist.

## 11. Exceptions and Escalation

When ambiguity exists, operate in additive-only mode, preserve legacy, and log details in convergence reports.

## 12. Change Control

Any canonical governance change must update `MANIFEST.yaml` and maintain deterministic ordering.
