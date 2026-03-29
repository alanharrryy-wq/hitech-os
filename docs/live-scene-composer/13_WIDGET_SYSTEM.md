# 13_WIDGET_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product, Design
- Scope: Widget definition, lifecycle, capabilities, and authoring behavior

---

## Purpose

This document defines the Widget System for Live Scene Composer. Widgets are the concrete renderable units users see and manipulate inside slots. The system exists to make widget behavior structured, composable, and governable.

Widgets are one of the most visible parts of the product, so ambiguity here quickly becomes product confusion.

---

## Widget System Summary

A Widget is a renderable composition unit hosted inside a Slot.
Widgets are not layout owners, not scenes, and not mutation authorities.
They are concrete content or visual blocks with type-specific behavior, props, style, and runtime binding context.

The Widget System should support:

- clear widget identity
- predictable placement in slots
- widget-type capabilities
- widget props and style separation
- prefab-origin support
- safe editing through inspector and mutation flows
- future bounded custom widget support

---

## Widget Responsibilities

A Widget is responsible for:

- representing a concrete visual/content block
- rendering according to widget type and configuration
- owning widget-level props
- owning widget-level style data
- exposing widget-type capabilities to the authoring system
- participating in preview and selection

A Widget is not responsible for:

- defining scene-wide structure
- owning layout tree logic
- bypassing mutation governance
- operating as unrestricted code execution

---

## Widget Identity

Each widget should have a stable identity.

Expected identity concerns include:

- widget id
- widget type
- owning slot id
- optional originating prefab id
- optional runtime binding info
- visibility / lock state

Stable identity matters for:

- selection
- structure view
- mutation targeting
- compare / revert
- testability

---

## Widget Types

Early widget types may include:

- text
- rich text
- image
- KPI
- chart
- table
- container widget
- custom widget

The system should treat widget type as a first-class concept, because type influences:

- inspector surface
- allowed props
- allowed styles
- slot compatibility
- rendering behavior
- future validation behavior

---

## Widget Capabilities

Each widget type should imply or declare capabilities.
Capabilities are useful for reasoning about what the system may do with a widget.

Possible capabilities include:

- textual
- media
- metric
- chart
- layout-container
- custom

Capabilities may inform:

- slot acceptance
- inspector sections
- prefab compatibility
- module activation
- validation rules

---

## Widget Props vs Widget Style

The Widget System must distinguish between props and style.

### Widget props

Props describe semantic or functional content relevant to the widget type.

Examples:

- text content
- chart dataset reference
- image source
- KPI label/value
- table configuration

### Widget style

Style describes appearance and treatment.

Examples:

- typography
- colors
- spacing
- backgrounds
- border treatment
- glow, shadow, opacity
- chart palette and card chrome

This separation matters because content and visual treatment often evolve differently and need different validation and reset semantics.

---

## Widget Placement

Widgets live inside Slots.
This is a non-negotiable structural rule.

A widget should not exist in the scene with no host relationship.
This is important because:

- slots define insertion rules
- slots define bounded composition regions
- slots support safe prefab and future custom widget behavior
- structure view becomes much clearer when widget placement is explicit

---

## Widget Lifecycle

A healthy widget lifecycle includes:

1. creation or insertion
2. hosting within a valid slot
3. optional selection and editing
4. preview changes
5. accepted updates
6. optional movement or replacement
7. eventual removal

The lifecycle should remain legible to support validation, compare, and removability.

---

## Widget Selection and Editing

Widgets are common authoring targets.

The system should support:

- selection on canvas
- selection from structure
- inspector surfaces tailored to widget type
- move and reorder where valid
- style updates
- prop updates
- replacement by compatible prefab or widget type in controlled flows

Selection should not imply direct mutation. It should expose eligible editing flows through governed channels.

---

## Widget Validation

Widgets should be validated against:

- slot compatibility
- required props
- supported style shape
- widget type constraints
- runtime rendering constraints
- mode restrictions if relevant

This is especially important for complex widgets like charts and future custom widgets.

---

## Widget and Prefab Relationship

A prefab may create or initialize a widget, but the resulting live widget instance is distinct from the prefab definition.

This distinction is important because:

- the widget is mutable in the scene
- the prefab is a reusable template
- compare/revert works at instance level
- changing a live widget should not silently rewrite prefab definitions

---

## Container Widgets

The system may support container-style widgets, but care is required.

A container widget may visually group content or provide widget-level local structure, but it must not erase the distinction between:

- layout structure
- slot hosting
- widget rendering

Container widgets are useful, but should not become hidden layout engines that bypass the main layout model.

---

## Chart Widgets

Chart widgets deserve special care.

Users often need more than simple color editing. Chart widgets may require:

- chart-type changes
- palette changes
- label changes
- padding adjustments
- chrome or card treatment changes
- title/subtitle adjustments
- replacement with a different chart or metric representation

This should be handled as a serious widget capability area, not as a footnote.

---

## Custom Widgets

Custom widgets are a special widget type with stricter boundaries.

They should:

- render within bounded slot regions
- use restricted APIs
- fail locally
- avoid unrestricted DOM, filesystem, or runtime access
- remain visibly part of the Widget System, not a loophole around it

Custom widgets matter, but the base Widget System must be strong before they expand.

---

## Widget Anti-Patterns

The Widget System must reject:

- widgets with no stable identity
- widgets that directly own layout tree truth
- widgets that mutate runtime state directly
- widgets that exist outside valid slots
- widget instances that secretly rewrite prefab definitions
- “special widgets” that bypass system rules without explicit contract

---

## Summary

The Widget System defines the concrete units that users compose inside Live Scene Composer. Widgets live in slots, expose typed capabilities, separate props from style, and are edited through governed authoring flows. A strong Widget System is essential for meaningful composition, selection, validation, and future extensibility.
