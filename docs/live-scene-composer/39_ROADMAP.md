# 39_ROADMAP

## Document Status

- Status: Canonical
- Audience: Product, Architecture, Engineering, Leadership
- Scope: Planned evolution of Live Scene Composer from foundation through mature capability growth

---

## Purpose

This document defines the roadmap for Live Scene Composer at a strategic level. It exists to guide sequencing, keep scope disciplined, and avoid mixing foundational work with future ambition in a way that destabilizes the product.

A roadmap should preserve direction, not create fantasy commitments.

---

## Roadmap Principles

The roadmap should prioritize:

- strong foundations first
- MVP usefulness before broad expansion
- safety before power
- structural clarity before advanced complexity
- modular growth before feature sprawl
- contract stability before extension explosion

The Composer should grow in layers, not as a pile of simultaneous ambitions.

---

## Phase 0: Foundation and Boundary Hardening

### Goals

- establish canonical project identity
- separate Composer from Runtime Debug Console
- establish `console-core` as shared infrastructure
- establish `runtime-mutation-bridge` as controlled write boundary
- document the core system thoroughly
- define dependency policy and protected nodes
- create hardening guardrails

### Outcomes

- strong conceptual model
- clear ownership boundaries
- durable foundation for implementation work

---

## Phase 1: Minimum Safe Composer MVP

### Goals

- render a dedicated Composer shell
- support scene-aware selection
- support Canvas + Structure + Inspector interaction loop
- support basic layout movement and resizing where appropriate
- support text and typography editing
- support basic styling and background editing
- support prefab insertion into valid slots
- support a small typed bridge command set
- support draft, compare, discard, and commit basics

### MVP Success Criteria

The MVP is successful when a user can make real visual composition changes safely and understand what changed.

### Out of Scope for MVP

- large custom widget platform
- broad scripting
- advanced responsive rules
- heavy data-binding complexity
- giant plugin ecosystem

---

## Phase 2: Strong Authoring Modules

### Goals

- deepen module-based authoring
- improve chart appearance tools
- improve layout tooling
- improve visual styling system
- improve structure operations
- strengthen reset/revert granularity

### Expected Additions

- richer typography controls
- stronger chart editing surfaces
- better alignment and guide support
- improved visual treatment modules
- stronger module registration and isolation behavior

---

## Phase 3: Reuse, Presets, and Variation

### Goals

- strengthen prefab system
- introduce presets and reusable composition states
- introduce stronger compare and snapshot workflows
- begin richer variants and theme logic

### Outcomes

- faster authoring
- more reusable composition patterns
- stronger scene consistency

---

## Phase 4: Bounded Advanced Capability

### Goals

- introduce carefully governed advanced authoring paths
- deepen bridge policy where needed
- introduce stronger future-ready custom widget surfaces
- expand mode-aware capability safely

### Important Rule

This phase should happen only after foundation and safe workflows are proven.
It must not become a shortcut that rewrites the earlier discipline.

---

## Phase 5: Mature Extension and Ecosystem Integration

### Goals

- strengthen extension points
- improve tooling and validation around modules and bindings
- support richer future integrations
- allow the Composer to function as a durable platform rather than only a first-party tool

### Preconditions

- protected seams remain strong
- mutation governance remains intact
- dependency policy remains enforced
- extension safety is proven, not assumed

---

## Current Strategic Priority

The current highest priority is not “maximum feature count.”
The highest priority is:

- strong Composer foundation
- clear provider and wiring seams
- minimum safe bridge commands
- useful MVP authoring loop
- preserved boundary discipline

This is the right order because it avoids paying for undisciplined growth later.

---

## Roadmap Risks

The roadmap can fail if the team:

- inflates the MVP
- reintroduces debug/composer coupling
- weakens bridge discipline
- ignores slot/widget/layout contract clarity
- over-prioritizes advanced power before safe usability
- lets extension needs dominate before the base system is stable

---

## Summary

The roadmap for Live Scene Composer begins with boundary hardening and a safe useful MVP, then grows into richer authoring modules, reuse systems, variation tools, and eventually bounded advanced extension. The roadmap is intentionally disciplined so the product can become powerful without becoming chaotic.
