# 40_ARCHITECTURAL_DECISIONS

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Reviewers
- Scope: Major architecture decisions and the rationale behind them

---

## Purpose

This document records important architecture decisions for Live Scene Composer. It exists because strong systems are easier to evolve when the reasoning behind key decisions is preserved instead of living only in memory or scattered conversations.

This file is the long-term memory of the project’s architectural intent.

---

## How to Use This Document

Use this file to record decisions that materially affect:

- system boundaries
- domain model
- mutation governance
- extensibility
- dependency direction
- provider seams
- protected nodes
- high-impact workflow semantics

Do not use it for trivial implementation details.

---

## Decision 001: Live Scene Composer is a separate sibling product from Runtime Debug Console

### Decision

Live Scene Composer and Runtime Debug Console are separate sibling products.

### Rationale

They serve different purposes:

- Runtime Debug Console is for diagnostics, inspection, overlays, performance, and runtime state awareness
- Live Scene Composer is for authoring, composition, layout editing, styling, and controlled scene mutation

Combining them would blur product identity and create long-term architecture problems.

### Consequences

- separate product boundaries must remain visible
- registration and routing must preserve separation
- debug logic must not absorb authoring logic

---

## Decision 002: `console-core` is the only shared infrastructure layer

### Decision

Shared infrastructure should be normalized under `console-core`.

### Rationale

The system needs a single canonical shared layer for shell, layout primitives, registry primitives, events, lifecycle helpers, and related reusable infrastructure.

Parallel or ambiguous shared-core paths increase architecture drift.

### Consequences

- duplicate or legacy shared-core paths should be blocked
- shared code should be truly shared, not product-specific convenience code

---

## Decision 003: The Composer model is Scene -> Layout -> Slots -> Widgets

### Decision

The core composition model of the product is:

**Scene -> Layout -> Slots -> Widgets**

### Rationale

This model supports:

- structured composition
- layout clarity
- bounded host regions
- widget identity
- prefab insertion
- future custom widget containment

It is superior to vague “panel” mental models for this product.

### Consequences

- domain docs and contracts should preserve this model
- feature design should not flatten these concepts into anonymous components

---

## Decision 004: All write-capable composer mutations go through `runtime-mutation-bridge`

### Decision

The Composer must not write directly to runtime-facing state.
Write-capable changes must go through `runtime-mutation-bridge`.

### Rationale

This provides:

- validation
- explicit mutation contracts
- mode-aware governance
- preview vs commit semantics
- better testing and auditing

### Consequences

- direct write shortcuts are architectural violations
- modules and future custom widgets must not bypass the bridge

---

## Decision 005: The runtime must not depend on the Composer

### Decision

The runtime is not allowed to depend on the Composer as a core requirement.

### Rationale

The Composer is an authoring client of the runtime ecosystem, not a foundational runtime dependency.

### Consequences

- runtime integration should happen through explicit adapters
- runtime-facing systems must not silently absorb composer ownership

---

## Decision 006: Modularity is a first-class product and architecture requirement

### Decision

The Composer should grow through explicit modules, not monolithic feature accumulation.

### Rationale

The product is expected to expand across multiple feature domains and needs removability, isolation, and clear ownership.

### Consequences

- module manifests and SDK matter
- module registration should stay explicit
- local failure containment should be expected

---

## Decision 007: Safe Mode is the default authority posture

### Decision

The normal operating mode of the Composer is Safe Mode.

### Rationale

A live visual authoring product should deliver most useful power through bounded, understandable actions by default.

### Consequences

- normal workflows should not require advanced privilege
- advanced capabilities should remain gated and deliberate

---

## Decision 008: Custom widgets must be sandboxed and slot-bounded

### Decision

Future custom widgets must render only inside approved slot regions and use restricted APIs.

### Rationale

Custom code inside a live authoring/runtime-aware system is high risk without containment.

### Consequences

- no unrestricted code injection
- custom widgets require sandbox, capability gating, and local failure isolation

---

## Decision 009: Dependency direction is part of the architecture contract

### Decision

Allowed and forbidden dependency relationships must be documented and enforced.

### Rationale

Architecture boundaries are not real if the import graph can silently violate them.

### Consequences

- dependency policy is a living architecture tool
- architecture guard and focused tests should reinforce dependency discipline

---

## Decision 010: Protected nodes require elevated care

### Decision

Certain seams, contracts, and provider/adaptor surfaces should be treated as protected nodes.

### Rationale

Some files and contracts have disproportionate blast radius.
Treating them casually leads to recurring architecture damage.

### Consequences

- stronger review and validation expectations apply
- contributors should be aware when touching protected seams

---

## Decision 011: Draft, baseline, preview, and commit must remain semantically distinct

### Decision

The state model must preserve these distinctions.

### Rationale

User trust, compare/revert behavior, and predictable authoring all depend on these state categories remaining legible.

### Consequences

- preview should not silently equal accepted state
- mutations and UI must preserve these meanings

---

## Decision 012: The product should optimize for usefulness before maximal power

### Decision

The roadmap prioritizes a safe useful MVP before large advanced extension surfaces.

### Rationale

Trying to solve advanced scripting, huge binding systems, or large custom extension before core authoring is stable is likely to create chaos.

### Consequences

- early scope should stay disciplined
- feature expansion should follow proven foundation work

---

## Guidance for Future Decisions

Future entries should include:

- the decision
- the rationale
- what alternatives were rejected if relevant
- what consequences the decision creates
- what boundaries or contracts are affected

This keeps the project’s reasoning durable over time.

---

## Summary

This document preserves the core architectural reasoning behind Live Scene Composer: sibling product separation, a structured domain model, governed runtime mutations, modular growth, safe defaults, bounded extension, dependency discipline, and strong state semantics. These decisions are the backbone of the project and should not be casually revisited.
