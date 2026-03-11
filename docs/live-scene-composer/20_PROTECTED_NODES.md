# 20_PROTECTED_NODES

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation, Reviewers
- Scope: High-impact files, contracts, and seams that require elevated care

---

## Purpose

This document defines the concept of protected nodes for Live Scene Composer and related boundaries. Protected nodes are high-impact files, contracts, directories, or seams whose changes can create disproportionate architectural, behavioral, or integration risk.

The goal is not to freeze the system.
The goal is to make high-impact change visible and deliberate.

---

## What Is a Protected Node

A protected node is any file, contract, seam, or architectural surface that has unusually high leverage over:

- dependency direction
- mutation authority
- scene model integrity
- module registration
- runtime integration
- product boundary preservation
- system-wide safety or trust

Changes to protected nodes should receive stronger review and validation than ordinary feature work.

---

## Why Protected Nodes Matter

Large systems fail less often because a random button changed and more often because a foundational seam drifted silently.

Protected nodes help the team answer:

- what should not be changed casually
- what requires stronger validation
- what carries large impact cones
- what future workers must treat carefully

They are a governance tool, not a bureaucratic ritual.

---

## Protected Node Categories

The system should treat the following categories as protected by default.

### 1. Shared infrastructure boundaries

Examples:

- `console-core` shell primitives
- `console-core` registry foundations
- `console-core` contracts
- `console-core` lifecycle primitives

Why protected:
These affect both sibling products and can create broad architecture drift quickly.

---

### 2. Mutation governance boundaries

Examples:

- `runtime-mutation-bridge/contract.ts`
- validation rules in bridge logic
- mutation policy helpers
- source/target validation seams

Why protected:
These define who may change what and how, and therefore directly affect safety.

---

### 3. Scene composition contracts

Examples:

- scene model contracts
- slot contracts
- widget contracts
- layout contracts
- prefab contracts

Why protected:
These define the shape of the authoring domain. Drift here affects many modules and workflows.

---

### 4. Registration seams

Examples:

- module registration contracts
- module SDK registration entry points
- shell registration boundaries
- inspector contribution seams

Why protected:
These control how capability enters the system. Weak registration seams create monolithic drift.

---

### 5. Provider and adapter seams

Examples:

- `LiveSceneComposerProvider` location and dependencies
- runtime adapter seams
- scene-related adapter seams
- bridge-to-runtime adapter seams

Why protected:
These are where integration pressure tends to reintroduce bad coupling.

---

### 6. Dependency policy enforcement surfaces

Examples:

- architecture guard rules
- dependency policy artifacts
- path-blocking rules for legacy shared-core aliases

Why protected:
These are the mechanical means by which boundaries stay real.

---

## Core Protected Nodes in This Project

The following should be treated as protected in principle, even if exact filenames evolve:

1. `console-core` contracts and registry foundations
2. `runtime-mutation-bridge` command and policy contracts
3. scene model root contracts
4. layout node contracts
5. slot definition contracts
6. widget instance contracts
7. prefab definition contracts
8. module manifest and module SDK contracts
9. Composer provider seam
10. runtime integration adapter seams
11. dependency policy and architecture guard assertions

These are high-impact seams.

---

## What Makes a Change High Risk

A change should be considered high risk if it:

- alters dependency direction
- widens mutation authority
- changes scene/layout/slot/widget identity or relationship rules
- changes registration mechanics
- changes runtime adapter ownership
- introduces a new path around the bridge
- reintroduces debug/composer coupling
- invalidates compare/revert assumptions
- weakens failure isolation

Even a small diff can be high risk if it touches one of these areas.

---

## Review Expectations for Protected Nodes

Changes touching protected nodes should typically require:

- architectural review
- contract review
- stronger reasoning than “it works locally”
- focused tests
- verification of affected guards
- explicit consideration of blast radius

Protected node changes should be explainable, not merely executable.

---

## Validation Expectations for Protected Nodes

Depending on the node, validation may include:

- typecheck
- focused unit tests
- boundary tests
- architecture guard
- dependency policy checks
- mutation rejection-path tests
- registration seam tests
- adapter behavior tests

The exact set depends on the node, but “no extra validation” should be rare.

---

## Worker Ownership Guidance

Protected node work should skew toward core architecture and validation ownership.

Typical patterns:

- core architecture workers define or modify domain contracts
- tooling workers strengthen enforcement and scaffolding
- validation workers verify blast radius and rule integrity
- feature workers should usually consume protected seams rather than casually redefining them

This does not prohibit changes by feature workers, but it makes review responsibility explicit.

---

## Protected Nodes and Multi-Step Work

When work touches protected nodes, the preferred sequence is:

1. make the intended change explicit
2. explain why the seam must change
3. update related docs or policy if necessary
4. run focused validation
5. inspect impact cone before continuing adjacent feature work

This reduces hidden cascading damage.

---

## Anti-Patterns Around Protected Nodes

The system must reject:

- casual contract changes with no blast-radius review
- “temporary” bypasses around protected seams
- duplicate contract definitions in parallel paths
- rewriting provider or adapter seams as part of unrelated feature work
- widening mutation permissions without explicit review
- changing scene/slot/widget relationships because it simplifies one local implementation

---

## Minimal Protected-Node Review Checklist

Before merging a protected-node change, verify:

1. what boundary this node belongs to
2. why the change is necessary
3. what downstream areas are affected
4. what tests or guards prove safety
5. whether the change weakens policy or boundary clarity
6. whether related docs need updates

If those answers are unclear, the change is not ready.

---

## Summary

Protected nodes are the high-impact seams of the Live Scene Composer ecosystem: shared-core foundations, mutation governance contracts, scene/layout/slot/widget contracts, registration seams, provider seams, adapter seams, and dependency enforcement rules. Treating them explicitly as protected helps the project evolve without repeatedly damaging its foundation.
