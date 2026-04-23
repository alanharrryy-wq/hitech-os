# GOLDEN SPEC APPROVAL RECORD V1
Project: `apps/external_interaction_template`  
Record version: `v1.0`  
Status: `APPROVED`  
Approval date: `2026-04-13`

---

## 1) Approved artifacts

The following artifacts are approved and effective:

1. `docs/architecture/GOLDEN_SPEC_UI_SHELL_V1.md`
2. `docs/architecture/GOLDEN_SPEC_ACCEPTANCE_MATRIX_V1.md`

---

## 2) Approval scope

Approval covers:

1. Persistent sidebar-first shell language.
2. Ultra-minimal chrome bar behavior and constraints.
3. Unified route grammar for inbox/flow/record/sync families.
4. Canonical theme personas:
   - `aurora` (Nebula Midnight)
   - `solstice` (Pearl Mist)
   - `neon` (Nova Rose)
5. Motion/accessibility/performance constraints defined in golden spec.

Approval does not cover:

1. Business logic redesign.
2. API or schema contract changes.
3. Route path changes.

---

## 3) Decision statement

Decision:

1. Golden spec is now repository-level source of truth for visual and functional shell behavior.
2. Any UI change affecting shell, route grammar, theme persona, motion, or accessibility must be reviewed against the acceptance matrix.
3. Unapproved deviations are regressions.

---

## 4) Enforcement policy

### 4.1 Required before merge (for affected UI changes)

1. Route/theme matrix updated for impacted slices.
2. Evidence notes attached for any FAIL and fix cycle.
3. Explicit statement confirming compliance with `GOLDEN_SPEC_UI_SHELL_V1`.

### 4.2 Rejection triggers

Reject the change if any condition is true:

1. Sidebar is no longer persistent on desktop.
2. Chrome bar exceeds minimal contract.
3. Route reverts to hero-first composition.
4. Theme persona drifts from canonical definitions.
5. Motion harms readability or ignores reduced-motion behavior.

---

## 5) Change management process for spec updates

When changing this spec set:

1. Create new versioned record (`V2`, `V3`, etc.).
2. Document rationale and intended impact.
3. Update matrix criteria accordingly.
4. Mark previous version as superseded only after explicit approval.

---

## 6) Current approver record

Approved by:

1. Operator request in active implementation thread.
2. Codex integration action under repository governance.

Notes:

1. This approval record exists to lock execution discipline and prevent layout/theme drift.

