
# 22_STRUCTURE_TREE_CANVAS_SYNC_CONTRACT

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Coordinated behavior contract for Structure Tree and Canvas over the Selection Store seam

---

## Purpose

This document defines how **Structure Tree** and **Canvas** must synchronize authoring focus in Live Scene Composer.

The goal is not to make the two surfaces identical.
The goal is to ensure they operate from the same selection truth, the same structural interpretation, and the same stale/recovery semantics.

Without this contract, the product tends to rot into one of these patterns:

- tree highlight says one thing while canvas overlays say another
- canvas hit-testing becomes a hidden authority tier
- structure tree auto-recovers selection in ways that silently retarget editing
- keyboard navigation in tree drifts away from pointer selection on canvas
- mutation entrypoints depend on whichever surface was touched last instead of typed selected target data

---

## Core Principle

Structure Tree and Canvas are **sibling authoring surfaces**, not rival state owners.

They must each:

- read from the same selection truth
- derive their own presentation instructions from explicit typed inputs
- report user intent through typed surface events
- respect stale state and recovery rules
- avoid direct runtime writes

---

## Ownership Model

### Selection Store owns

- current selection status
- active or stale target identity
- revision token associated with the target
- transition metadata

### Structure Tree owns

- hierarchical projection of authoring structure
- expansion state
- keyboard focus state
- tree-specific presentation state

### Canvas owns

- visual interaction overlays
- pointer hit mapping
- focus frames and handles
- visual affordance state

### Surface Coordinator owns

- normalization of surface events
- derivation of synchronized surface instructions
- stale/recovery broadcast behavior
- diagnostics records for synchronization decisions

---

## Required Guarantees

1. There is one canonical active selection at a time.
2. Structure Tree must not silently invent a new target when the selected node disappears.
3. Canvas overlays must disappear immediately when selection becomes stale.
4. Tree expansion state may survive selection changes, but active-node state must remain synchronized.
5. Pointer hit results must be normalized into typed entity refs before they can affect selection.
6. Keyboard navigation must operate on tree projection, not raw DOM ordering.
7. Surface-derived mutation entrypoints must use explicit selected target refs, not implicit local component memory.

---

## Synchronization States

### None

No current target.
Expected behavior:

- tree clears active highlight
- canvas clears overlays and handles
- inspector shows empty state

### Active

A valid selected target exists in the current revision.
Expected behavior:

- tree highlights matching structural node
- canvas highlights matching visual entity or scene frame
- inspector renders contextual editor derived from the selected target

### Stale

The last known target no longer matches the current revision or can no longer be resolved safely.
Expected behavior:

- tree clears active highlight but may show stale ghost marker in diagnostics mode
- canvas removes editable affordances
- mutation entrypoints become unavailable
- recovery suggestions may be shown, but not auto-applied as silent retargeting

---

## Allowed Event Sources

- tree node click or keyboard confirm
- tree navigation request
- canvas pointer hit selection
- canvas clear-background request
- system revision refresh
- entity removed or moved event
- explicit recovery action

Opaque raw UI events must be translated before entering the coordination seam.

---

## Summary

Structure Tree and Canvas are coordinated readers and requesters around one selection seam. Their projections may differ visually, but their authoring focus truth must remain synchronized, typed, explicit, and recoverable.
