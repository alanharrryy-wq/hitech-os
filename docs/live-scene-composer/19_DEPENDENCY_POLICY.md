# 19_DEPENDENCY_POLICY

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation
- Scope: Allowed and forbidden dependency relationships across the core system boundaries

---

## Purpose

This document defines the dependency policy for Live Scene Composer and its sibling boundaries. It exists because architecture boundaries are only meaningful if dependency direction is explicit and enforceable.

A dependency policy turns “please keep this clean” into something reviewable and testable.

---

## Policy Summary

The system must preserve a small number of high-value top-level boundaries:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`
- runtime-facing integration areas such as `pitch/*`
- scene-related integration areas such as `scene-studio/*`

The policy defines which of these may depend on which others, and under what conditions.

---

## Dependency Principles

### 1. Shared infrastructure must stay shared

`console-core` is the only shared infrastructure layer and must not absorb product-specific logic.

### 2. Sibling products must not collapse into one another

`runtime-debug-console` and `live-scene-composer` are sibling products and should not import or register each other’s product logic.

### 3. Write-capable authority must remain explicit

`live-scene-composer` must not take direct runtime write shortcuts.
Write-capable flows must go through `runtime-mutation-bridge`.

### 4. Adapters are better than accidental privilege

Where integration is needed, explicit adapter seams are preferred over direct low-level imports.

### 5. Convenience is not a dependency policy

A dependency is not allowed simply because it saves time today.

---

## Top-Level Allowed Dependency Matrix

### console-core

May depend on:

- stable low-level shared UI/utilities
- generic shared internal primitives appropriate to repo conventions

Must not depend on:

- `runtime-debug-console`
- `live-scene-composer`
- product-specific authoring logic
- product-specific debug logic
- `runtime-mutation-bridge` product semantics

Reason:
`console-core` must remain product-neutral shared infrastructure.

---

### runtime-debug-console

May depend on:

- `console-core`
- approved runtime-facing read/diagnostic integration seams
- approved debug-oriented helpers and contracts

Must not depend on:

- `live-scene-composer` product logic
- composer module registration
- composer widget/slot/prefab systems
- composer-specific authoring flows

Reason:
Debug tooling must remain diagnostics-oriented and not become an editor host.

---

### live-scene-composer

May depend on:

- `console-core`
- `runtime-mutation-bridge`
- approved adapter seams into runtime-facing or scene-facing systems
- its own internal scene/layout/slot/widget/module contracts

Must not depend on:

- `runtime-debug-console`
- debug-only product internals
- direct low-level runtime write paths that bypass the bridge
- hidden route-binding shortcuts

Reason:
The Composer is the authoring product and must preserve both sibling separation and mutation discipline.

---

### runtime-mutation-bridge

May depend on:

- typed contracts
- policy helpers
- adapter seams required to route approved changes
- approved validation helpers

Must not depend on:

- broad Composer UI internals
- Runtime Debug Console product logic
- arbitrary runtime internals without explicit adapter or contract purpose
- convenience imports that collapse its role into a generic shared service

Reason:
The bridge is a mutation governance boundary, not a broad application layer.

---

### pitch/* or runtime-facing systems

May depend on:

- their own runtime internals
- approved shared utilities
- explicit adapter contracts where needed

Must not depend on:

- `live-scene-composer` as a required core dependency
- composer UI internals as runtime prerequisites

Reason:
The runtime must not become dependent on the Composer.

---

### scene-studio/* or scene-related systems

May depend on:

- approved scene-related contracts
- approved adapters
- their own product concerns

Must not depend on:

- hidden Composer-only assumptions unless made explicit through stable integration contracts

Reason:
Scene-related systems may integrate with the Composer ecosystem, but should not collapse into it by accidental import drift.

---

## Gray Areas Requiring Care

Some relationships are possible but require deliberate design.

### Composer to runtime observation

The Composer may need read-oriented adapters for bounds, render mapping, or scene runtime state relevant to authoring.
This must be bounded and should not silently become write authority.

### Bridge to runtime adapters

The bridge may need adapter-level knowledge to route approved changes.
These adapters should remain explicit and not evolve into raw unrestricted internals.

### Shared contracts

Some low-level contracts may be shared, but only if they are genuinely shared.
A “shared” contract that exists only because one product imported another’s internals is not healthy sharing.

---

## Forbidden Dependency Patterns

The following are explicitly forbidden:

1. `runtime-debug-console` importing composer product logic
2. `live-scene-composer` importing runtime-debug product logic
3. direct composer-to-runtime write paths outside `runtime-mutation-bridge`
4. `console-core` becoming a container for product-specific concerns
5. duplicate shared-core paths or aliases that reintroduce ambiguity
6. route-binding shortcuts that mount or wire composer through debug paths
7. module code importing unrelated private internals because they happened to be nearby

---

## Dependency Review Questions

When reviewing a dependency change, ask:

1. Which top-level boundary owns this code?
2. Which boundary is it importing from?
3. Is that relationship allowed, adapter-based, or forbidden?
4. Is this read-oriented, write-oriented, or mixed?
5. Is there a more explicit seam that should exist instead?
6. Does this make future wiring easier or more dangerous?

These questions should become habitual.

---

## Enforcement Recommendations

The dependency policy should be reinforced through:

- architecture guard rules
- focused regression tests
- allowed-dependency documentation
- protected-node review expectations
- code review discipline
- module registration checks

Documentation alone is not enough.

---

## Legacy Path Discipline

Legacy shared-core path ambiguity must be blocked.
Only canonical shared infrastructure paths should remain active.

The system should fail verification if obsolete or duplicate shared-core paths are reintroduced.

This matters because path ambiguity creates hidden architecture drift very quickly.

---

## Summary

The dependency policy preserves the integrity of the Live Scene Composer ecosystem by making dependency direction explicit. `console-core` remains the only shared infrastructure layer. `runtime-debug-console` and `live-scene-composer` remain siblings. `runtime-mutation-bridge` remains the explicit write boundary. Runtime-facing systems do not become Composer dependents. These rules are central to long-term architecture health.
