# 24_TESTING_STRATEGY

## Document Status

- Status: Canonical
- Audience: Engineering, Validation, Tooling, Reviewers
- Scope: Testing philosophy, layers, priorities, and boundary-oriented verification

---

## Purpose

This document defines the testing strategy for Live Scene Composer and its related architecture. It exists because this project cannot rely on visual confidence alone. The system includes protected contracts, mutation governance, sibling product boundaries, and integration seams that require targeted evidence.

The goal is not “more tests.”
The goal is the right tests at the right layers.

---

## Testing Principles

The testing strategy should optimize for:

- boundary protection
- contract confidence
- mutation governance
- local failure detection
- regression resistance
- confidence in architectural rules
- focused evidence rather than noisy test volume

A thousand shallow tests are less useful than a smaller set of tests that defend the real seams.

---

## What the Test Suite Must Protect

The test strategy must protect at minimum:

- sibling separation between Runtime Debug Console and Live Scene Composer
- canonical domain contracts
- mutation bridge enforcement
- slot/widget compatibility rules
- module registration discipline
- dependency policy assumptions
- preview/commit/revert semantics at the level the product supports
- failure isolation for bounded modules and widgets where implemented

---

## Test Layers

### 1. Contract tests

These validate important typed contracts and domain rules.

Examples:

- scene/layout/slot/widget contract expectations
- prefab compatibility rules
- module manifest validation
- mutation command shape validation

Contract tests matter because many future capabilities depend on these definitions staying coherent.

---

### 2. Boundary tests

These validate architecture boundaries and wiring expectations.

Examples:

- runtime-debug does not register composer modules
- composer does not write directly to runtime paths
- no legacy shared-core path drift
- no forbidden sibling imports where checkable

Boundary tests are among the highest leverage tests in this project.

---

### 3. Mutation behavior tests

These validate the mutation model and bridge.

Examples:

- rejects invalid target
- rejects forbidden Safe Mode command
- accepts allowed widget style mutation
- rejects bypass path
- preserves explicit preview vs commit behavior

These tests matter because mutation is the safety center of the system.

---

### 4. Module registration tests

These validate module lifecycle and contribution discipline.

Examples:

- module registers valid inspector contribution
- invalid manifest is rejected
- disabled module does not contribute surfaces
- broken module contribution does not collapse the shell

---

### 5. Integration tests

These validate meaningful end-to-end slices within bounded scope.

Examples:

- selecting a widget exposes the expected inspector contribution
- inserting a prefab into a compatible slot produces expected structure
- valid mutation request updates draft and preview
- invalid insertion is blocked and reported

Integration tests should prove coherent slices, not replace every lower-level test.

---

### 6. Smoke tests

These validate top-level health.

Examples:

- core architecture-related tests pass
- key shells mount
- critical routes or providers initialize
- architecture guard still passes

Smoke tests do not prove depth, but they help catch catastrophic breakage early.

---

## Risk-Based Testing Priority

Higher risk areas deserve stronger testing density.

### Highest priority

- mutation bridge
- scene/layout/slot/widget contracts
- dependency policy enforcement
- provider seams
- registration seams
- runtime/composer separation

### Medium priority

- inspector contributions
- widget-specific editing behavior
- prefab filtering and insertion
- structure tree interactions

### Lower but still meaningful priority

- minor UI polish
- purely cosmetic rendering details
- static documentation-only surfaces

The point is not to ignore low-risk areas, but to assign energy intelligently.

---

## What Not to Over-Rely On

Do not over-rely on:

- visual manual testing alone
- giant broad integration tests that are hard to maintain
- snapshot tests as the main correctness mechanism
- local “seems okay” runtime impressions
- tests that only assert implementation details with no product or architecture meaning

This system needs evidence aligned with its actual risks.

---

## Mutation Bridge Testing Expectations

The bridge deserves special attention.

At minimum, the bridge should have tests for:

- accepted command flow
- rejected command flow
- source validation
- target validation
- mode gating
- preview vs commit handling
- no-bypass assumptions where feasible

If the bridge is under-tested, the whole product safety story weakens.

---

## Dependency and Path Guard Testing

The project should verify critical path and dependency rules such as:

- no legacy core path reintroduction
- no composer registration inside runtime-debug
- no canonical shared boundary drift
- no forbidden path aliases

These checks may be split between tests and architecture guard tooling.

---

## Failure Isolation Testing

As modularity grows, the test strategy should increasingly validate local containment.

Examples:

- one broken module does not break unrelated inspector surfaces
- widget-type-specific failure does not collapse selection model
- future sandboxed custom widget failures stay local

The Composer should be tested not only for happy paths but for survivability.

---

## Test Writing Guidelines

A good test should:

- describe behavior clearly
- target a meaningful seam
- fail for the right reason
- remain stable as implementation refactors
- communicate intent in plain language

A bad test:

- is coupled to internals that should be private
- asserts incidental implementation details
- is so broad that failures are hard to interpret
- duplicates other tests without adding confidence

---

## Minimum Verification for Risky Changes

For higher-risk changes, the contributor should usually run:

- typecheck
- architecture guard
- relevant unit or integration tests
- targeted new tests for the seam being changed

Risky changes without evidence should not be normalized.

---

## Summary

The testing strategy for Live Scene Composer should defend the architecture, mutation safety, and domain integrity of the system. Boundary tests, contract tests, bridge tests, and focused integration tests matter far more than raw test count. The goal is to prove that the important seams still hold, not merely that the UI still renders.
