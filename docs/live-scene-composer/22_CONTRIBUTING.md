# 22_CONTRIBUTING

## Document Status

- Status: Canonical
- Audience: Engineers, Tooling, Validation, Reviewers
- Scope: Contribution rules, expectations, and review discipline

---

## Purpose

This document defines how contributions should be made to Live Scene Composer and related boundaries. It exists to ensure that contributors do not accidentally weaken the architecture, introduce hidden coupling, or create code that cannot be safely evolved.

Contributing is not only about adding code.
It is about preserving the integrity of the system while extending it.

---

## Contribution Philosophy

All contributions should optimize for:

- explicitness
- correctness
- bounded ownership
- reviewability
- testability
- architecture preservation
- maintainability over cleverness

A contribution that ships a feature but weakens core boundaries is not a successful contribution.

---

## Who This Applies To

This document applies to:

- feature contributors
- core architecture contributors
- tooling contributors
- validation contributors
- reviewers
- automation-assisted contribution flows

Everyone who changes the codebase inherits the obligation to respect its architecture.

---

## What Counts as a Contribution

A contribution may include:

- code
- tests
- architecture guard updates
- dependency policy updates
- documentation
- refactors
- validation additions
- scaffolding or tooling improvements

The same discipline applies whether the change is a feature or “just cleanup.”

---

## Contribution Rules

### Rule 1: Know the boundary you are changing

Every change must have an identifiable boundary owner:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`
- runtime adapter area
- scene-related integration area

If the contribution crosses multiple boundaries, that should be explicit and justified.

### Rule 2: Do not smuggle architecture changes

A PR labeled as refactor, cleanup, or convenience should not silently introduce:

- new dependency directions
- new product coupling
- mutation bypasses
- hidden ownership shifts

### Rule 3: Respect canonical concepts

Do not invent parallel concepts when the system already has canonical ones such as:

- Scene
- Layout
- Slot
- Widget
- Prefab
- Mutation
- Bridge
- Module manifest

If the canonical concept is insufficient, improve it deliberately instead of duplicating it.

### Rule 4: Update docs when meaning changes

Architecture and domain meaning changes require doc updates or explicit rationale for why docs remain valid.

### Rule 5: Add evidence for risky changes

The higher the risk, the stronger the evidence required.

---

## Contribution Categories

### Low-risk contributions

Examples:

- typo fixes
- local UI polish without semantic changes
- internal cleanup within a bounded private area
- comment improvements

Expected process:
Normal review and normal verification.

### Medium-risk contributions

Examples:

- new module contributions
- inspector behavior additions
- new prefab categories
- structure tooling improvements
- widget-type enhancements

Expected process:
Clear explanation, targeted tests, and architecture awareness.

### High-risk contributions

Examples:

- mutation contract changes
- scene/layout/slot/widget contract changes
- provider seam changes
- adapter seam changes
- dependency policy changes
- shared-core changes
- bridge validation behavior changes

Expected process:
Explicit rationale, focused review, stronger verification, and likely doc updates.

---

## Branch and Change Hygiene

A contribution should be:

- scoped
- coherent
- readable
- minimally noisy
- explainable in one narrative

Avoid PRs that mix:

- feature work
- architecture rewrites
- unrelated cleanup
- random formatting churn

That kind of bundle makes review weaker and regression more likely.

---

## Commit Message Guidance

Commits should explain intent, not only activity.

Prefer messages that communicate:

- what changed
- why it changed
- what boundary or concept it affects

Examples of good intent framing:

- preserve composer/debug boundary in registry wiring
- add typed widget style mutation through bridge
- harden slot compatibility validation
- isolate chart appearance module registration

Avoid vague messages like:

- stuff
- fixes
- cleanup
- updates
- wip

---

## Pull Request Expectations

A healthy PR should include:

- problem statement
- boundary affected
- summary of change
- risk level
- validation run
- docs updated or rationale for not updating
- any remaining risks or follow-up items

The reviewer should not have to guess what the contribution is doing to the system.

---

## Required PR Questions

Every meaningful PR should answer:

1. What problem does this solve?
2. Which boundary owns the solution?
3. What contracts or protected nodes are affected?
4. Does this change dependency direction?
5. Does this alter mutation behavior?
6. What tests or guards prove safety?
7. Do docs remain correct?

These questions are not bureaucracy; they are architecture protection.

---

## Reviewer Expectations

Reviewers should not limit review to “does the code run?”

Reviewers should ask:

- is this in the right place
- is the dependency direction allowed
- does it preserve sibling product separation
- does it widen authority unsafely
- does it weaken the bridge
- does it duplicate an existing concept
- is the blast radius understood

A reviewer is a boundary defender, not just a syntax checker.

---

## Protected Node Contributions

Changes touching protected nodes require stronger discipline.

Examples:

- scene model contracts
- mutation bridge contracts
- dependency policy
- module SDK
- console-core registry foundations
- provider seams
- adapter seams

These changes should include:

- explicit rationale
- stronger validation
- targeted tests
- doc review
- careful impact explanation

---

## Testing Expectations for Contributions

A contributor should run the strongest relevant verification subset for the change.
Possible examples include:

- typecheck
- architecture guard
- targeted tests
- mutation rejection-path tests
- registration seam tests
- dependency or path assertions

The contribution should not depend on the reviewer to discover all missing validation.

---

## Forbidden Contribution Patterns

The following are unacceptable contribution patterns:

- adding a feature by bypassing mutation governance
- importing across sibling boundaries because it is convenient
- hiding architecture changes inside unrelated cleanup
- introducing new shared folders without ownership clarity
- shipping “temporary” hacks that create long-term coupling
- editing protected seams with no explanation or validation

---

## Summary

Contributing to Live Scene Composer requires more than making code compile. Contributors must respect boundaries, preserve canonical concepts, explain changes clearly, validate risky work, and avoid smuggling architectural damage inside convenience changes. Strong contribution discipline is how the project stays healthy as it grows.
