# 12_MODULE_SDK

## Document Status

- Status: Canonical
- Audience: Engineering, Architecture, Tooling
- Scope: Module-facing APIs, registration contracts, and contribution surfaces

---

## Purpose

This document defines the shape and intent of the Module SDK for Live Scene Composer. The SDK is the formal interface between the Composer platform and feature modules.

Its purpose is to answer a simple but critical question:
How may modules extend the Composer without destabilizing it?

---

## Why an SDK Exists

A module system without an SDK devolves into informal imports, private assumptions, and duplicated patterns. The Module SDK exists so that modules can be built against explicit, stable seams rather than against whichever internal component happened to be available at the time.

The SDK is what turns modularity from aspiration into practice.

---

## SDK Goals

The Module SDK should:

1. provide a stable registration seam
2. define contribution points explicitly
3. limit what modules can see and do
4. reduce coupling to internal application implementation details
5. make future refactoring safer by preserving a formal extension contract
6. support tooling and validation
7. allow safe feature growth without encouraging product sprawl

---

## SDK Scope

The Module SDK should cover:

- module identity and manifest contracts
- registration contracts
- capability declarations
- contribution APIs
- context access rules
- mutation helper access
- cleanup lifecycle
- mode compatibility
- validation expectations

It should not expose unrestricted access to the full Composer internals.

---

## Core SDK Principle

Modules should be able to do useful work through a narrow, explicit surface.
They should not need privileged access to accomplish normal extension tasks.

A powerful narrow API is healthier than a vague giant one.

---

## Manifest Contract

A module should declare a manifest or equivalent typed descriptor that includes concepts such as:

- id
- display name
- version
- category
- capabilities
- supported targets
- safe mode compatibility
- advanced mode compatibility
- dependencies
- optional dependencies

The manifest exists so the system can reason about the module before loading it deeply.

---

## Registration Contract

The registration contract should answer:

- what the module contributes
- where the contributions belong
- what lifecycle hooks are required
- what contexts it may access
- what cleanup must occur on disable/unmount
- what validations are needed

Registration should be declarative and inspectable.

---

## Expected Contribution Types

A module may contribute some combination of the following.

### Inspector contributions

A module may contribute inspector sections or controls for relevant targets.

Examples:

- typography controls for text widgets
- background controls for containers or scenes
- chart appearance controls for chart widgets

### Canvas contributions

A module may contribute overlays, guides, handles, or interaction aids relevant to its domain.

These should remain bounded and not become hidden global behavior.

### Structure contributions

A module may contribute structure actions, icons, metadata, or structure-specific editing affordances.

### Validation contributions

A module may contribute validation rules or constraints relevant to its domain.

### Mutation wrapper contributions

A module may expose typed helper calls that route through approved mutation channels, rather than doing direct writes.

### Widget support contributions

A module may enhance authoring support for specific widget types.

---

## Module Context

The SDK may expose a module context object or equivalent, but that context must be carefully limited.

A healthy module context may include:

- current selection
- current scene id or scene reference
- read-only access to relevant scene model views
- approved mutation request helpers
- registration-time extension surfaces
- mode awareness
- logging or diagnostics hooks appropriate for the module
- cleanup helpers

A healthy module context must not include:

- unrestricted runtime internals
- direct low-level bridge bypass handles
- write-anything methods
- hidden backdoors to sibling products
- full ownership of unrelated module state

---

## Mutation Access Through SDK

The SDK should not give modules direct raw mutation authority.
Instead, it should provide one or more safe patterns such as:

- typed mutation helper factories
- scoped mutation request builders
- target-aware helper wrappers

The intent is that modules remain productive without bypassing runtime-mutation-bridge or inventing their own mutation semantics.

---

## Lifecycle Hooks

The SDK should support a small, explicit lifecycle.

Typical lifecycle hooks may include:

- register
- activate
- dispose

Optional lifecycle concepts may include:

- onSelectionChanged
- onModeChanged
- onSceneChanged

These should remain bounded and not turn into a giant event soup.

---

## Cleanup Expectations

The SDK must make cleanup part of the module contract.

Modules should clean up:

- subscriptions
- overlays
- temporary state
- listeners
- timers
- structure decorations
- canvas contributions

A module that contributes to the environment but cannot clean up after itself is not production-ready.

---

## Mode Awareness

The SDK should allow modules to declare and inspect mode compatibility.

Examples:

- safe-only
- safe-and-advanced
- advanced-only

This matters because not every module should be active under all authority levels.

---

## Versioning and Compatibility

The SDK should be versioned or at least compatibility-conscious.

The system should be able to answer:

- what SDK version a module targets
- whether a manifest is still compatible
- whether a module relies on deprecated extension points

Even if formal semantic versioning comes later, the concept must be anticipated now.

---

## Validation and Tooling

The SDK should be designed so tooling can validate:

- required manifest fields
- illegal contribution surfaces
- mode compatibility declarations
- missing cleanup
- dependency rule violations
- unsupported capabilities

The easier the SDK is to validate, the more safely the module ecosystem can grow.

---

## What the SDK Must Not Become

The SDK must not become:

- a disguised full internal API export
- a convenience portal to unstable product internals
- a mutation bypass surface
- a place where permissions are assumed instead of declared
- a dumping ground for arbitrary helper methods

If the SDK becomes “just import whatever you need,” it has failed.

---

## Minimal Early SDK Direction

The initial SDK can stay focused.

A small but strong v1 SDK might provide:

- module manifest type
- registration entry point
- inspector contribution API
- selection-aware context
- typed mutation helper access
- cleanup registration
- mode inspection

That is enough to support real modules without over-designing the system.

---

## Summary

The Module SDK is the formal extension contract between Live Scene Composer and its modules. It should provide stable, narrow, useful APIs for registration, context access, inspector contribution, mutation helpers, and cleanup—without exposing unrestricted internals. A strong SDK is what allows modularity to scale without turning into chaos.
