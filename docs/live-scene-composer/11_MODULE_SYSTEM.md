# 11_MODULE_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation
- Scope: Module architecture, boundaries, lifecycle, and governance for Live Scene Composer

---

## Purpose

This document defines the module system for Live Scene Composer. Its purpose is to ensure that feature growth happens through bounded, removable, testable units rather than through uncontrolled expansion of product logic across the codebase.

The module system is not a convenience pattern. It is one of the core architectural defenses that keeps the Composer from becoming a monolith.

---

## Why a Module System Exists

Live Scene Composer is expected to grow across multiple domains:

- layout
- typography
- backgrounds
- effects
- charts
- prefabs
- structure tooling
- snapshots
- future themes and variants
- future bounded custom widget support

Without a module system, these concerns tend to collapse into a single application layer, which creates:

- hidden coupling
- unbounded imports
- high blast radius changes
- difficult removability
- accidental ownership confusion
- weak validation surfaces

A module system exists to make growth governable.

---

## Module System Goals

The module system must achieve the following:

1. allow feature growth without collapsing boundaries
2. make feature ownership explicit
3. support registration discipline
4. support selective enablement or removal
5. provide a clean place for feature-specific panels, actions, and schema
6. support validation and cleanup
7. reduce system-wide breakage when one module fails

---

## Module Definition

A module is a bounded feature unit that extends the Composer through approved seams.

A module may contribute:

- inspector sections
- canvas tools or overlays
- structure actions
- widget-type support
- slot-aware behaviors
- mutation helpers
- validation hooks
- local state or lifecycle behavior
- feature-specific configuration or schema

A module is not just a folder of code. It is a declared, governed unit of capability.

---

## Module Design Principles

### 1. Modules must be explicit

A module should have clear identity, declared capabilities, clear registration behavior, and clear ownership.

### 2. Modules must remain bounded

A module should only depend on what it truly needs. It should not reach across the system and acquire broad authority by convenience.

### 3. Modules must be removable

If a module proves unstable, irrelevant, or poorly designed, it should be possible to disable or remove it without dismantling the product.

### 4. Modules must fail locally where possible

A broken module should not crash the whole Composer shell or corrupt unrelated authoring state.

### 5. Modules must obey product boundaries

Modules are part of Live Scene Composer. They are not allowed to reintroduce runtime-debug coupling or bypass mutation governance.

---

## Module Categories

The system may support multiple kinds of modules.

### Authoring modules

Examples:

- typography module
- backgrounds module
- chart appearance module
- layout tools module
- effects module

These primarily extend editing capability.

### Structural modules

Examples:

- structure tree helpers
- slot management helpers
- selection refinement tooling

These primarily extend scene understanding or composition structure.

### Widget capability modules

Examples:

- text widget support
- chart widget support
- KPI widget support
- image widget support

These help the system handle widget-specific authoring behavior.

### Workflow modules

Examples:

- compare/revert tools
- snapshots
- presets
- future variants

These extend the authoring workflow around change management and reuse.

---

## What a Module May Own

A module may own:

- feature-specific UI surfaces
- feature-specific local state
- feature-specific validation rules
- feature-specific mutation wrappers
- feature-specific defaults and schemas
- feature-specific cleanup logic

A module should not quietly become the owner of core product architecture or unrelated feature domains.

---

## What a Module Must Not Own

A module must not own:

- global mutation bypass
- shared infrastructure responsibilities that belong in console-core
- the entire scene model
- runtime-debug-only concerns
- unrestricted runtime access
- unrelated module state by stealth
- product-wide registry power without approval

---

## Module Registration

Modules should register through explicit Composer registration seams.

Registration should be capable of describing:

- module identity
- module version
- module capabilities
- inspector contributions
- widget or slot relevance
- required dependencies
- optional dependencies
- cleanup hooks
- enablement flags
- safe mode compatibility
- advanced mode compatibility

Module registration must be deterministic and testable.

---

## Module Lifecycle

A healthy module lifecycle should include:

1. declaration
2. registration
3. activation
4. runtime contribution
5. disposal / cleanup

The exact mechanics may vary, but lifecycle clarity matters because dynamic or optional modules otherwise become a source of leaks and inconsistent behavior.

### Declaration

The module states what it is and what it contributes.

### Registration

The system decides whether the module may participate in the current Composer environment.

### Activation

The module becomes live and can contribute approved behaviors or surfaces.

### Disposal

The system removes the module cleanly and tears down any local state, subscriptions, or ephemeral UI effects.

---

## Module Manifest Expectations

Each module should have a declared manifest or equivalent typed registration structure that answers:

- what is this module called
- what category is it
- what capabilities does it contribute
- what parts of the system can it extend
- what prerequisites does it need
- what modes can it run in
- what cleanup is required
- what validation should apply if it changes

The goal is to make module behavior explicit instead of tribal.

---

## Safe Mode and Module Participation

Not all modules need the same authority.

Some modules are Safe Mode compatible by default, such as:

- typography
- backgrounds
- simple layout tools
- visual effects within policy
- prefab browsing

Some future modules may require stronger gating and should not appear as default capabilities.

The module system should be able to distinguish:

- always-safe modules
- conditionally safe modules
- advanced-only modules
- disabled modules

---

## Failure Isolation

Failure isolation must be a design requirement.

Expected behavior:

- a broken inspector section from one module should not blank the entire inspector
- a widget capability module failure should degrade locally
- a module should not corrupt unrelated state on activation failure
- the Composer shell should remain stable if a non-core module fails

This is one of the main reasons the system is modular at all.

---

## Dependency Discipline

Modules should depend inward on allowed Composer seams, not outward into unrelated system internals.

Preferred dependency style:

- module -> composer contracts
- module -> scene model contracts
- module -> mutation wrappers
- module -> shared UI primitives where appropriate

Disallowed dependency style:

- module -> runtime internals directly
- module -> runtime-debug-console
- module -> hidden route-binding hacks
- module -> sibling module private internals without explicit contract

---

## Minimum Initial Modules

The early Composer should likely begin with a modest module set such as:

- layout module
- typography module
- backgrounds module
- effects module
- chart appearance module
- prefab library module

This gives strong authoring value while preserving manageable scope.

---

## Module System Anti-Patterns

The module system must reject:

- modules with no declared ownership
- modules that directly mutate runtime state
- one module importing everything and behaving like a hidden monolith
- “temporary” modules that bypass registration
- putting feature logic into console-core because multiple people use it
- modules that cannot be removed because they secretly own core flows

---

## Validation Expectations

The module system should support:

- registration tests
- allowed dependency checks
- module manifest checks
- enable/disable checks
- failure-isolation tests
- mode compatibility checks

This is how the module system becomes a real architecture tool rather than a naming convention.

---

## Summary

The Live Scene Composer module system is the mechanism by which the product grows without collapsing. Modules must be explicit, bounded, removable, and governable. They should contribute capability through approved seams, remain subject to dependency discipline, and fail locally where possible. A healthy module system is one of the strongest defenses against long-term product and architecture decay.
