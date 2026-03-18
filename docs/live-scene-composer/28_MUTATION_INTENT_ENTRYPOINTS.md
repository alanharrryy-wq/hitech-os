
# 28_MUTATION_INTENT_ENTRYPOINTS

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering
- Scope: Bridge-safe mutation-intent request builders derived from synchronized selected targets

---

## Purpose

This document defines how synchronized selection can expose mutation-intent entrypoints without bypassing the mutation boundary.

The key move is simple:

- selection enables intent availability
- intent builders create typed requests
- `runtime-mutation-bridge` remains the enforcement boundary for any write-capable action

---

## Allowed early entrypoints

- focus selected entity
- reset selected entity
- move selected layout node
- resize selected layout node
- insert widget into selected slot
- update selected widget props
- update selected widget style
- remove selected widget

---

## Prohibited patterns

- canvas handle directly mutating runtime-facing state
- tree action silently mutating draft without an intent record
- entrypoints built from raw DOM nodes or anonymous local ids

---

## Summary

This seam is not bridge replacement. It is the typed on-ramp from synchronized authoring focus into governed mutation requests.
