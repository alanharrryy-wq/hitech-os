#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="${1:-docs}"
mkdir -p "$DOCS_DIR"

cat > "$DOCS_DIR/01_PROJECT_OVERVIEW.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/02_PRODUCT_VISION.md" <<'EOF'
# 02_PRODUCT_VISION

## Document Status

- Status: Canonical
- Audience: Product, Design, Architecture, Engineering
- Scope: Product intent, direction, and experience principles

---

## Vision Statement

Live Scene Composer should become the default live authoring workspace for scene-based visual composition in this ecosystem: a product that makes scene editing feel immediate, structured, elegant, and safe.

The target experience is not “editing configs in a panel.” The target experience is “working directly with the scene,” with the confidence that the system is modular, governable, and resilient.

---

## Long-Term Product Vision

The long-term vision is a product that enables teams to:

- compose live scenes visually
- manipulate layout and appearance directly
- reason about structure through a stable scene model
- insert prefabricated content blocks quickly
- extend the scene with bounded custom widgets
- compare drafts, revert changes, and maintain baseline integrity
- evolve complex visual systems without collapsing runtime discipline

This is a visual composition product with runtime awareness, not a diagnostics product with editing accidents.

---

## Product Identity

The identity of Live Scene Composer should remain clear in all product decisions.

It is:

- a composition workspace
- a structured scene authoring tool
- a modular system
- a real-time visual editor with controlled mutations
- a product optimized for authoring tasks, not operational diagnostics

It should never drift into:

- a technical console with extra controls
- a dumping ground for unrelated tooling
- a script shell against internals
- a “temporary” editor path inside debug experiences

---

## Product Experience Principles

### 1. Direct manipulation over abstract indirection

The user should be able to select, move, resize, reorder, and style visible things directly where possible. The system should favor “edit the scene” over “edit hidden metadata and hope the scene updates correctly.”

### 2. Structure must remain visible

Even while the product feels visual, the structure of the scene must remain intelligible. The user should be able to understand the hierarchy and placement of content through a structure view or equivalent system map.

### 3. Safe power beats unsafe freedom

The product should be powerful, but controlled. Users should be able to do meaningful work safely. Unsafe capabilities should be explicitly gated and never become the default mode of operation.

### 4. Immediate feedback is required

The editing loop must feel responsive. The system should show preview changes quickly and make the current state understandable.

### 5. Reversibility builds trust

The product should create confidence by supporting compare, revert, discard, and reset semantics. A tool that changes a live scene without clear recovery paths erodes trust.

### 6. Modularity is a product feature

Modularity is not just an engineering preference. It is how the product stays reliable, extensible, and operable over time.

---

## Desired User Feeling

The ideal user should feel:

- in control
- visually grounded
- structurally informed
- safe to experiment
- able to undo mistakes
- confident that the editor is not silently breaking the runtime
- able to extend the system in bounded ways

The product should feel like a serious workspace, not a pile of side panels.

---

## Experience Metaphor

The right metaphor is closer to a **visual composition studio** than a configuration console.

The user should feel like they are:

- composing a live scene
- arranging regions and content blocks
- shaping appearance and layout in context
- working with structured, reusable building blocks
- staying inside a system with rules that help rather than obstruct

---

## Product Scope Direction

The product should grow from a safe, well-governed MVP into a richer authoring platform.

### Early focus

- visual selection
- layout manipulation
- structure awareness
- typography and appearance editing
- prefab insertion
- controlled runtime mutation
- compare / discard / reset basics

### Later growth

- richer themes and variants
- stronger chart editing systems
- custom widget lifecycle tooling
- more advanced presets and snapshots
- safe advanced mode surfaces
- more capable integrations and data-driven composition

The product should not attempt maximum surface area on day one. It should build a durable center.

---

## Relationship to Existing Ecosystem

The product should reuse what is valuable from the ecosystem:

- runtime rendering paths
- scene-related infrastructure
- shell primitives where truly shared
- registry patterns where architecturally sound

But it must do so with clean boundaries.

The vision is not to discard the ecosystem.
The vision is to use it without inheriting old coupling mistakes.

---

## Design Values

1. **Clarity**
   - the user should understand what they are selecting, editing, and changing

2. **Containment**
   - edits should remain bounded and interpretable

3. **Precision**
   - the system should respect structure, constraints, and controlled layouts

4. **Recoverability**
   - the user should be able to compare, revert, and reset

5. **Composability**
   - the scene should be assembled through reusable blocks and understandable models

6. **Governance**
   - power should be delivered through explicit contracts, not hidden wiring

---

## Anti-Vision

To protect product direction, the following anti-vision patterns must be rejected:

- “let’s just add authoring into the debug console for now”
- “let’s expose direct runtime writes because it’s faster”
- “let’s skip structure and just edit by side panel”
- “let’s permit custom code everywhere and secure it later”
- “let’s make the shared layer absorb product-specific logic”
- “let’s let the MVP define architecture by accident”

These shortcuts always look convenient early and always become expensive later.

---

## Product Success Narrative

A mature version of Live Scene Composer should enable a user to open a live scene, understand its structure immediately, select regions and widgets directly, modify layout and styling with confidence, insert approved prefabs, preview the result, compare against a baseline, and commit only what they intend. When something breaks, it breaks locally, not catastrophically.

That is the bar.

---

## Summary

The vision for Live Scene Composer is a true live authoring workspace: visual, structured, modular, and safe. It should be powerful without being reckless, extensible without being chaotic, and strongly separated from diagnostics tooling. Every meaningful product decision should preserve this identity.
EOF

cat > "$DOCS_DIR/03_GOALS_AND_NON_GOALS.md" <<'EOF'
# 03_GOALS_AND_NON_GOALS

## Document Status

- Status: Canonical
- Audience: Product, Architecture, Engineering, Delivery
- Scope: Project intent, scope control, and anti-scope drift

---

## Purpose

This document defines what the project is explicitly trying to accomplish and what it is explicitly not trying to accomplish. Its purpose is to prevent scope drift, architecture drift, and category confusion as the system grows.

A project without non-goals becomes a magnet for every adjacent idea.
This document exists to stop that.

---

## Primary Goals

### Goal 1: Build a real live visual authoring product

The system must be able to function as a real authoring environment for scene composition on top of the runtime. It should support meaningful visual editing tasks, not symbolic placeholders for future editing.

### Goal 2: Preserve clean product separation

Runtime Debug Console and Live Scene Composer must remain separate sibling products with distinct purposes, ownership, and evolution paths.

### Goal 3: Establish a durable scene composition model

The system must operate through a model robust enough to support growth:

**Scene -> Layout -> Slots -> Widgets**

The project is not allowed to devolve into anonymous panels and ad hoc element mutations.

### Goal 4: Govern runtime mutations through a bridge

All write-capable authoring mutations must pass through runtime-mutation-bridge. Mutation validation, mode control, reversibility expectations, and safety rules must remain explicit.

### Goal 5: Support modular product growth

The system must be able to grow through modules that can be added, removed, validated, and isolated without destabilizing the entire product.

### Goal 6: Deliver a useful MVP without inflating the scope

The first product version must be safe, coherent, and useful. It must not try to solve every authoring, extension, theming, scripting, and runtime integration problem at once.

### Goal 7: Support trust through compare and recovery semantics

The system should make users comfortable experimenting. Preview, compare, discard, reset, and commit semantics must be part of the mental model.

---

## Secondary Goals

### Secondary Goal 1: Reuse strong existing infrastructure without inheriting bad coupling

The project should reuse what is genuinely useful from the ecosystem, but only through explicit boundaries.

### Secondary Goal 2: Make future extension safer

The system should leave clear paths for prefabs, safe custom widgets, themes, variants, richer modules, and more advanced behavior later.

### Secondary Goal 3: Improve team coordination

The project should be documentable, dispatchable, and governable across different worker roles and future implementation slices.

---

## MVP Goals

The MVP should prove the product category and architecture at the same time.

The MVP should:

- render a usable composer shell
- support selection on a real scene
- support basic drag / resize / reorder interactions where appropriate
- show a structure view for scene composition
- show an inspector for selected items
- support text, typography, and background editing
- support basic prefab insertion into valid slots
- route write-capable changes through a mutation bridge
- support baseline/draft/revert semantics at a minimum useful level
- keep Runtime Debug Console separate and intact

---

## Non-Goals

### Non-Goal 1: Do not merge debug and authoring into one tool

The project must not collapse debug and authoring into the same product path, even temporarily. The “temporary” version always becomes the accidental permanent version.

### Non-Goal 2: Do not expose direct unrestricted runtime mutation

The project is not building a raw write console to the runtime. That would undermine safety, validation, reversibility, and future architecture.

### Non-Goal 3: Do not make custom code the first-class MVP path

Custom widgets matter, but the initial version is not about unrestricted user code injection. The project should begin with safe prefab and visual authoring foundations.

### Non-Goal 4: Do not build a universal design tool

The goal is not to replicate a general-purpose design suite or visual design platform. The product is specifically about live scene composition inside this ecosystem.

### Non-Goal 5: Do not solve all responsive and advanced behaviors at once

Deep responsive rules, advanced behavior editing, large-scale scripting, internal marketplaces, and complex binding systems are not first-wave requirements.

### Non-Goal 6: Do not convert shared infrastructure into a grab bag

console-core is not allowed to absorb product-specific logic just because multiple teams might find it convenient.

### Non-Goal 7: Do not let the MVP define architecture accidentally

The MVP must be constrained, but not careless. Fast implementation is not permission to erase long-term boundaries.

---

## What the Project Should Intentionally Delay

These areas should be deferred until the foundation is strong:

- large custom widget platform surface
- deep advanced mode scripting
- complex responsive authoring rules
- highly dynamic cross-scene binding systems
- broad plugin ecosystems
- generalized runtime code injection surfaces
- overgrown theme engines
- feature marketplace mechanics

Deferral is not weakness. Deferral is deliberate scope control.

---

## What Must Be True Before Expanding Scope

Before major expansion, the following must be true:

- the core scene model is stable
- bridge-based mutation flow is real, not aspirational
- debug and authoring remain separated in code and runtime paths
- module growth is governed by contracts
- failure isolation exists
- preview/commit/revert semantics are legible
- architecture guardrails exist and pass

If those are not true, adding more features is just decorating instability.

---

## Decision Filter

Every proposed feature or change should be evaluated through these questions:

1. Does it strengthen the identity of Live Scene Composer as a visual authoring product?
2. Does it preserve separation from Runtime Debug Console?
3. Does it require or bypass runtime-mutation-bridge?
4. Does it preserve or damage the Scene -> Layout -> Slots -> Widgets model?
5. Can it be delivered modularly?
6. Does it improve or weaken recoverability and trust?
7. Is this necessary now, or is it future work pretending to be urgent?

If a proposal fails these questions, it should not enter the near-term scope.

---

## Summary

The goals of Live Scene Composer are ambitious but controlled: real visual authoring, strong boundaries, governed mutations, stable domain structure, modular growth, and a useful safe MVP. The non-goals are equally important: no debug/editor collapse, no free runtime mutation, no fake shared layer, and no bloated MVP. This document exists to preserve that discipline.
EOF

cat > "$DOCS_DIR/04_CORE_CONCEPTS.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/05_SYSTEM_ARCHITECTURE.md" <<'EOF'
# 05_SYSTEM_ARCHITECTURE

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation
- Scope: High-level system architecture for Live Scene Composer and its sibling boundaries

---

## Purpose

This document defines the intended top-level architecture for Live Scene Composer and its relationship to the surrounding ecosystem. It describes what major parts exist, why they exist, and how they are allowed to relate to each other.

This is not a low-level implementation spec.
It is the structural map that the implementation must remain faithful to.

---

## Top-Level Architectural Shape

The intended system boundary includes these primary areas:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`

Surrounding integration surfaces may include runtime-specific and scene-specific systems such as pitch runtime paths and scene-studio-related paths, but those integrations must not erase the product boundaries above.

---

## Top-Level Responsibility Model

### console-core

Shared infrastructure only.

It may own:

- shell primitives
- layout primitives
- registry primitives
- lifecycle helpers
- event foundations
- shared runtime invariants
- legitimately reusable diagnostics helpers

It must not own product-specific authoring behavior or runtime-debug-only behavior just because those behaviors need some UI.

---

### runtime-debug-console

Diagnostic sibling product.

It owns:

- runtime inspection views
- performance diagnostics
- overlay controls
- event monitoring
- runtime state inspection
- safe technical control surfaces

It must not become the host for visual authoring logic.

---

### live-scene-composer

Authoring sibling product.

It should own:

- canvas-based authoring
- selection systems
- structure view
- inspector systems
- scene composition model
- layout editing
- slot and widget composition
- prefab insertion
- appearance and typography editing
- chart appearance editing
- snapshot / draft / compare workflows
- future bounded custom widget support

---

### runtime-mutation-bridge

Mutation governance boundary.

It should own:

- typed mutation contracts
- validation
- allowlists / policy enforcement
- safe mode vs advanced mode gating
- preview / commit / revert semantics at the mutation level
- adapter routing toward runtime-facing state

The composer should not perform uncontrolled write actions outside this boundary.

---

## Architectural Principle: Sibling Products, Not One Product

Runtime Debug Console and Live Scene Composer are separate sibling products. They may both use console-core, but they should not merge into one runtime path or one ambiguous product shell.

This matters because:

- they solve different problems
- they should evolve at different speeds
- their safety concerns differ
- their module sets differ
- their ownership and validation needs differ

---

## Core Authoring Architecture

The internal architecture of Live Scene Composer should follow these conceptual layers:

1. **Composer Shell**
   - product shell and top-level workspace orchestration

2. **Scene Model**
   - structured authoring representation of the scene

3. **Selection System**
   - selected target and editing focus model

4. **Canvas Interaction Layer**
   - direct manipulation, overlays, bounds, handles, guides

5. **Structure Layer**
   - hierarchical representation of layout, slots, and widgets

6. **Inspector Layer**
   - contextual property editing surfaces

7. **Prefab and Widget Systems**
   - insertion and composition mechanisms

8. **Mutation Client Layer**
   - typed requests routed through runtime-mutation-bridge

9. **Integration Adapters**
   - bounded integration with runtime-facing rendering or scene-specific surfaces

---

## Data and Control Flow

High-level flow:

1. The composer loads a scene-oriented composition model.
2. The canvas renders the current authoring target against runtime-aware output.
3. Selection is synchronized between canvas, structure, and inspector.
4. User actions generate typed mutation intent.
5. Write-capable changes are routed through runtime-mutation-bridge.
6. Bridge validation determines whether a change is allowed.
7. Approved preview or commit effects propagate through the appropriate adapter path.
8. The scene reflects the new approved state or remains unchanged if validation fails.

This flow exists to make changes explicit, governable, and testable.

---

## Scene Model Position

The scene model is central and should not be treated as incidental glue.

It is the structured authoring representation that allows the system to reason about:

- scene identity
- layout structure
- slot definitions
- widget instances
- prefab relationships
- draft vs baseline semantics
- future snapshot capabilities

Without a strong scene model, the system will devolve into ad hoc runtime poking.

---

## Mutation Boundary Position

runtime-mutation-bridge sits between authoring intent and runtime effect.

Conceptual path:

Live Scene Composer -> runtime-mutation-bridge -> adapters -> runtime-facing state

This separation exists so that:

- mutation policy is enforceable
- writes are visible and auditable
- different operating modes are possible
- reversibility can be reasoned about
- dangerous shortcuts are harder to introduce

---

## Integration Strategy

The system should reuse real runtime and existing ecosystem pieces where appropriate, but integration should occur through explicit adapter seams.

Preferred integration style:

- explicit adapter seams
- typed bridges
- named contracts
- import direction discipline
- product-level isolation

Disallowed integration style:

- direct arbitrary runtime writes
- product-specific logic hidden inside shared layers
- route-binding shortcuts that collapse sibling boundaries
- circular ownership between composer and runtime systems

---

## Failure Isolation Model

The architecture must assume that some modules or widget systems will fail.

Therefore:

- failure should be local wherever possible
- one broken authoring module should not collapse the whole composer
- future custom widget failures must remain bounded to their slot region
- infrastructure and policy boundaries must fail clearly rather than silently

Failure isolation is a first-class architecture requirement, not a polish item.

---

## Modular Growth Model

Live Scene Composer should grow through bounded modules rather than monolithic surface expansion.

A healthy module system should allow:

- clear ownership
- scoped capabilities
- registration discipline
- local cleanup
- replacement or removal without wide teardown
- compatibility with policy validation

This matters because the product will eventually span layout, typography, charts, effects, prefabs, custom widgets, snapshots, and more.

---

## Architectural Anti-Patterns

The architecture must reject the following:

1. shared infrastructure absorbing product logic
2. direct runtime mutation from authoring UI
3. debug routes registering composer features
4. flat “everything is a panel” mental models
5. duplicated ownership between scene, slot, widget, and layout concepts
6. uncontrolled import graphs between sibling boundaries
7. basing architecture on current convenience instead of durable seams

---

## Recommended Package Shape

Conceptually, the package shape should continue to reflect:

- `dev-console/console-core/`
- `dev-console/runtime-debug-console/`
- `live-scene-composer/`
- `runtime-mutation-bridge/`

Additional sub-areas inside the composer may include:

- `canvas/`
- `selection/`
- `structure/`
- `inspector/`
- `scene-model/`
- `layout/`
- `slots/`
- `widgets/`
- `prefabs/`
- `snapshots/`
- `custom-widgets/`
- `modules/`

Exact folders may evolve, but the architectural roles should not.

---

## Validation Expectations

Architecture is only real if the system can detect violations.

The project should maintain:

- architecture guardrails
- dependency policies
- registration seam tests
- mutation path validation
- boundary-focused tests

It should be cheap to detect when someone tries to reintroduce the wrong coupling.

---

## Summary

The architecture of Live Scene Composer is built on four core boundaries: console-core, runtime-debug-console, live-scene-composer, and runtime-mutation-bridge. The composer is a structured authoring product, not a debug add-on. Runtime writes must cross a controlled mutation boundary. Integration must happen through explicit adapters. The system must optimize for modularity, failure isolation, and boundary preservation from the start.
EOF

cat > "$DOCS_DIR/06_SYSTEM_BOUNDARIES.md" <<'EOF'
# 06_SYSTEM_BOUNDARIES

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation
- Scope: Ownership boundaries, import discipline, and cross-system responsibility control

---

## Purpose

This document defines the major boundaries in the Live Scene Composer ecosystem and the rules that preserve them. It exists because boundaries are easier to state than to preserve, and once blurred they are expensive to restore.

A system with weak boundaries eventually replaces design with accidental coupling.
This document exists to prevent that.

---

## Boundary Summary

The system must preserve these top-level boundaries:

- **console-core**: shared infrastructure
- **runtime-debug-console**: diagnostics product
- **live-scene-composer**: authoring product
- **runtime-mutation-bridge**: runtime write governance boundary

Surrounding runtime and scene ecosystems may be integrated, but they do not erase these ownership lines.

---

## Boundary 1: console-core

### Purpose

console-core is the only shared infrastructure layer intended for sibling product reuse.

### Allowed responsibilities

- shell primitives
- layout primitives
- registry primitives
- event infrastructure
- lifecycle helpers
- shared runtime invariants
- genuinely shared diagnostics helpers
- common product-shell building blocks that remain product-neutral

### Forbidden responsibilities

- runtime-debug-specific product logic
- composer-specific authoring logic
- mutation policy logic that belongs in the bridge
- scene authoring semantics
- direct ownership of prefab, slot, or widget composition systems
- product-specific routing shortcuts

### Boundary rule

If a concern is shared only because current code placement is convenient, it does not belong here.

---

## Boundary 2: runtime-debug-console

### Purpose

runtime-debug-console is the diagnostic sibling product.

### Allowed responsibilities

- runtime inspection
- overlays and layer visibility aids
- performance diagnostics
- event monitoring
- runtime state visualization
- safe operational debug controls

### Forbidden responsibilities

- visual scene authoring
- scene composition
- layout editing as authoring functionality
- prefab insertion
- general style editing for composition
- custom widget authoring
- composer module registration

### Boundary rule

runtime-debug-console may inspect the scene and runtime but must not become the place where scene composition is authored.

---

## Boundary 3: live-scene-composer

### Purpose

live-scene-composer is the authoring sibling product.

### Allowed responsibilities

- scene composition shell
- canvas interaction
- selection
- structure tree
- inspector
- layout authoring
- slot and widget composition
- prefab insertion
- appearance editing
- chart styling and visual treatment
- draft / compare / revert workflows
- bounded custom widget systems
- authoring-specific module registration

### Forbidden responsibilities

- bypassing runtime-mutation-bridge
- absorbing runtime diagnostics concerns
- mutating runtime internals directly
- reclassifying shared infrastructure as product-specific by stealth
- inheriting debug routes or runtime-debug registration flows

### Boundary rule

The composer owns authoring, not diagnostics, and not unrestricted runtime access.

---

## Boundary 4: runtime-mutation-bridge

### Purpose

runtime-mutation-bridge is the enforcement boundary between authoring intent and write-capable runtime effect.

### Allowed responsibilities

- mutation contracts
- validation
- mutation allowlists
- source and target checks
- safe mode / advanced mode gating
- preview / commit / revert semantics at mutation level
- adapter routing to downstream runtime-facing systems

### Forbidden responsibilities

- becoming the general owner of authoring UI
- housing broad product logic unrelated to mutation governance
- becoming a hidden substitute for scene modeling
- bypassing its own policies through privileged shortcuts

### Boundary rule

All write-capable composer mutations must pass through the bridge, and the bridge must remain a real policy boundary rather than a naming ornament.

---

## Read vs Write Boundary

A useful distinction in the system is the difference between reading and writing.

### Read-oriented relationships

Read-oriented relationships may include:

- reading runtime state for inspection
- reading scene structure for composition
- reading visual bounds for interaction overlays
- reading allowed capabilities or contract metadata

Read access still needs discipline, but it is not equivalent to write authority.

### Write-oriented relationships

Write-oriented relationships are more sensitive and must be explicitly governed. Examples include:

- changing widget props
- changing layout or positioning
- applying style changes
- inserting or removing widget instances
- committing draft changes to accepted state

These changes must pass through runtime-mutation-bridge when they affect runtime-facing state.

---

## Ownership Boundaries Inside the Composer

Even within live-scene-composer, ownership must remain explicit.

### Scene model owns

- overall scene composition structure
- scene-level metadata
- top-level layout reference
- slot registry association
- widget instance inclusion

### Layout owns

- structural placement
- ordering
- spatial relationships
- layout node hierarchy

### Slots own

- bounded region semantics
- host constraints
- widget acceptance policy
- capacity and insertion rules

### Widgets own

- instance-level content props
- style props
- widget-specific runtime bindings where applicable

### Inspector owns

- presentation of editable properties for a current selection
- it does not own composition truth by itself

### Canvas owns

- direct interaction and live feedback surface
- it does not own domain truth either

This separation matters because flattening these roles produces unmaintainable state.

---

## Boundary Violation Examples

The following are examples of unacceptable boundary violations:

1. A composer panel registered through runtime-debug-console paths
2. A shared console-core helper that knows about widget prefab policy
3. A composer UI directly calling runtime internals without bridge validation
4. A runtime-debug overlay mutating scene layout in authoring ways
5. A slot system that secretly behaves like a layout tree
6. A widget instance that performs unrestricted global side effects
7. A route-binding shortcut that mounts composer inside debug-specific flows

These are not harmless conveniences. They are architecture debt.

---

## Boundary Preservation Techniques

The project should actively preserve boundaries through:

- file and package structure
- import discipline
- dependency policy
- architecture guard checks
- registration seam tests
- mutation-path tests
- protected-node tracking
- clear documentation and ownership rules

Good intentions alone are not enough.

---

## Boundary Review Questions

When reviewing a change, ask:

1. Which boundary does this code belong to?
2. Which boundary does it now depend on?
3. Is that dependency read-only, write-capable, or mixed?
4. Is this concern truly shared or merely reused?
5. Does this change blur the debug/composer distinction?
6. Does this bypass the mutation bridge?
7. Would this make future wiring easier or more dangerous?

If the answers are fuzzy, the boundary is probably being weakened.

---

## Summary

System boundaries in Live Scene Composer are a core part of product and architecture correctness. console-core is shared infrastructure only. runtime-debug-console is diagnostics only. live-scene-composer is authoring only. runtime-mutation-bridge governs write-capable mutations. These lines must be preserved in naming, imports, runtime paths, and ownership decisions.
EOF

cat > "$DOCS_DIR/07_DOMAIN_MODEL.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/08_STATE_MODEL.md" <<'EOF'
# 08_STATE_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation
- Scope: State categories, ownership, transitions, and trust model

---

## Purpose

This document defines how state should be understood and categorized in Live Scene Composer. It exists because state confusion is one of the fastest ways to create invalid behavior, broken preview semantics, accidental persistence bugs, and impossible-to-debug authoring workflows.

The goal is to make state explicit, layered, and testable.

---

## State Model Summary

The system should reason about state in at least five categories:

1. **Baseline State**
2. **Draft State**
3. **Preview State**
4. **Ephemeral UI State**
5. **Runtime-Observed State**

These categories are related, but not interchangeable.

---

## Baseline State

### Definition

Baseline State is the accepted reference state against which current authoring changes are evaluated.

### Responsibilities

Baseline State exists to:

- preserve a trusted reference point
- support compare and diff
- support discard semantics
- reduce fear during live authoring
- define what “current accepted state” means for the user

### Characteristics

- stable until intentionally replaced
- not casually mutated by local UI behavior
- suitable for comparison and recovery workflows

### Examples

- last accepted scene composition
- last approved set of visual styles
- current accepted widget arrangement

---

## Draft State

### Definition

Draft State is the mutable working state where authoring changes accumulate before acceptance.

### Responsibilities

Draft State exists to:

- hold current in-progress edits
- allow experimentation
- isolate unaccepted changes from baseline
- support preview and compare workflows

### Characteristics

- mutable
- user-driven
- reversible
- may be promoted to accepted state later
- should remain coherent even after multiple local edits

### Examples

- moved widget not yet committed
- typography changes under review
- inserted prefab not yet accepted into baseline state

---

## Preview State

### Definition

Preview State is the rendered presentation of a Draft or pending change within the live editing experience.

### Why it matters

The user sees the preview, not abstract state categories.
If preview semantics are wrong, trust collapses.

### Responsibilities

Preview State exists to:

- show what the user is about to accept
- provide immediate visual feedback
- allow compare with baseline
- support a safe iterative editing loop

### Characteristics

- visible
- reactive
- sometimes transient
- should not be confused with accepted persistence

### Important rule

A previewed change is not necessarily a committed or accepted change.

---

## Ephemeral UI State

### Definition

Ephemeral UI State is short-lived interaction state used by the authoring experience.

### Examples

- current selection
- hovered node
- drag in progress
- resize handles
- focused inspector section
- expanded structure tree nodes
- guide visibility
- snap candidate state

### Characteristics

- local
- short-lived
- frequently changing
- not itself part of composition truth

### Important rule

Ephemeral UI State must not become the accidental source of domain truth.

---

## Runtime-Observed State

### Definition

Runtime-Observed State is runtime-derived information that the composer reads in order to understand or align with the actual rendered system.

### Examples

- visual bounds
- runtime node identifiers
- actual render tree relationships relevant to inspection
- diagnostics useful for alignment
- measured dimensions

### Purpose

This state helps the composer align with the real runtime but does not automatically become the authoring truth model.

### Important rule

Observed runtime state is informative, but not an excuse for uncontrolled runtime writes.

---

## State Ownership Summary

### Scene model owns

- baseline composition data
- draft composition data
- structural relationships among scene, layout, slots, widgets
- accepted scene metadata

### Interaction systems own

- selection
- hover state
- local manipulation state
- transient view/UI interaction states

### Runtime adapter layers own

- mapping between authoring concepts and runtime-observed facts
- runtime node/bounds lookups
- translation between render world and authoring world

### Mutation bridge owns

- validation and routing decisions about write-capable changes
- it does not own all state, but it governs sensitive transitions

---

## State Transition Model

A healthy editing flow should follow a disciplined progression:

1. user selects a target
2. user performs an action
3. action generates mutation intent
4. mutation is validated
5. draft state is updated
6. preview reflects draft
7. user compares or continues editing
8. user commits or discards
9. baseline is updated only after accepted commit semantics

This path should be legible in code and behavior.

---

## Commit Semantics

### Commit

Commit means the system now treats a previously in-progress change as accepted state for the relevant workflow.

### Important note

Commit does not necessarily mean “persisted everywhere forever” in the broadest platform sense. But it must mean that from the composer’s perspective, the change has passed from unaccepted draft to accepted state.

---

## Revert Semantics

### Revert

Revert means returning some scope of state to a previously accepted or previously captured state.

Possible scopes may include:

- selected entity reset
- current module reset
- whole draft discard
- snapshot restore

These scopes should remain explicit.

---

## Reset Semantics

Reset should be narrower than full discard when possible.

Examples:

- reset selected widget style
- reset a slot’s local visual treatment
- reset layout node adjustments
- reset current module contribution

The system should distinguish reset from full draft discard.

---

## State Invariants

The following invariants should hold:

1. Baseline and Draft are not silently the same thing.
2. Preview reflects Draft or pending state, not some hidden mix of unrelated data.
3. Ephemeral UI State does not overwrite domain truth directly.
4. Write-capable changes do not bypass validation.
5. Selection state does not define ownership or persistence.
6. Runtime-observed facts may inform authoring but do not replace the scene model.
7. Revert paths must remain coherent.

---

## Common State Failures to Avoid

- writing directly from UI controls into runtime-facing state with no draft layer
- storing composition truth inside React-local component state only
- merging selection and domain state until they cannot be separated
- pretending preview equals commit
- reusing debug runtime state as authoring truth
- losing the baseline, then pretending compare/revert still exists
- allowing mutation without target scope clarity

---

## Summary

The Live Scene Composer state model must distinguish Baseline State, Draft State, Preview State, Ephemeral UI State, and Runtime-Observed State. State clarity is not optional: it is what makes compare, revert, trust, and controlled authoring possible. The system should be built so that state categories remain understandable in code, behavior, and testing.
EOF

cat > "$DOCS_DIR/09_RUNTIME_MODEL.md" <<'EOF'
# 09_RUNTIME_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Runtime-facing behavior and the composer's relationship to the real runtime

---

## Purpose

This document defines how Live Scene Composer should relate to the runtime. It exists to prevent a recurring class of mistakes: treating the runtime as either irrelevant to authoring or as a free-for-all target for arbitrary writes.

The runtime matters deeply, but it must be engaged through disciplined boundaries.

---

## Runtime Model Summary

Live Scene Composer is built on top of the real runtime, but it is not allowed to own the runtime, rewrite the runtime’s architectural rules, or mutate runtime internals directly at will.

The composer must:

- observe enough runtime information to provide true live authoring
- align its visual editing experience with real rendered output
- route write-capable changes through runtime-mutation-bridge
- preserve separation between authoring intent and runtime effect

---

## Core Runtime Principle

The runtime must not depend on the composer.
The composer may depend on runtime capabilities only through controlled, bounded integration seams.

This is one of the most important architectural principles in the system.

---

## Runtime Relationship Types

The composer may have several kinds of relationship with runtime-facing systems.

### 1. Observation

Reading runtime-facing information such as:

- visual bounds
- render identifiers
- region mappings
- measured layout facts
- scene render state relevant to authoring alignment

Observation helps the composer stay accurate.

### 2. Presentation coupling

The canvas must show the real rendered result or a faithful runtime-backed representation. The composer is therefore presentation-coupled to the runtime outcome, even if the domain model is distinct.

### 3. Controlled write-capable interaction

When the composer initiates changes that affect runtime-facing state, those changes must pass through runtime-mutation-bridge.

This is the only acceptable write relationship.

---

## Runtime as Execution Environment, Not Ownership Target

The runtime is the environment in which the scene ultimately renders and behaves.
The composer is a client of this environment for authoring purposes.

The composer should not assume:

- unrestricted ownership of runtime state
- privilege to call arbitrary runtime internals
- license to infer stable architecture from current runtime implementation details

The runtime is an integration partner, not a dumping ground for authoring shortcuts.

---

## Runtime Observation Needs

To support quality authoring, the composer likely needs access to:

- element bounds and coordinates
- slot region mapping
- layer ordering information where relevant to selection or overlays
- scene render state for accurate preview
- stable references or adapters that map authoring entities to runtime instances

These reads should be routed through appropriate adapter or contract layers where possible.

---

## Runtime Write Model

The runtime write model must remain governed.

### Rule

If a composer action causes a write-capable effect on runtime-facing state, that action must go through **runtime-mutation-bridge**.

### Why

This enables:

- validation
- auditing
- policy enforcement
- safe mode / advanced mode decisions
- reversibility expectations
- clearer testing and reasoning

### Prohibited pattern

UI control -> direct runtime state mutation -> hope for the best

That pattern is banned.

---

## Runtime Adapter Seams

The runtime should be accessed through explicit adapter seams where needed.

Adapter seams may help with:

- mapping scene entities to runtime representations
- translating layout intents into runtime-friendly operations
- reading scene runtime facts
- applying validated mutation results to runtime-facing paths

Adapters are valuable because they preserve explicitness and make integration behavior testable.

---

## Preview Semantics in Runtime Context

Live authoring requires that preview feel real.
However, runtime-facing preview must remain semantically distinct from accepted commit.

The system must support the idea that:

- something can be visibly previewed
- without yet being accepted as baseline
- without silently becoming persistent accepted truth

If the runtime view cannot reflect that distinction, trust degrades.

---

## Runtime Failure Isolation

The runtime model must assume that authoring interactions can fail.

Failure examples:

- invalid mutation requests
- adapter mismatch
- stale runtime mapping
- broken widget rendering
- future custom widget execution failure
- unsupported preview transition

Expected response:

- fail clearly
- fail locally where possible
- preserve broader scene integrity
- preserve product shell stability
- avoid global collapse for local authoring errors

---

## Runtime Debug Console Relationship

Runtime Debug Console may inspect runtime internals more directly for diagnostics purposes, but that does not grant the composer the same rights.

The composer may reuse shared infrastructure from console-core, but must not inherit debug-specific mutation habits or diagnostic privilege as if it were authoring authority.

These are different products with different responsibilities.

---

## Runtime Modes and Safety

The runtime-facing behavior of the composer should be sensitive to mode.

### Safe Mode

Safe Mode should permit only bounded, validated, policy-approved authoring operations.

### Advanced Mode

Advanced Mode may enable more powerful behavior later, but only through deliberate, explicit expansion of the contract model. It should not become a loophole for bypassing architecture.

---

## Runtime Invariants

The following invariants must hold:

1. The runtime does not depend on the composer for its core functioning.
2. The composer does not write directly to runtime internals.
3. Runtime-observed facts may influence authoring but do not replace the scene model.
4. Preview and commit remain distinguishable.
5. Bridge validation remains the gate for write-capable runtime effect.
6. Failures in authoring should not globally destabilize the runtime.
7. Debug privileges do not automatically transfer to authoring flows.

---

## Runtime Anti-Patterns

The following are architecture failures:

- direct composer writes into runtime internals
- route bindings that mount authoring through debug-only flows
- using runtime inspection paths as authoring mutation paths
- treating observed render structure as the sole source of composition truth
- bypassing bridge validation because “it’s just UI”
- assuming advanced runtime knowledge is a substitute for explicit authoring contracts

---

## Summary

Live Scene Composer is runtime-aware and runtime-backed, but not runtime-owning. It must observe enough of the real runtime to make visual authoring true, while routing all write-capable changes through runtime-mutation-bridge. The runtime is a controlled integration partner, not an unrestricted authoring substrate.
EOF

cat > "$DOCS_DIR/10_MUTATION_MODEL.md" <<'EOF'
# 10_MUTATION_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation, Tooling
- Scope: Mutation semantics, governance, validation, and safe change flow

---

## Purpose

This document defines the mutation model for Live Scene Composer. It exists because mutations are where authoring intent becomes runtime-facing effect, and that transition is the most sensitive part of the system.

If mutation semantics are vague, safety becomes imaginary.
If mutation flows are hidden, debugging becomes expensive.
If mutation boundaries are bypassed, the product loses trust.

---

## Mutation Model Summary

A mutation is a typed request to change composition state.
The mutation model exists to make changes:

- explicit
- validated
- scoped
- attributable
- testable
- reversible when appropriate
- governable by mode and policy

All write-capable mutations affecting runtime-facing state must pass through **runtime-mutation-bridge**.

---

## Why a Mutation Model Exists

The composer is not allowed to rely on informal side effects or UI-driven direct writes. A mutation model exists to provide:

- contract clarity
- architecture safety
- operational visibility
- mode-aware governance
- consistent preview / commit semantics
- structured error handling
- future extension without chaos

---

## Mutation Lifecycle

The intended lifecycle of a mutation is:

1. authoring action occurs
2. mutation intent is created
3. source and target are identified
4. mutation type is resolved
5. mode policy is checked
6. validation runs
7. mutation is either rejected or accepted
8. accepted mutations update draft / preview / accepted state as appropriate
9. inverse or revert semantics are recorded where applicable
10. downstream runtime-facing effect occurs only through the governed path

This sequence should be legible in code and in test expectations.

---

## Mutation Categories

### 1. Scene-level mutations

Examples:

- scene metadata updates
- scene-level theme changes
- scene-level baseline/draft transitions

### 2. Layout mutations

Examples:

- move layout node
- resize layout node
- reorder layout node
- adjust layout constraints

### 3. Slot mutations

Examples:

- create slot
- change slot properties
- adjust slot acceptance policy
- move slot association in layout contexts

### 4. Widget mutations

Examples:

- insert widget
- remove widget
- move widget between valid slots
- update widget props
- update widget style
- toggle widget visibility or lock state

### 5. Draft workflow mutations

Examples:

- discard draft
- commit draft
- reset selected element
- reset current module contribution

---

## Mutation Scope

Every mutation should carry an explicit scope.

### Possible scopes

- preview-only
- commit-capable
- accepted-state transition
- local reset
- full draft discard

The exact names may evolve, but the idea must remain explicit.

### Why scope matters

Without scope clarity, the system cannot reliably distinguish:

- temporary visual feedback
- accepted authoring decisions
- reset behavior
- persistence intent

---

## Mutation Source

Every mutation should identify its source.

Examples:

- live-scene-composer
- specific composer module
- future bounded custom widget API wrapper

This matters for:

- policy
- validation
- auditing
- debugging
- safe permissioning

---

## Mutation Target

Every mutation should identify its target.

Possible targets include:

- scene
- layout node
- slot
- widget
- draft state
- module-specific contribution

A mutation without a clear target is a design smell.

---

## Validation Model

A mutation should not be applied just because it was requested.

Validation may include:

- source validation
- target existence validation
- policy allowlist checks
- mode checks
- slot/widget compatibility checks
- structural validity checks
- preview vs commit rules
- reversibility expectations
- future capability checks for custom widget requests

Validation is one of the reasons runtime-mutation-bridge exists.

---

## runtime-mutation-bridge Role

runtime-mutation-bridge is the enforcement layer for write-capable mutation flow.

It should be responsible for:

- receiving typed mutation requests
- checking source and target validity
- enforcing allowed mutation types
- deciding whether the action is legal in Safe Mode or Advanced Mode
- routing approved changes to appropriate adapters or downstream state transitions
- rejecting invalid or unsafe changes clearly

The bridge is not optional infrastructure.
It is the safety boundary.

---

## Safe Mode Mutation Policy

Safe Mode should allow only bounded and strongly understandable mutations.

Typical Safe Mode candidates:

- text changes
- typography updates
- background and color changes
- approved layout adjustments
- widget insertion from valid prefabs
- widget property changes within contract limits
- style changes that remain within governed boundaries
- draft reset / discard / commit actions

Safe Mode should not become a polite label for unrestricted write power.

---

## Advanced Mode Mutation Policy

Advanced Mode may eventually enable more powerful changes, but this mode must still remain explicit and governed.

Advanced Mode should not mean:

- direct runtime access
- policy bypass
- untyped changes
- undocumented mutation flows

Advanced Mode is an expansion of explicit authority, not the absence of authority.

---

## Reversibility

Mutations should explicitly state or imply whether they are reversible.

Reversibility matters for:

- undo / redo
- local reset
- module rollback
- user trust
- validation rigor

Not all future mutations must be perfectly reversible, but the system should know which are and which are not.

---

## Error Semantics

Rejected or failed mutations should fail clearly.

Expected behaviors:

- reject with meaningful reason
- preserve baseline and broader draft integrity
- avoid silent partial corruption
- avoid hidden fallback writes
- surface actionable information for debugging and validation

A failed mutation should never quietly mutate unrelated state.

---

## Mutation Record Shape

The exact type shape may evolve, but a healthy mutation contract should include concepts like:

- mutation id
- source
- type
- mode
- scope
- target
- payload
- timestamp
- reversibility metadata

These concepts help the bridge and validation system reason about change.

---

## Mutation Anti-Patterns

The following are unacceptable:

- direct UI control mutating runtime internals
- untyped “update anything” payloads as the default strategy
- hidden side effects that write outside the declared target
- preview actions silently becoming accepted state
- allowing custom widget code to bypass mutation governance
- using route-level hacks instead of mutation contracts
- treating mode as a UI label rather than a policy input

---

## Minimum MVP Mutation Direction

The MVP should start small and disciplined.

A sensible initial mutation surface would likely include:

- update scene look or visual context
- move / resize / reorder layout node
- insert widget from prefab into valid slot
- update widget props
- update widget style
- remove widget
- discard draft
- commit draft
- reset selected element

This is sufficient to make the product useful without creating a giant mutation universe on day one.

---

## Summary

The mutation model is the governance center of Live Scene Composer. Every meaningful write-capable change should be typed, scoped, validated, and routed through runtime-mutation-bridge. Mutation semantics must remain explicit so that preview, commit, revert, safety modes, and future extensibility all remain coherent and trustworthy.
EOF

echo "[OK] Generated Part 1 docs in: $DOCS_DIR"
echo "[OK] Files created:"
ls -1 "$DOCS_DIR"/01_PROJECT_OVERVIEW.md \
      "$DOCS_DIR"/02_PRODUCT_VISION.md \
      "$DOCS_DIR"/03_GOALS_AND_NON_GOALS.md \
      "$DOCS_DIR"/04_CORE_CONCEPTS.md \
      "$DOCS_DIR"/05_SYSTEM_ARCHITECTURE.md \
      "$DOCS_DIR"/06_SYSTEM_BOUNDARIES.md \
      "$DOCS_DIR"/07_DOMAIN_MODEL.md \
      "$DOCS_DIR"/08_STATE_MODEL.md \
      "$DOCS_DIR"/09_RUNTIME_MODEL.md \
      "$DOCS_DIR"/10_MUTATION_MODEL.md