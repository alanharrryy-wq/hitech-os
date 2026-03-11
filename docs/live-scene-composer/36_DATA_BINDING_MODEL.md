# 36_DATA_BINDING_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product
- Scope: Conceptual data binding rules, boundaries, and future-safe handling of data-driven widgets

---

## Purpose

This document defines the Data Binding Model for Live Scene Composer. It exists because many widgets and visual elements may eventually depend on data, but the system must not let data flows become a hidden second architecture that bypasses the scene model, widget model, or mutation rules.

Data binding should remain structured and explicit.

---

## Data Binding Summary

The Composer should support the idea that some widgets render data-driven content, but binding must remain:

- bounded
- typed where possible
- understandable
- compatible with widget identity
- separate from raw unrestricted runtime access
- consistent with draft and preview semantics

The system should treat data binding as an explicit concern, not as a hidden implementation accident.

---

## What Data Binding Means Here

Data binding means associating a widget or widget property with some approved data source, derived value, or structured payload so the widget can render meaningful content.

Examples include:

- KPI value binding
- chart series binding
- table data source binding
- text widget binding to approved structured content
- conditional visual states from approved status data

---

## What Data Binding Is Not

Data binding is not:

- unrestricted query execution
- arbitrary runtime code access
- hidden implicit data mutation
- direct access to all available platform data
- a replacement for widget props
- a secret way around authoring constraints

The Composer should not become a general-purpose unbounded data scripting environment.

---

## Binding Principles

### 1. Explicit over implicit

Bindings should be declared, not guessed from scattered runtime behavior.

### 2. Widget-aware

Bindings belong to widgets or widget sub-properties, not to random invisible global state.

### 3. Read-oriented by default

The default posture for binding should be reading approved data, not mutating data systems.

### 4. Bounded sources

Bindings should use approved data sources or contracts, not arbitrary access to anything reachable.

### 5. Preview-compatible

Bindings should behave in ways that make preview and accepted state understandable.

---

## Binding Targets

Bindings may apply to:

- widget props
- specific presentation fields
- chart series config
- KPI values and labels
- table content
- status indicators

Bindings should remain target-aware and not turn the widget into an opaque blob of remote behavior.

---

## Binding Sources

Binding sources should be approved and scoped.

Examples may include:

- scene-provided data context
- approved resolved dataset references
- stable view-model-style data contracts
- safe computed value providers

The system should avoid allowing each widget to reach anywhere it wants for data.

---

## Binding and Widget Props

A binding should not erase the existence of widget props.
Instead, bindings should be part of how props are supplied or resolved.

This matters because:

- widgets still need stable local identity
- compare/revert still needs to make sense
- authoring UX still needs visible, editable structure
- bindings should remain inspectable and understandable

---

## Binding Visibility in the Product

Users should be able to tell when a widget is data-bound.

Helpful UI signals may include:

- binding indicators
- binding source summary
- read-only or derived value cues
- explicit binding editor surfaces in future versions

Invisible binding logic is a recipe for confusion.

---

## Binding and Preview

The system should define what preview means for data-bound widgets.

Examples of important questions:

- is the preview using current live data
- is it using resolved sample data
- are some style changes previewed while data remains stable
- what does compare show if style changed but data is derived

These questions should be answered by design, not discovered by accident.

---

## Binding Mutations

Changes to bindings should be treated as governed authoring changes when supported.

Examples:

- change binding source
- change field mapping
- remove binding
- switch from static prop to bound prop

These actions should remain explicit and should not bypass the mutation model.

---

## Future Scope Discipline

Data binding is important, but should not be allowed to dominate early MVP scope.
The product should first establish:

- strong scene structure
- strong slot/widget model
- strong mutation governance
- strong authoring UX

Then richer binding behavior can grow on a more stable foundation.

---

## Data Binding Anti-Patterns

The system must reject:

- hidden data reads from arbitrary internals
- widgets with invisible business logic embedded in ad hoc binders
- bindings that mutate unrelated systems
- turning the Composer into a data scripting console
- binding behavior that cannot be inspected or reasoned about

---

## Summary

The Data Binding Model should allow data-driven widgets in a bounded, explicit, widget-aware way. Binding must remain understandable, source-scoped, and compatible with the rest of the Composer architecture. Data is important, but it must not become a loophole around structure, visibility, or governance.
