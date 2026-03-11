# 01_PROJECT_OVERVIEW

## Document Status

- Status: Canonical
- Audience: Product, Architecture, Engineering, Design, QA, Tooling
- Scope: Entire Live Scene Composer initiative

---

## Purpose

This document defines the project in its most practical form: what it is, why it exists, what problem it solves, and what boundaries must remain intact so the effort does not drift into a generic console, a debug panel with extra controls, or an ungoverned runtime editor.

Live Scene Composer is not a side panel, not a configuration form, and not a disguised debug console. It is a dedicated live visual authoring product built on top of the real runtime, with controlled mutation boundaries, clear ownership boundaries, modular extensibility, and safe failure isolation.

---

## Project Name

**Live Scene Composer**

Accepted sibling and related names:

- **Runtime Debug Console**
- **console-core**
- **runtime-mutation-bridge**

These names are already established and should not be changed casually.

---

## Product Definition

Live Scene Composer is a live visual, modular authoring environment for composing scenes using a structured model:

**Scene -> Layout -> Slots -> Widgets**

It allows controlled editing of the real rendered scene without collapsing the architectural separation between authoring and runtime diagnostics.

The system must support:

- live visual editing
- layout changes
- selection, drag, resize, reorder
- typography and text editing
- backgrounds, colors, effects, and treatments
- chart appearance and replacement
- prefab insertion
- controlled custom widgets inside bounded slot regions
- preview, compare, revert, and commit workflows
- modular growth with removable feature modules
- local failure isolation so broken modules do not crash the full scene experience

---

## Problem Statement

Existing tooling in this ecosystem has historically mixed runtime diagnostics, scene/editor concerns, and shared infrastructure in ways that create confusion, stale wiring, and architectural drift. The project exists to solve the following problems:

1. There is a real need for visual authoring on top of the runtime, not just technical inspection.
2. Debug tooling and authoring tooling have different product goals and must not be conflated.
3. Runtime writes must be governed, reversible where possible, and validated through a controlled boundary.
4. The system must be extensible without becoming a monolith or a soft pile of implicit dependencies.
5. Teams need a structure that allows safe growth across modules, widgets, layouts, and future custom extensions.

---

## What the Project Is

Live Scene Composer is:

- a live visual authoring product
- a structured editor for scene composition
- a workspace centered on canvas, structure, and inspection
- a controlled mutation client of the runtime
- a modular platform for safe visual editing and composition
- a product intended to evolve through stable contracts rather than accidental wiring

---

## What the Project Is Not

Live Scene Composer is not:

- a generic admin console
- a repackaged debug tool
- a freeform runtime hacking surface
- a raw scripting shell against engine internals
- a place for direct runtime writes outside governed boundaries
- a monolithic editor that absorbs every visual, diagnostic, and operational concern

---

## Primary Users

### Primary user classes

1. **Scene authors**
   - need visual control over layout, structure, text, visual treatment, charts, and content blocks

2. **Design-minded operators**
   - need safe editing of appearance without dealing with low-level runtime internals

3. **Technical integrators**
   - need controlled extension points, prefab systems, layout structure, and predictable mutation behavior

4. **Validation and tooling teams**
   - need architecture boundaries, test seams, and evidence that the system remains governable

---

## Core User Outcomes

A successful Live Scene Composer lets users do the following without confusion:

- understand the structure of a scene
- select and manipulate visible elements
- edit appearance with immediate feedback
- insert approved prefabricated components
- make safe runtime-visible changes
- compare edits against a baseline
- discard a bad draft
- isolate local failures
- extend the system without breaking adjacent concerns

---

## Product Shape

The product should feel like a visual workspace with three persistent mental anchors:

1. **Canvas**
   - the real rendered view and interaction surface

2. **Structure**
   - the scene tree and hierarchy of layout, slots, and widgets

3. **Inspector**
   - the contextual surface for editing properties of the current selection

Optional support surfaces include prefab library, snapshots, compare/revert tools, and future advanced extensions.

The ideal working loop is:

**Select -> Change -> Preview -> Compare -> Commit or Revert**

---

## Relationship to Runtime Debug Console

This separation is fundamental.

### Runtime Debug Console

Purpose:

- inspect runtime state
- inspect overlays and layers
- inspect diagnostics and performance
- monitor runtime behavior
- validate operational and technical conditions

### Live Scene Composer

Purpose:

- author scene composition visually
- edit layout and appearance
- manage content structure
- insert prefabs
- manage safe visual changes
- support controlled custom widget regions

These are sibling products, not variants of one product and not temporary names for the same system.

---

## Architectural Position

Live Scene Composer depends on shared infrastructure through **console-core**, and depends on runtime writes through **runtime-mutation-bridge**.

It must not become the owner of runtime internals.
The runtime must not depend on the composer.
The composer must remain a controlled consumer of runtime capabilities.

Conceptual flow:

Live Scene Composer -> runtime-mutation-bridge -> adapters / scene model / runtime integration -> runtime

---

## Success Criteria

The project is successful when the following are true:

- visual authoring is useful on day one
- debug and authoring remain clearly separate
- runtime writes are validated and controlled
- the model remains structured and navigable
- modules can be added or removed without tearing down the system
- contracts define behavior better than tribal knowledge
- future extension does not require architecture re-litigation every week

---

## Non-Negotiable Principles

1. Debug and authoring remain separate.
2. The composer never performs uncontrolled direct runtime writes.
3. Mutation flows must remain explicit.
4. Modular growth is preferred over feature dumping.
5. Failure isolation is required.
6. Shared infrastructure must stay genuinely shared.
7. The project must optimize for long-term maintainability, not short-term convenience.

---

## Expected Long-Term Value

If built correctly, Live Scene Composer becomes:

- a durable authoring platform for scenes and layouts
- a stable integration surface for prefabs and future extensions
- a safer way to make runtime-visible changes
- a force multiplier for product, design, engineering, and validation teams
- a cleaner long-term replacement for any accidental editor/debug coupling that previously existed

---

## Summary

Live Scene Composer is a dedicated live visual authoring system built on top of the real runtime, but governed through explicit contracts, structured boundaries, and controlled mutation flows. Its model is Scene -> Layout -> Slots -> Widgets. It is not the Runtime Debug Console, and it must not collapse into one. The project exists to provide powerful visual composition without sacrificing modularity, governance, or runtime integrity.
