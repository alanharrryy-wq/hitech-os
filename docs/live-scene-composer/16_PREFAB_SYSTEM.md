# 16_PREFAB_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product, Design
- Scope: Prefab definitions, insertion behavior, compatibility, and reuse

---

## Purpose

This document defines the Prefab System for Live Scene Composer. Prefabs are reusable composition templates that accelerate authoring and create consistency without hard-coding the scene into inflexible layouts.

The Prefab System exists to make composition fast, structured, and reusable.

---

## Prefab System Summary

A Prefab is a reusable definition that can instantiate one or more widget instances, optionally with default structure, props, and style assumptions.

Prefabs should support:

- fast insertion
- repeatable composition patterns
- compatibility with valid slots
- sensible defaults
- safe replacement or reuse workflows
- structured growth of the authoring ecosystem

A Prefab is not the same thing as a live widget instance.

---

## Why Prefabs Exist

Prefabs solve several real authoring needs:

- users should not build every scene element from scratch
- common blocks should be reusable
- composition should move faster
- structure and visual quality should improve through good defaults
- insertion should remain governed instead of arbitrary

Without prefabs, authoring becomes slower, less consistent, and more vulnerable to low-quality ad hoc assembly.

---

## Prefab Responsibilities

A prefab is responsible for:

- naming a reusable composition unit
- declaring its intended category
- declaring what slot kinds it can be inserted into
- defining default props and style
- optionally defining multi-widget or compound structure
- enabling repeatable composition patterns

A prefab is not responsible for:

- being the live mutable instance in the scene
- bypassing slot validation
- bypassing mutation flows
- owning unrelated scene state

---

## Early Prefab Categories

Early useful prefab categories may include:

- text
- rich text
- image
- KPI
- chart
- table
- badge / status
- hero / header
- spacer / divider
- container / stack

Compound prefabs may later include:

- executive KPI section
- chart + KPI stack
- hero + summary
- comparison block
- checklist or audit card

The key is that prefabs should represent meaningful authoring value, not just a random list of components.

---

## Prefab Definition Shape

A healthy prefab definition should include concepts such as:

- prefab id
- display name
- category
- widget type or composite definition
- default props
- default style
- accepted slot kinds
- tags or search metadata
- version

This helps the system reason about insertion, compatibility, search, and migration later.

---

## Prefab and Widget Relationship

A prefab is a template.
A widget is the live scene instance.

This distinction must stay explicit because:

- prefabs are reusable definitions
- widgets are mutable scene instances
- compare/revert operates on scene instances
- editing a widget should not silently rewrite prefab definitions
- prefab evolution and widget evolution are related but not identical concerns

---

## Prefab Insertion Flow

A healthy prefab insertion flow looks like this:

1. user selects or focuses a target slot
2. system filters compatible prefabs
3. user picks a prefab
4. prefab is instantiated into widget instance(s)
5. slot acceptance and capacity are validated
6. preview is shown
7. user continues editing, commits, or discards as usual

This flow is far safer and clearer than unrestricted free insertion.

---

## Compatibility Rules

Prefabs should declare compatibility explicitly.

Compatibility may depend on:

- slot kind
- slot capacity
- widget capabilities
- current mode
- composition constraints
- whether the prefab is single-widget or compound

The system must not assume “everything can go everywhere.”

---

## Compound Prefabs

The system may support compound prefabs that create more than one widget or create a local structured grouping.

This can be useful, but must remain disciplined.

Compound prefabs should still:

- target valid slots
- obey slot policy
- remain representable in structure view
- produce understandable scene instances
- avoid smuggling a hidden second composition model into the system

---

## Prefab Library

The Prefab Library is the discovery and insertion surface for prefabs.

A good prefab library should support:

- search
- category browsing
- compatibility filtering
- preview or description
- quick insertion into current selection

The library should feel like a practical composition tool, not a random component catalog.

---

## Prefab Quality

Prefabs should be opinionated enough to be useful.
Bad prefabs create clutter and low-quality output.

A strong prefab should provide:

- good defaults
- visual coherence
- valid structure
- meaningful use case
- clear insertion expectations

The goal is not maximum prefab count.
The goal is meaningful reusable building blocks.

---

## Prefab Evolution

Prefab definitions may evolve over time, but the system should avoid coupling that makes all existing widgets fragile whenever a prefab changes.

The relationship between prefab versioning and existing widget instances should be approached deliberately.
Even if full migration mechanics come later, the system should preserve the conceptual separation now.

---

## Prefab Anti-Patterns

The Prefab System must reject:

- prefabs that are indistinguishable from live widget state
- inserting prefabs into invalid slot contexts
- giant prefab catalogs with no compositional logic
- prefabs used as a substitute for a scene model
- compound prefabs that secretly own broad layout truth
- editing flows that rewrite prefab definitions unintentionally

---

## Summary

The Prefab System exists to make composition fast, reusable, and structured. Prefabs are reusable templates that instantiate widget instances into valid slots. They must be compatibility-aware, well-categorized, and clearly distinct from live widget state. A strong Prefab System is one of the fastest ways to make Live Scene Composer genuinely useful.
