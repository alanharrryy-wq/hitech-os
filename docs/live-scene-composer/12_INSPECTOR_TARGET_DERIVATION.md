# 12_INSPECTOR_TARGET_DERIVATION

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Deterministic derivation rules from SelectionState to InspectorTarget

---

## Purpose

This document defines how `InspectorTarget` must be derived from the Selection Store snapshot and bounded capability context.

The key rule is simple:

**InspectorTarget is derived, not independently authored.**

That means the inspector must not become a parallel source of target truth.

---

## Inputs to Derivation

The derivation function may read:

1. current `SelectionState`
2. bounded capability context for the selected entity kind/ref
3. current mode (`safe` or `advanced`) when needed for capability narrowing
4. optional presentation metadata that does not redefine identity

It may not read arbitrary local panel state to decide what entity is selected.

---

## Capability Context Shape

A bounded capability context should answer questions such as:

- is the target editable?
- is it removable?
- is it resettable?
- can it expose style groups?
- can it expose props groups?
- are there warnings or blockers?
- is the target unresolved or policy-limited?

The capability context should be deliberately smaller than the full scene model.

---

## Derivation Matrix

### Scene selection

Produces:

- `scene-editor`
- scene-level appearance and metadata groups
- actions like `reset-scene-look` when allowed

Must not expose:

- widget-only groups
- slot-only policy editors
- layout-node-only structural controls

### Layout Node selection

Produces:

- `layout-node-editor`
- structure / spacing / arrangement groups
- reorder and resize actions only when capability context allows them

### Slot selection

Produces:

- `slot-editor`
- host policy / acceptance / occupancy framing
- insertion affordances only when slot policy allows them

### Widget selection

Produces:

- `widget-editor`
- content / style / visibility / binding groups as appropriate
- removal and reset actions only when capability context allows them

### None selection

Produces:

- `empty-editor`
- zero target-specific property groups
- zero target actions

### Stale selection

Produces:

- `unavailable-editor`
- no target-specific mutation affordances
- visible recovery / invalidation messaging

---

## Property Group Rules

Property groups should be named and bounded.
Suggested groups include:

- `scene-appearance`
- `scene-metadata`
- `layout-structure`
- `layout-spacing`
- `layout-style`
- `slot-policy`
- `slot-occupancy`
- `slot-compatibility`
- `widget-content`
- `widget-style`
- `widget-visibility`
- `widget-binding`

The inspector must never expose property groups from a different target kind just because the UI layout makes that convenient.

---

## Action Rules

Actions shown in the inspector are advisory affordances, not authority.

Even when an action is visible:

- mutation intent must still carry an explicit typed target
- mutation policy still routes through the proper bridge / client boundary
- capability context should be treated as a narrowing hint, not a replacement for governance

---

## Determinism Rule

Given the same:

- selection snapshot
- capability context
- mode

The derivation must produce the same `InspectorTarget` every time.

If it does not, the inspector is reading hidden state and the architecture is drifting.

---

## Summary

InspectorTarget derivation is where the product decides how to present the selected thing, not what the selected thing is. That distinction is what keeps selection, inspector behavior, and mutation composition legible and testable.
