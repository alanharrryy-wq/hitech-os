
# 24_CANVAS_VIEWMODEL_AND_OVERLAY_CONTRACT

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Canvas-facing projection rules derived from selection and scene/runtime-observed inputs

---

## Purpose

This document defines how Canvas derives visual interaction affordances from synchronized authoring state.

Canvas is the direct manipulation surface.
That does not make it domain truth.

Its viewmodel should be derived from:

- selected target identity
- scene structure facts
- runtime-observed bounds and visibility facts
- mode and capability hints
- stale or recovery status

---

## Expected Overlay Families

A healthy canvas viewmodel may include:

- focus frame
- slot occupancy frame
- layout guides
- handle descriptors
- hover preview hints
- ghost or unavailable overlays for stale diagnostics
- breadcrumb / title hints for selected target

---

## Viewmodel Guarantees

1. Overlay derivation must be pure with respect to its typed inputs.
2. Active overlays disappear when selection becomes none or stale.
3. A stale target may show unavailable diagnostics, never editable handles.
4. Overlay plans must remain target-kind aware.
5. Canvas viewmodel must not silently produce write actions.

---

## Input Categories

### Selection input

- active target or stale target
- origin and revision metadata

### Structural input

- layout path
- slot ownership path
- widget host slot
- lock / visibility hints

### Runtime-observed input

- bounds
- measured visibility
- render node identifiers when available

---

## Overlay Anti-Patterns

Reject these:

- handle visibility for stale targets
- canvas writing directly because a handle moved locally
- overlays depending on hidden React-local selected ids only
- using runtime node ids as the canonical authoring identity

---

## Summary

Canvas overlays are a projection, not authority. They must remain typed, selection-driven, structurally aware, and safe under stale or missing-target conditions.
