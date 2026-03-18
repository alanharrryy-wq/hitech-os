# 13_SELECTION_SURFACE_SYNC_MATRIX

## Document Status

- Status: Proposed Canonical
- Audience: Engineering, Validation, QA
- Scope: Cross-surface synchronization behavior for selection-related state

---

## Purpose

This document defines how the major authoring surfaces should respond to selection snapshot changes.

The three main surfaces are:

- Canvas
- Structure Tree
- Inspector

The goal is not to make every surface identical.
The goal is to make them **consistent with one canonical selection truth**.

---

## Sync Matrix

| Selection snapshot | Canvas | Structure Tree | Inspector |
|---|---|---|---|
| `none` | clear overlays and handles | clear active node highlight | show `empty-editor` |
| `active scene` | highlight scene shell / stage framing | focus scene root node | show scene editor |
| `active layout-node` | show layout overlays / handles | focus matching layout node | show layout-node editor |
| `active slot` | show slot boundary / occupancy framing | focus matching slot node | show slot editor |
| `active widget` | show widget overlay / handles | focus matching widget node | show widget editor |
| `stale` | remove target-specific overlays | clear or mark stale visual state | show unavailable editor with recovery message |

---

## Surface-specific notes

### Canvas

Canvas response is the most visual and should be the fastest to clear when the target becomes stale.
A stale target must not leave resize handles or widget affordances floating on screen.

### Structure Tree

The tree may preserve expansion state independently from selection.
However, active-node highlighting must still be driven by the canonical selection snapshot.

### Inspector

The inspector may preserve UI chrome such as section expansion or tab memory only when the target identity remains the same.
When target kind/ref changes, target-local UI state should reset to a safe scope.

---

## Ordering expectations

A healthy sequence for a selection change is:

1. store commits the new snapshot
2. canvas reconciles overlays
3. structure tree reconciles active node
4. inspector derives the new target and resets target-local stale UI

Exact render timing may vary by framework, but the dependency direction should stay legible.

---

## Anti-patterns

- canvas visually selecting one widget while the inspector edits another
- structure tree auto-selecting a nearby node to hide a stale target problem
- inspector showing cached widget controls after the widget disappeared
- selection logic embedded only in one surface component tree

---

## Summary

The surfaces do not need to own the same code, but they do need to obey the same selection snapshot. That is the whole point of having a shared store in the first place.
