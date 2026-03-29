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
