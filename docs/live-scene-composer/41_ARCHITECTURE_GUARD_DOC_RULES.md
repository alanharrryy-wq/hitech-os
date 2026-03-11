# 41_ARCHITECTURE_GUARD_DOC_RULES

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation, Reviewers
- Scope: Enforceable documentation-to-code rules for Live Scene Composer and sibling boundaries

---

## Purpose

This document defines the architecture guard rules that must remain true for the Live Scene Composer ecosystem.

Its purpose is not only to describe architecture.
Its purpose is to define the rules that tooling and review should enforce so the documentation cannot silently drift away from the codebase.

This document is meant to have teeth.

---

## Why This Exists

Large systems do not usually rot because someone wrote one bad function.
They rot because:

- boundaries blur slowly
- "temporary" shortcuts survive
- old paths reappear
- docs stop matching reality
- protected seams change without review
- sibling products start importing each other because it was convenient one afternoon

This document exists so the project can detect that drift early.

---

## Core Principle

If the code and the documentation disagree on foundational architecture, that is a real defect.

The response should not be:
"the docs are probably stale"

The response should be:
"identify the truth, fix the mismatch, and restore alignment"

---

## Canonical Boundary Model

The system must preserve these top-level boundaries:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`

These are not naming suggestions.
They are the intended top-level architectural seams.

---

## Canonical Project Truths

The following truths are treated as non-negotiable unless explicitly re-decided through a documented architecture decision.

### Truth 1

**Runtime Debug Console and Live Scene Composer are sibling products, not one product with two moods.**

### Truth 2

**`console-core` is the only canonical shared infrastructure layer.**

### Truth 3

**Legacy shared-core paths must not be reintroduced.**

### Truth 4

**Live Scene Composer must not directly mutate runtime-facing state outside `runtime-mutation-bridge`.**

### Truth 5

**`runtime-debug-console` must not register or absorb Composer authoring logic.**

### Truth 6

**The canonical authoring model is: Scene -> Layout -> Slots -> Widgets.**

### Truth 7

**Protected nodes and mutation boundaries require stronger review and stronger evidence.**

---

## What the Guard Must Protect

The architecture/docs guard should protect at minimum:

- canonical docs presence
- canonical shared-core path discipline
- sibling boundary separation
- no legacy `dev-console/core` path drift
- no composer/debug cross-import drift
- existence of the critical architecture docs
- index and reading path consistency for core documents
- explicit rule ownership for protected seams

The guard is not meant to prove the whole product is correct.
It is meant to detect foundational drift.

---

## Rule Catalog

### AGR-001: Canonical docs must exist

The project must contain the canonical Live Scene Composer documentation set in the expected docs location.

At minimum, the following files are critical and must exist:

- `README.md`
- `00_TOC.md`
- `00_READING_PATHS.md`
- `01_PROJECT_OVERVIEW.md`
- `05_SYSTEM_ARCHITECTURE.md`
- `06_SYSTEM_BOUNDARIES.md`
- `07_DOMAIN_MODEL.md`
- `10_MUTATION_MODEL.md`
- `18_RUNTIME_MUTATION_BRIDGE.md`
- `19_DEPENDENCY_POLICY.md`
- `20_PROTECTED_NODES.md`
- `40_ARCHITECTURAL_DECISIONS.md`
- `41_ARCHITECTURE_GUARD_DOC_RULES.md`

A project can survive missing nice-to-have docs for a short time.
It should not normalize missing foundation docs.

---

### AGR-002: Legacy shared-core path must not exist

The following path must not reappear as active canonical code:

- `apps/keystone/components/dev-console/core/`

If that path exists again, the guard should fail unless there is an explicit, documented, reviewed architecture reversal.

---

### AGR-003: Legacy core imports must not exist

Imports referencing the old dev-console core path must fail the guard.

Examples of forbidden import forms include:

- `dev-console/core`
- `./core/`
- `/core/`

when they refer to the legacy shared-core path inside the dev-console boundary.

---

### AGR-004: Runtime Debug Console must not import Composer product logic

Code inside the Runtime Debug Console boundary must not import `live-scene-composer` product logic.

This includes direct and obvious imports into Composer product paths.

The reason is simple:
diagnostics must not quietly become authoring hosts.

---

### AGR-005: Live Scene Composer must not import Runtime Debug Console product logic

Code inside the Composer boundary must not import Runtime Debug Console product logic.

The Composer may reuse `console-core`.
It may not consume debug product internals as if they were its platform.

---

### AGR-006: The docs index must reflect the critical docs

`README.md`, `00_TOC.md`, and `00_READING_PATHS.md` must continue to reference the critical architectural documents.

This exists to prevent onboarding drift and the slow disappearance of the actual rules that keep the project sane.

---

### AGR-007: Guard rules doc must name the canonical boundaries

This file must continue to mention the canonical boundary names:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`

If that stops being true, the guard itself is drifting away from the architecture.

---

### AGR-008: Docs/code drift is a failure, not just a note

When a foundational doc is wrong or a foundational code rule is broken, the expected response is to fix the mismatch.

The guard should be treated as a quality gate for foundational alignment.

---

## Protected Areas Covered by This Guard

This guard is especially concerned with the following high-impact seams:

- shared-core boundary discipline
- sibling product separation
- mutation governance boundary presence
- dependency policy stability
- documentation discoverability for critical architecture rules

This does not replace protected-node review.
It reinforces it.

---

## Evidence Expectations

Changes that affect the guard should normally provide evidence such as:

- architecture guard output
- targeted tests
- typecheck where relevant
- explicit explanation of why a rule changed
- updated docs if the rule meaning changed

This is one of the places where "it compiles" is nowhere near enough.

---

## CI and Local Use

This guard should be runnable:

- locally by contributors
- in CI
- before or during review for risky changes

Suggested usage:

- run it after documentation generation
- run it after boundary refactors
- run it whenever shared-core, bridge, provider, or sibling-product seams change

---

## What This Guard Intentionally Does Not Guarantee

This guard does not guarantee:

- perfect product behavior
- perfect runtime correctness
- perfect mutation semantics
- complete dependency-graph proof of all architecture assumptions

That is not its job.

Its job is to catch a specific class of high-value architectural/documentation drift.

---

## Process for Changing a Guard Rule

A rule in this document should not be changed casually.

When a rule must change:

1. explain why the old rule is no longer valid
2. update related architecture docs
3. update the validator logic
4. update tests or evidence expectations if needed
5. record the reasoning in `40_ARCHITECTURAL_DECISIONS.md` if the change is architectural in nature

This keeps the guard from becoming random.

---

## Failure Philosophy

A guard failure should be treated as one of these:

- architecture drift
- documentation drift
- forbidden dependency drift
- canonical path regression
- missing critical documentation

That means a failure is meaningful.
It is not a decorative warning.

---

## Long-Term Value

If maintained seriously, this guard makes the project much harder to corrupt by accident.

It helps preserve:

- product identity
- boundary discipline
- safer onboarding
- better review quality
- lower architecture entropy over time

That is exactly what a serious system needs.

---

## Summary

This document defines the architecture guard rules that keep Live Scene Composer aligned with its own foundations. It protects canonical docs, canonical boundaries, legacy path discipline, sibling-product separation, and critical documentation discoverability. It exists so the project's rules do not dissolve into tribal memory and wishful thinking.
