# 28_SECURITY_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Security, Validation
- Scope: Safety, authority boundaries, restricted capabilities, and system hardening principles

---

## Purpose

This document defines the security and authority model for Live Scene Composer. It exists because a live authoring product that interfaces with runtime-facing state can become dangerous very quickly if permissions, boundaries, and execution surfaces are not governed carefully.

Security here includes both traditional safety concerns and architectural authority control.

---

## Security Model Summary

The security model for Live Scene Composer is based on:

- explicit authority boundaries
- typed mutation governance
- bounded extension surfaces
- restricted capability exposure
- clear sibling product separation
- safe defaults
- containment of failures and privileges

The system is not a trusted freeform scripting shell.
It is a governed authoring environment.

---

## Core Security Principles

### 1. Least authority

Give each subsystem only the authority it needs.

### 2. Explicit write boundaries

All write-capable runtime-facing changes from the Composer must go through `runtime-mutation-bridge`.

### 3. Safe defaults

Normal operation should occur in Safe Mode with bounded capabilities.

### 4. No hidden privilege inheritance

Diagnostic power from Runtime Debug Console must not quietly transfer into the Composer.

### 5. Bounded extension

Modules and future custom widgets must not receive unrestricted access by default.

### 6. Local containment

A failure or misuse in one area should not automatically compromise the rest of the product.

---

## Security-Relevant Boundaries

The most security-relevant top-level boundaries are:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`

The most sensitive among them for authority control is `runtime-mutation-bridge`.

The most sensitive for extension control is future custom widget support.

---

## Authority Model

Authority in the system should be explicit and layered.

### Shared infrastructure authority

`console-core` should have infrastructure authority, not product-specific mutation authority.

### Diagnostic authority

`runtime-debug-console` may have stronger inspection capabilities for diagnostics, but that must not imply authoring write authority.

### Authoring authority

`live-scene-composer` may create mutation intent, but should not directly apply unrestricted runtime writes.

### Mutation authority

`runtime-mutation-bridge` governs whether requested write-capable actions are allowed, and under what mode and policy.

---

## Safe Mode

Safe Mode should be the default authority posture.

It should allow:

- bounded visual changes
- approved layout operations
- approved text and style edits
- valid prefab insertions
- safe draft workflows

It should not allow:

- unrestricted scripting
- arbitrary runtime writes
- vague untyped privileged actions
- extension mechanisms that bypass policy

Safe Mode exists to protect both the product and the user.

---

## Advanced Mode

Advanced Mode may eventually enable more powerful capabilities, but it must still remain explicit, typed, and governed.

Advanced Mode should not be:

- an architecture bypass
- a hidden admin mode for unsafe writes
- a broad permission shortcut

If Advanced Mode exists, it must remain legible and testable.

---

## Mutation Security

Mutation security depends on the bridge enforcing:

- source validation
- target validation
- allowed command types
- mode policy
- reversibility or acceptance semantics as relevant
- adapter routing discipline

This is one of the central security mechanisms of the product.

---

## Module Security

Modules should operate through declared capabilities and approved SDK surfaces.

A module must not:

- access arbitrary runtime internals
- widen its own authority silently
- register hidden privileged actions
- act as a shadow bridge
- access sibling product internals by convenience

Modules are extension units, not privilege loopholes.

---

## Custom Widget Security

Custom widgets are a major security surface and must be tightly bounded.

The sandbox model should enforce:

- bounded region rendering
- restricted API surface
- no filesystem access
- no unrestricted DOM or global access
- no uncontrolled runtime mutation
- local failure isolation
- explicit capability declaration

Custom widgets are valuable only if they remain safer than raw code injection.

---

## Data Access Security

Composer-facing data access should remain scoped and intentional.

The system should avoid:

- exposing unrelated global state widely
- giving extension points broad hidden data access
- letting runtime mappings become a side-channel for unrestricted reads or writes

Data access should be designed, not leaked.

---

## Path and Dependency Security

Path discipline is also part of the security posture.

The system should reject:

- legacy or ambiguous shared-core paths
- forbidden sibling imports
- hidden route-binding privilege shortcuts
- accidental coupling that widens authority

Bad dependency direction is often a security problem in architecture clothing.

---

## Failure Security

When a sensitive operation fails, the system should fail in a way that:

- preserves state integrity
- does not widen authority
- does not silently fall back to unsafe paths
- remains diagnosable

A rejection followed by an unsafe fallback is a security failure.

---

## Security Anti-Patterns

The system must reject:

- direct runtime write access from UI layers
- broad “admin” helpers with unclear scope
- modules that mutate anything because they can import it
- custom widget paths with unrestricted power
- hidden privilege transfer from debug tooling
- mode toggles that do not actually change authority rules

---

## Summary

The security model for Live Scene Composer is built on bounded authority, explicit mutation governance, safe defaults, and restricted extension surfaces. The product must remain powerful without becoming permissive by accident. Security here is not only about hostile misuse; it is also about preventing the system from becoming architecturally unsafe.
