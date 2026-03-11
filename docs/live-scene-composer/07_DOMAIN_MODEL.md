# 07_DOMAIN_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product, QA
- Scope: Core authoring domain entities and their relationships

---

## Purpose

This document defines the minimum durable domain model for Live Scene Composer. It exists so the system can grow on top of named concepts rather than ad hoc UI state and informal assumptions.

The domain model is the backbone of the product.
If the domain is vague, every implementation will invent its own truth.

---

## Domain Model Summary

The core model is:

**Scene -> Layout -> Slots -> Widgets**

Supporting entities include:

- Prefab
- Selection
- Inspector Target
- Draft
- Baseline
- Mutation
- Mode
- Snapshot
- Custom Widget Spec

These entities are related but distinct.
They must not be merged casually.

---

## Entity: Scene

### Definition

A Scene is the top-level editable composition unit.

### Core responsibilities

- identifies the composition as a whole
- owns top-level metadata
- references the root layout
- anchors slots and widget instances
- provides the main authoring target context
- participates in baseline and draft workflows

### Typical properties

- scene id
- display name
- version / revision
- root layout reference
- theme or visual context reference
- metadata
- current draft association

### Relationships

- a Scene has one root Layout
- a Scene contains many Slots
- a Scene contains many Widget instances
- a Scene may reference baseline and draft states

---

## Entity: Layout

### Definition

A Layout is the structured spatial organization of the scene.

### Core responsibilities

- arranges regions
- determines hierarchy and placement
- contains structural nodes
- references slot positions where content can live

### Notes

Layout is structural, not semantic content.
It says where things go and how they relate spatially.

### Relationships

- a Scene has one root Layout
- a Layout contains layout nodes
- some layout nodes may reference Slots
- layout changes affect structure, not necessarily widget identity

---

## Entity: Layout Node

### Definition

A Layout Node is a structural unit within a layout tree.

### Core responsibilities

- represent containers, stacks, grids, roots, slot references, or structural groupings
- describe hierarchy
- participate in reordering and resizing
- expose layout-level style or constraints where appropriate

### Relationships

- Layout Nodes form a tree
- a Layout Node may reference one Slot
- a Layout Node may contain child Layout Nodes

---

## Entity: Slot

### Definition

A Slot is a bounded host region that accepts one or more widgets according to policy.

### Core responsibilities

- define a valid host region
- express compatibility rules
- limit capacity
- bound visual placement for hosted widgets
- provide the composition seam for prefab insertion and future custom widgets

### Common slot kinds

- content
- chart
- media
- container
- metric
- custom

### Relationships

- a Scene contains many Slots
- a Layout Node may reference a Slot
- a Slot contains one or more Widget instances
- a Slot may declare whether custom widgets are allowed

---

## Entity: Widget

### Definition

A Widget is a concrete renderable composition unit hosted in a Slot.

### Core responsibilities

- render a specific content or visual block
- own widget-level props
- own widget-level styles
- participate in preview and runtime binding
- expose capabilities by widget type

### Common widget types

- text
- rich text
- image
- KPI
- chart
- table
- container
- custom widget

### Relationships

- a Widget belongs to one Slot at a time
- a Widget may have originated from a Prefab
- a Widget may have runtime binding metadata
- a Widget may have visibility and lock state

---

## Entity: Prefab

### Definition

A Prefab is a reusable composition template used to create widget instances or widget groupings.

### Core responsibilities

- encode reusable starting patterns
- speed authoring
- enforce compatible insertion targets
- supply default props and style

### Relationships

- a Prefab may instantiate one or more Widgets
- a Prefab declares slot compatibility
- a Prefab is not itself the live instance inside the scene

---

## Entity: Selection

### Definition

Selection identifies the active authoring target.

### Core responsibilities

- represent what the user is currently editing
- drive inspector state
- drive canvas interaction overlays
- synchronize authoring focus across surfaces

### Possible targets

- Scene
- Layout Node
- Slot
- Widget

### Notes

Selection is transient interaction state, but highly important to product behavior.

---

## Entity: Inspector Target

### Definition

An Inspector Target is the interpreted editing context derived from the current selection.

### Why this matters

Selection says what is selected.
Inspector Target says what editing surface should be shown and which properties are relevant.

This distinction is useful because not every selected entity should expose the same editing contract.

---

## Entity: Draft

### Definition

A Draft is the current mutable working state under authoring.

### Core responsibilities

- hold uncommitted changes
- support preview workflows
- remain comparable to baseline
- allow discard and reset semantics

### Relationships

- a Scene may have an active Draft
- mutations often target Draft state first
- a Draft may eventually be committed

---

## Entity: Baseline

### Definition

Baseline is the previously accepted reference state.

### Core responsibilities

- serve as a comparison target
- support discard semantics
- provide user trust
- distinguish accepted state from current experimentation

---

## Entity: Snapshot

### Definition

A Snapshot is a named or recorded state capture of scene composition at a given moment.

### Role

Snapshots are not required to be fully mature in the earliest MVP, but the concept matters because compare, recovery, and historical confidence are easier when the model anticipates snapshots rather than denying them.

---

## Entity: Mutation

### Definition

A Mutation is a typed request to change composition state.

### Core responsibilities

- identify source and target
- describe intended change
- encode scope such as preview vs commit
- support validation
- support auditing and testing

### Relationships

- a Mutation may target Scene, Layout, Slot, Widget, or Draft semantics
- write-capable mutations affecting runtime-facing state must go through runtime-mutation-bridge

---

## Entity: Mode

### Definition

Mode describes the operational safety mode of authoring.

### Expected modes

- Safe Mode
- Advanced Mode

### Purpose

Mode influences what mutations are allowed and how much power is exposed to the user.

---

## Entity: Custom Widget Spec

### Definition

A Custom Widget Spec defines the bounded capabilities and execution constraints of a custom widget.

### Responsibilities

- identify the widget package/spec
- declare allowed capabilities
- define execution isolation assumptions
- declare API surface expectations

### Relationship

- a Custom Widget Spec may instantiate a custom Widget in an approved Slot
- its execution remains bounded and governed

---

## Critical Relationships

### Scene to Layout

A Scene has one top-level Layout that defines its structural organization.

### Layout to Slot

Layout determines where Slot references appear within the structural composition.

### Slot to Widget

Slots host Widgets according to compatibility and policy rules.

### Prefab to Widget

Prefabs provide reusable starting definitions that instantiate Widgets.

### Selection to Inspector

Selection determines the current Inspector Target.

### Mutation to Draft / Baseline

Mutations affect Draft or preview state and may later become accepted relative to Baseline.

---

## Relationship Rules

1. A Slot is not a Widget.
2. A Layout Node is not a Slot.
3. A Prefab is not a live Widget instance.
4. Selection is not the same thing as domain truth.
5. Draft is not the same thing as Baseline.
6. Mutation intent is not the same thing as applied runtime state.
7. The bridge is not the same thing as the scene model.

These distinctions must remain visible in both code and product language.

---

## Domain Anti-Patterns

The following anti-patterns must be rejected:

- treating the scene as “just panels”
- flattening layout and slot into one anonymous thing
- letting widgets silently become layout owners
- using prefabs as mutable live state containers
- hiding draft/baseline differences
- inventing authoring behavior from selected DOM nodes alone
- storing domain truth only in UI component state

---

## Summary

The Live Scene Composer domain model is intentionally structured: Scene, Layout, Slots, Widgets, Prefabs, Draft, Baseline, Mutation, and related supporting concepts. These are not semantic luxuries; they are the minimum domain anchors required to keep the product coherent, governable, and extensible.
