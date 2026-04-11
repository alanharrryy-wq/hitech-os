---
doc_id: GOVOS_U1_CONSTITUTIONAL_CHANGE
title: U1 Constitutional Change Governance
doc_type: governance
status: active
version: 1.0.0
canonical_path: docs/govos/u1_constitutional_change/U1_CONSTITUTIONAL_CHANGE.md
universe: u1_constitutional_change
owners:
  - governance-core
last_updated: 2026-02-26
depends_on:
  - docs/govos/MASTER_INDEX.md
  - docs/govos/u3_policy_plane/U3_POLICY_PLANE.md
---

# U1 Constitutional Change Governance

## 1. Purpose

Control constitutional-level governance edits that alter repository-wide operating rules.

## 2. Scope

Applies to constitutional clauses, root authority rules, and governance invariants used by all universes.

## 3. Authority

U1 is the highest governance layer. Lower universes cannot weaken U1 controls.

## 4. Terms

- Constitutional change: modification that changes normative governance authority.
- Ratification set: mandatory evidence and approvals for acceptance.

## 5. Non-Negotiables

- No weakening of determinism guarantees.
- No removal of evidence requirements.
- No silent policy downgrade.
- Explicit rollback path for every change.

## 6. Anti-Patterns

- Backdoor constitutional edits in unrelated docs.
- Retroactive authority changes without migration notes.
- Mixed policy and runtime edits in one approval step.

## 7. Controls

- Required front matter with unique `doc_id`.
- Mandatory dependency declaration to policy-plane enforcement.
- Compatibility statement for downstream universes.

## 8. Procedure

1. Draft constitutional proposal in canonical path.
2. Link impacted universes and controls.
3. Produce deterministic review notes and change rationale.
4. Update manifest and dependency graph.

## 9. Evidence Outputs

- Constitutional change rationale.
- Compatibility statement.
- Updated convergence and final reports.

## 10. Validation Gates

- No duplicate `doc_id`.
- 12-section structure present.
- Dependencies resolve to existing canonical docs.

## 11. Exceptions and Escalation

Emergency exceptions require explicit blocker log entry and follow-up ratification.

## 12. Change Control

Version increments are required for accepted constitutional changes.
