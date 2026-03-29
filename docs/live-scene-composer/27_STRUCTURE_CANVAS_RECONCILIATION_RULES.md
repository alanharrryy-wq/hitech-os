
# 27_STRUCTURE_CANVAS_RECONCILIATION_RULES

## Document Status

- Status: Proposed Canonical
- Audience: Engineering, Validation
- Scope: Reconciliation and stale-recovery behavior when the selected target no longer maps cleanly across revisions or surfaces

---

## Purpose

This document defines what should happen when the selected target cannot be resolved safely after scene refresh, entity removal, host-slot change, or structural reorder.

---

## Reconciliation Principles

1. Missing target does not justify silent retargeting.
2. Tree and Canvas must agree on stale state.
3. Mutation entrypoints must become unavailable when the selected target is stale.
4. Recovery suggestions must be explicit and typed.
5. Diagnostics should preserve the last-known target key for debugging.

---

## Common stale cases

- widget removed from scene
- slot no longer exists
- layout node id replaced by migration/refactor
- widget moved to a new host slot and old selected ref is no longer valid
- revision token changed and the selected ref can no longer be resolved

---

## Recovery Suggestions

Possible safe suggestions include:

- clear selection
- reselect parent slot
- reselect nearest surviving layout ancestor
- reselect scene root

But any such action should remain suggested, not silently enforced.

---

## Summary

Reconciliation is where sloppy products fake continuity and lose trust. The correct rule is explicit stale state first, explicit recovery second.
