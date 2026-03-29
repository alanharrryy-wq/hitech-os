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
