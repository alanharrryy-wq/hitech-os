# 15_LAYOUT_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product, Design
- Scope: Layout structure, spatial organization, and layout editing behavior

---

## Purpose

This document defines the Layout System for Live Scene Composer. Layout is the structured spatial organization of the scene. It answers how regions are arranged, how composition is positioned, and how spatial structure is represented independently from content.

Layout must remain a first-class system because users need to author structure, not just content appearance.

---

## Layout System Summary

The Layout System is responsible for:

- structural composition
- region hierarchy
- ordering
- placement and sizing
- alignment and spatial relationships
- layout node tree management
- slot references within structure

The Layout System is not the same thing as widgets, slots, or scene metadata, even though it interacts with all of them.

---

## Why Layout Exists as Its Own System

Without an explicit Layout System, products tend to collapse into a flat set of components with ad hoc positioning rules. That quickly leads to:

- inconsistent structure
- fragile drag/drop behavior
- confused ownership
- unclear mutation semantics
- hard-to-maintain responsive behavior later
- hidden layout logic inside widgets or panels

Layout deserves its own model because spatial structure is a real part of authoring.

---

## Core Layout Concepts

The Layout System should represent structure through layout nodes.
Common conceptual node types may include:

- root
- stack
- grid
- container
- slot reference

Exact node types may evolve, but the system must preserve the distinction between structural nodes and content nodes.

---

## Responsibilities of Layout Nodes

A layout node may be responsible for:

- parent/child structural relationships
- ordering among children
- sizing constraints
- alignment rules
- spacing rules
- reference to a slot where content may appear
- layout-level visual treatment where appropriate

A layout node should not automatically become a widget or slot.
Those concepts remain distinct.

---

## Layout and Scene Relationship

A scene has a root layout.
The layout defines the structural organization of the scene.

This means:

- layout changes affect structure
- layout changes may change slot placement and widget presentation
- layout does not by itself define content semantics

---

## Layout and Slot Relationship

A layout node may reference a slot.
That reference tells the system where a host region exists within the structural arrangement.

This relationship is powerful because it lets the system separate:

- spatial structure
from
- content hosting

That separation improves clarity and future extensibility.

---

## Layout Editing Requirements

The Layout System should support meaningful authoring behavior such as:

- move
- resize
- reorder
- align
- snap
- grid-aware placement
- spacing adjustments
- structural reorganization

These should feel visual and immediate, while still producing governed mutations.

---

## Drag, Resize, and Reorder

These are central layout operations and should be treated seriously.

### Drag

Drag should move eligible structural targets in ways consistent with layout rules.

### Resize

Resize should alter size-related constraints within valid bounds.

### Reorder

Reorder should preserve structural clarity and not become arbitrary DOM shuffling.

All three should remain consistent with mutation policies, draft workflows, and compare/revert behavior.

---

## Guides, Grid, and Snapping

A strong layout authoring experience often needs:

- alignment guides
- snapping
- visible bounds
- optional grid systems
- insertion hints

These are not cosmetic luxuries. They are part of what makes layout editing precise instead of frustrating.

---

## Layout Mutations

Typical layout mutations may include:

- move layout node
- resize layout node
- reorder layout node
- change layout constraints
- reparent a layout node within valid rules

These mutations should be typed and routed through approved mutation flows rather than enacted as hidden component-local side effects.

---

## Layout Constraints

The Layout System should support explicit constraints where needed.

Potential constraints include:

- minimum/maximum dimensions
- stacking rules
- grid placement rules
- allowed child types
- slot-ref constraints
- mode restrictions for certain operations

The system does not need to solve every possible responsive rule on day one, but it should leave room for disciplined expansion.

---

## Layout Visibility in the Product

Users need enough visibility into layout structure to reason about it.

Helpful surfaces include:

- structure tree
- canvas outlines
- parent/child highlighting
- drop previews
- reordering markers
- selected bounds

A layout system hidden behind invisible assumptions becomes hard to trust.

---

## Layout and Widgets

Widgets may appear visually central to the user, but they do not replace layout structure.
A chart widget inside a slot inside a structural container is not itself the layout tree.

This distinction is essential to prevent a product where content blocks accidentally become the only structural truth.

---

## Layout and Container Widgets

Container widgets may provide local visual grouping, but should not erase the primary layout model.
Where container widgets exist, their relationship to layout must remain explicit and bounded.

The danger is letting container widgets smuggle in a second unofficial layout engine.

---

## Layout Anti-Patterns

The Layout System must reject:

- treating widgets as the only structure
- storing layout truth purely in transient UI state
- using DOM order as the only layout model
- confusing slot definitions with structural nodes
- “temporary” direct manipulations that never formalize into governed mutations
- hidden layout logic inside unrelated modules

---

## Summary

The Layout System is the structural spine of scene composition. It defines how regions are arranged, how slot references are placed, and how users manipulate spatial structure. It must remain distinct from widgets and slots, visible enough to reason about, and governed through typed mutation flows rather than informal UI side effects.
