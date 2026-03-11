# 04_CORE_CONCEPTS

## Document Status

- Status: Canonical
- Audience: Product, Design, Architecture, Engineering, QA
- Scope: Foundational concepts and shared vocabulary

---

## Purpose

This document defines the core concepts that all other Live Scene Composer decisions depend on. It exists to stop terminology drift, conceptual flattening, and the repeated mistake of using the same word for multiple different responsibilities.

If the system is described loosely, it will be built loosely.
This document exists to prevent that.

---

## Foundational Model

The core conceptual model of Live Scene Composer is:

**Scene -> Layout -> Slots -> Widgets**

This is not a presentation preference. It is the model that should guide both architecture and user-facing behavior.

---

## Scene

### Definition

A **Scene** is the top-level composition unit that represents a complete editable visual experience or view in the composer context.

### Responsibilities

A Scene is responsible for:

- overall composition identity
- top-level metadata
- the root layout structure
- references to slots and widgets included in the composition
- theme / visual context at the scene level
- baseline and draft relationship where applicable

### What a Scene is not

A Scene is not:

- a raw runtime tree
- a single panel
- a single widget
- a freeform bag of arbitrary components

The Scene is the bounded whole.

---

## Layout

### Definition

A **Layout** is the spatial and structural organization of the scene. It determines how regions, containers, and slot references are arranged.

### Responsibilities

Layout is responsible for:

- structural composition
- spatial relationships
- ordering
- alignment and placement rules
- container hierarchy
- slot placement references

### What Layout is not

Layout is not the same thing as content.
Layout describes where and how things are arranged, not what data they represent.

---

## Slot

### Definition

A **Slot** is a bounded region of the scene where one or more widgets may live according to defined policies and constraints.

### Responsibilities

A Slot is responsible for:

- declaring what kind of region it is
- constraining what may be inserted
- limiting the number or kinds of widgets allowed
- serving as the bounded host for prefab or custom widget insertion
- acting as a compositional anchor between layout structure and widget instances

### Examples

A slot may represent:

- a chart region
- a metric strip area
- a media region
- a text region
- a custom bounded composition area

### What a Slot is not

A Slot is not:

- the content itself
- a layout tree in disguise
- a generic div with no meaning
- a full widget implementation

---

## Widget

### Definition

A **Widget** is a renderable composition unit placed inside a slot.

### Responsibilities

A Widget is responsible for:

- rendering a concrete visual or content block
- owning widget-level props and styles
- participating in preview and runtime binding
- exposing capabilities based on type

### Examples

Widgets may include:

- text
- rich text
- chart
- image
- KPI
- table
- container widget
- custom widget

### What a Widget is not

A Widget is not:

- a slot
- a layout engine
- a scene
- a direct runtime mutation authority

---

## Prefab

### Definition

A **Prefab** is a reusable template that can instantiate one or more widgets with predefined props, styles, and intended slot compatibility.

### Responsibilities

A Prefab is responsible for:

- representing reusable composition patterns
- speeding insertion
- carrying default structure, props, or styling
- constraining insertion to valid host slots

### What a Prefab is not

A Prefab is not the live widget instance itself.
A Prefab becomes useful when instantiated into widget instances inside valid slots.

---

## Selection

### Definition

**Selection** is the currently active authoring target in the composer.

### Responsibilities

Selection determines:

- what the user is actively editing
- what the inspector shows
- which handles and overlays appear on canvas
- what structure node is active
- which operations are currently legal

### Selection targets

Selection may point to:

- scene
- layout node
- slot
- widget

Selection must remain explicit and synchronized across canvas, structure, and inspector.

---

## Inspector

### Definition

The **Inspector** is the contextual editing surface for the current selection.

### Responsibilities

The Inspector is responsible for:

- exposing editable properties of the selection
- surfacing only relevant controls
- preserving contextual clarity
- invoking controlled mutations rather than mutating runtime state directly

The Inspector is not a random dumping ground for every possible property.

---

## Structure View

### Definition

The **Structure View** is the hierarchical representation of the scene model.

### Responsibilities

It helps users understand:

- scene composition
- layout hierarchy
- slot placement
- widget ownership
- visibility and ordering

The structure view exists because visual editing alone is not enough for complex composition.

---

## Canvas

### Definition

The **Canvas** is the live rendered interaction surface of the scene.

### Responsibilities

The Canvas is responsible for:

- showing the real rendered result
- supporting selection and direct manipulation
- displaying handles, guides, and overlays
- reflecting preview changes quickly

The canvas is not just a screenshot or symbolic mock surface. It must stay tied to the real rendering outcome.

---

## Mutation

### Definition

A **Mutation** is a controlled state change request initiated by the composer against draft, preview, or runtime-facing composition state.

### Responsibilities

A mutation must be:

- explicit
- typed
- validated
- attributable
- appropriately scoped
- routed through runtime-mutation-bridge when write-capable

Mutation is the unit of change, not a hidden side effect.

---

## Preview

### Definition

**Preview** is the temporary presentation of a change before the system considers it committed.

### Responsibilities

Preview allows:

- immediate visual feedback
- comparison against baseline
- experimentation
- controlled staging before commit

Preview must remain semantically distinct from commit and persistence.

---

## Commit

### Definition

A **Commit** is the action that promotes accepted draft or preview changes to the next accepted state within the governing workflow.

Commit does not necessarily mean irreversible persistence to every downstream system, but it always means “the system now treats this as accepted state.”

---

## Baseline

### Definition

The **Baseline** is the previously accepted reference state against which draft changes are compared.

This concept exists to enable:

- diffing
- comparison
- discard semantics
- trust in editing workflows

---

## Safe Mode

### Definition

**Safe Mode** is the default operational mode that allows only approved, reversible, or strongly governed editing actions.

### Expected Safe Mode actions

- styling changes
- text changes
- layout adjustments within constraints
- valid prefab insertion
- appearance updates
- bounded slot and widget modifications

### Why it exists

Safe Mode is the normal operating environment. It prevents the product from becoming reckless by default.

---

## Advanced Mode

### Definition

**Advanced Mode** is an explicitly gated mode for more powerful but higher-risk authoring operations.

This mode should not be treated as “normal but with fewer warnings.”
It exists for carefully bounded advanced capabilities and must remain deliberately governed.

---

## Custom Widget

### Definition

A **Custom Widget** is a bounded, non-prefab widget that renders inside an approved slot using a restricted API and sandboxed execution model.

### Core principles

A custom widget must:

- render only within its allowed region
- fail locally rather than globally
- use only approved APIs
- avoid unrestricted access to the filesystem, DOM, engine internals, or arbitrary runtime mutation

---

## Runtime-Mutation-Bridge

### Definition

The **runtime-mutation-bridge** is the controlled boundary through which write-capable composer changes must flow before they affect runtime-facing state.

### Responsibilities

It validates:

- source
- target
- mutation type
- mode
- reversibility expectations
- policy allowlists
- preview vs commit semantics

It is the enforcement boundary between authoring intent and runtime effect.

---

## Console-Core

### Definition

**console-core** is the shared infrastructure layer used by sibling products where shared ownership is legitimate.

### Responsibilities

It may contain:

- shell primitives
- layout primitives
- registry foundations
- event infrastructure
- lifecycle helpers
- diagnostics helpers that are truly shared
- runtime invariants useful across sibling products

It must not become a hidden product layer.

---

## Runtime Debug Console

### Definition

**Runtime Debug Console** is the diagnostic sibling product.

### Responsibilities

It owns:

- runtime inspection
- performance tools
- overlays
- event monitoring
- technical diagnostics
- safe runtime operational controls

It must not absorb authoring logic.

---

## Summary

These concepts define the vocabulary and structure of Live Scene Composer. The most important truths are: the model is Scene -> Layout -> Slots -> Widgets; runtime writes must be governed through runtime-mutation-bridge; debug and authoring are different products; and compositional meaning must remain stronger than ad hoc UI convenience.
