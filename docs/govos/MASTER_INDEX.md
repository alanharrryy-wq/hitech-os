---
doc_id: GOVOS_MASTER_INDEX
title: GOVOS Master Index
doc_type: governance
status: active
version: 1.0.0
canonical_path: docs/govos/MASTER_INDEX.md
universe: cross
owners:
  - governance-core
last_updated: 2026-02-26
depends_on:
  - docs/govos/README.md
---

# GOVOS Master Index

## 1. Purpose

Provide a deterministic index of canonical governance documents and their dependency boundaries.

## 2. Scope

Covers all governance docs in `docs/govos/` and their required report/schema/tooling artifacts.

## 3. Authority

This index defines the canonical location and interpretation order for governance content.

## 4. Terms

- Universe: one governance control plane.
- Dependency map: graph of directional governance dependencies.
- Doc manifest: deterministic catalog of all governance artifacts.

## 5. Non-Negotiables

- Every canonical doc must have a unique `doc_id`.
- Universe docs must stay universe-scoped.
- Cross-universe blending is blocked unless explicit and documented.

## 6. Anti-Patterns

- Hidden governance files outside indexed paths.
- Reordering manifest entries without deterministic sort.
- Policy changes without matching evidence outputs.

## 7. Controls

Indexed documents:

- `docs/govos/README.md`
- `docs/govos/u1_constitutional_change/U1_CONSTITUTIONAL_CHANGE.md`
- `docs/govos/u2_evidence_chain/U2_EVIDENCE_CHAIN.md`
- `docs/govos/u3_policy_plane/U3_POLICY_PLANE.md`
- `docs/govos/u4_enterprise_agents/U4_ENTERPRISE_AGENTS.md`
- `docs/govos/templates/GOVOS_DOC_TEMPLATE.md`

## 8. Procedure

1. Add or modify canonical docs in one universe at a time.
2. Update `MANIFEST.yaml` in sorted order.
3. Re-run Docs Doctor and Pester validation.

## 9. Evidence Outputs

- Manifest diff.
- Updated convergence reports.
- Test outputs from `tools/ops/tests`.

## 10. Validation Gates

- Canonical docs path check passes.
- Front-matter check passes.
- Duplicate `doc_id` check passes.

## 11. Exceptions and Escalation

If a legacy doc appears to span multiple universes, preserve it unchanged and log a cross-universe mixed warning.

## 12. Change Control

Index edits require coordinated manifest updates and deterministic graph updates in `dependency-map/GOVOS_DEPENDENCIES.dot`.
