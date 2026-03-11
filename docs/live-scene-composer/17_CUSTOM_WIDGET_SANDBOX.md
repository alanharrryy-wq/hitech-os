# 17_CUSTOM_WIDGET_SANDBOX

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Security, Validation
- Scope: Bounded custom widget execution, sandbox model, and safe extension rules

---

## Purpose

This document defines the sandbox model for custom widgets in Live Scene Composer. It exists because custom extension is valuable, but unrestricted code inside a live authoring and runtime-aware system is one of the fastest ways to destroy safety, trust, and maintainability.

Custom widgets matter, but they must be bounded.

---

## Sandbox Model Summary

A custom widget is a widget type that renders inside an approved Slot using a restricted API and an isolated execution model.

The sandbox must ensure that a custom widget:

- renders only within its designated region
- cannot freely mutate the system
- cannot escape into unrestricted global surfaces
- fails locally rather than globally
- uses only approved capabilities
- remains compatible with the mutation and validation model

---

## Why a Sandbox Exists

Without a sandbox, custom widgets become a loophole around the architecture.

A sandbox exists to prevent:

- direct access to runtime internals
- arbitrary filesystem access
- unrestricted DOM or global state access
- silent bridge bypass
- one broken custom widget crashing the whole scene
- accidental or malicious side effects across the broader product

The sandbox is not optional polish.
It is the condition under which custom widgets can exist safely.

---

## Core Sandbox Principles

### 1. Region-bounded rendering

A custom widget must render only within the bounds of its host slot.

### 2. Capability-based access

A custom widget should only be able to do what it has been explicitly allowed to do.

### 3. Local failure isolation

If a custom widget fails, the failure should remain local to that widget or slot region.

### 4. No direct runtime mutation authority

A custom widget must not gain unrestricted write access to runtime-facing state.

### 5. No silent policy bypass

The custom widget path is not allowed to become a loophole around the rest of the system.

---

## Custom Widget Hosting Model

The correct hosting model for custom widgets is:

- an approved Slot
- bounded rendering surface
- restricted execution environment
- approved API surface
- local error boundary
- explicit lifecycle

The key concept is a **Custom Widget Slot** or equivalent policy-approved slot configuration.

---

## What a Custom Widget May Do

A custom widget may be allowed to do bounded things such as:

- render visual content within its region
- read approved scoped data
- request local resize within policy
- apply local visual treatment through approved APIs
- render approved chart or visual primitives through safe wrappers

The exact API may evolve, but it must remain capability-based.

---

## What a Custom Widget Must Not Do

A custom widget must not:

- access the filesystem
- access unrestricted engine internals
- mutate arbitrary runtime state directly
- escape its slot bounds
- mutate unrelated widgets
- mutate the global DOM freely
- call privileged private interfaces by accident or by convenience

These restrictions are the foundation of the sandbox.

---

## Safe API Philosophy

The system should expose safe, purpose-specific APIs rather than raw power.

Examples of safe conceptual APIs may include:

- set local background
- set local text
- render approved chart
- request bounded resize
- read approved scoped data
- request approved effects

The right question is not “how much can a custom widget do?”
The right question is “what specific safe things should a custom widget be able to do well?”

---

## Sandbox Execution Strategy

The concrete technical mechanism may vary, but the execution strategy should aim for:

- isolation
- message-based communication where appropriate
- explicit lifecycle management
- local error boundaries
- capability allowlists
- controlled resource access

Common strategies may involve iframe-like or worker-like isolation patterns depending on product constraints, but the architecture should remain faithful to the principles above.

---

## Custom Widget Identity and Spec

A custom widget should be defined through a spec or manifest that includes concepts such as:

- custom widget id
- name
- api version
- entry point or render definition
- declared capabilities
- sandbox restrictions
- compatibility requirements

The system should know what it is loading before it loads it.

---

## Lifecycle Expectations

A custom widget should have a bounded lifecycle such as:

1. spec resolution
2. policy validation
3. slot compatibility check
4. activation inside sandbox
5. rendering within bounds
6. local event or data interaction through approved API
7. local disposal and cleanup

Custom widgets must not become immortal background processes.

---

## Data Access

Custom widgets may need data, but data access must remain scoped.

Approved data access should prefer:

- read-only scoped data
- approved queries or resolved data contracts
- explicit capability gating

Disallowed data access includes:

- arbitrary global data reads
- hidden access to unrelated product state
- secret backdoors into runtime internals

---

## Mutation Interaction

If custom widgets need to request changes, they should do so through a bounded request surface that remains subject to the broader mutation model.

A custom widget should not receive unrestricted direct mutation authority.
Requests from custom widgets should remain:

- typed
- scoped
- validated
- policy-aware

This keeps custom extension compatible with the overall system architecture.

---

## Failure Isolation

The system must assume that custom widgets will sometimes fail.

Failure handling should aim for:

- local rendering fallback
- visible but contained failure state
- cleanup of widget-specific resources
- preservation of shell and scene stability
- no unrelated state corruption

This is one of the most important reasons to sandbox them at all.

---

## MVP Direction

For an early Composer MVP, custom widgets should remain intentionally constrained.

A reasonable MVP posture is:

- define the concept
- define slot policy support
- define safe spec shape
- define restricted API intent
- delay broad authoring/editor surfaces for custom code until the core system is stable

This prevents custom widgets from dominating the early product before the foundation is sound.

---

## Sandbox Anti-Patterns

The sandbox model must reject:

- arbitrary code execution in the main application context
- unrestricted DOM access
- direct bridge bypass
- custom widgets that can mutate anything because “they’re advanced”
- no-capability, do-anything extension models
- custom widget failures that crash the whole composer

---

## Summary

The Custom Widget Sandbox exists to let Live Scene Composer support extension without sacrificing safety. Custom widgets must render inside bounded slot regions, use restricted APIs, fail locally, and remain subject to capability-based control. The sandbox is what makes custom extension viable instead of reckless.
