# 14_SLOT_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product
- Scope: Slot definitions, policies, hosting rules, and bounded composition behavior

---

## Purpose

This document defines the Slot System for Live Scene Composer. Slots are the bounded host regions that connect layout structure to concrete widget composition.

They are one of the most important concepts in the system because they prevent composition from collapsing into anonymous containers and uncontrolled placement.

---

## Slot System Summary

A Slot is a bounded composition region that accepts one or more widgets according to explicit policy.

Slots exist to provide:

- host semantics
- insertion rules
- capacity constraints
- bounded custom widget regions
- structure clarity
- safe replacement and composition flows

Without slots, widget placement becomes ambiguous and the system loses one of its strongest architecture anchors.

---

## Why Slots Exist

Slots solve several problems at once:

1. they create bounded composition regions
2. they connect layout structure to content placement
3. they define insertion compatibility
4. they support prefab insertion discipline
5. they provide the future host model for bounded custom widgets
6. they improve scene readability in structure view and mutation targeting

Slots are not UI decoration. They are part of the domain.

---

## Slot Responsibilities

A slot is responsible for:

- defining a host region
- identifying what kinds of widgets it accepts
- defining how many widgets it may host
- identifying whether custom widgets are allowed
- providing a stable target for insertion and replacement
- participating in layout/structure mapping

A slot is not responsible for:

- rendering concrete content by itself
- owning the whole layout tree
- replacing widget type semantics
- bypassing scene or mutation governance

---

## Slot Identity

Each slot should have a stable identity.

Expected concerns include:

- slot id
- slot name or label
- slot kind
- accepted capabilities or types
- max item count
- current widget ids
- lock state
- policies such as custom widget allowance

Stable identity matters for:

- structure view
- insertion
- mutation targeting
- compare/revert
- mapping between layout and composition

---

## Slot Kinds

The system may support multiple slot kinds such as:

- content
- media
- chart
- metric
- container
- custom

Slot kind helps express intent and constraints.
It should influence, but not wholly replace, explicit compatibility rules.

---

## Slot Acceptance Policy

A slot should express what kinds of widgets it may host.

This may be modeled through:

- accepted widget types
- accepted widget capabilities
- explicit allowlists
- capacity rules
- mode restrictions where relevant

Examples:

- a chart slot may accept chart widgets and maybe metric widgets
- a text slot may accept text-oriented widgets only
- a custom slot may allow custom widgets if policy permits

Acceptance policy is important because it keeps authoring understandable and prevents structurally incoherent scenes.

---

## Capacity and Ordering

Slots should define how many widgets they can host.

Examples:

- single-item slot
- multi-item stack-like slot
- bounded collection slot

Ordering rules matter whenever a slot can host multiple widgets.
These rules must remain explicit so reorder behavior is predictable.

---

## Slot and Layout Relationship

A slot is not the same as a layout node.

This distinction matters a lot.

### Layout node

- describes structural position in the layout tree

### Slot

- describes the host region for widget composition

A layout node may reference a slot, but they should not be fused into one anonymous concept.
This separation keeps the system flexible and structurally legible.

---

## Slot and Widget Relationship

A slot hosts widgets.
A widget belongs to a slot.

This relationship should remain explicit because it supports:

- insertion validation
- move/reparent operations
- replacement
- custom widget containment
- targeted reset and compare semantics

---

## Slot Visibility in the Product

Slots should be visible enough in the authoring experience that users can reason about structure.

Possible visibility mechanisms include:

- structure tree nodes
- canvas outlines during selection or insertion
- insertion affordances
- bounded region overlays
- slot labels in advanced structure views

A system with slots but no way to reason about them becomes confusing.

---

## Slot Editing

Slot editing should remain bounded.

Possible editable attributes include:

- label or display name
- acceptance policy
- capacity
- lock state
- visual placeholder treatment
- custom widget allowance

Slot editing should not become a side door for breaking layout or bypassing widget validation.

---

## Slots and Prefabs

Slots are one of the main things prefabs should target.

A healthy insertion flow is:

1. user selects or focuses a slot
2. system shows compatible prefabs
3. prefab is instantiated into widget instance(s)
4. slot capacity and policy are validated
5. preview and acceptance follow normal mutation rules

This is much safer than arbitrary free placement.

---

## Slots and Custom Widgets

Slots are the correct host concept for custom widgets.

A custom widget should:

- live inside an explicitly approved slot
- render inside slot bounds
- obey slot policy
- fail locally within that region

This is one of the strongest reasons the Slot System matters.

---

## Slot Anti-Patterns

The Slot System must reject:

- slots that are indistinguishable from widgets
- slots with no policy or bounded meaning
- placing widgets without a valid slot
- using layout nodes as secret slot substitutes
- creating “magic slots” that bypass validation
- custom widget placement without explicit slot approval

---

## Summary

The Slot System is the bounded host layer that connects layout to widgets. Slots define valid composition regions, acceptance policy, capacity, and future custom widget containment. They are essential to structural clarity, insertion safety, and long-term product coherence.
