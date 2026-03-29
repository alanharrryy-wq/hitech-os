# 37_VERSIONING_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation
- Scope: Versioning expectations for docs, contracts, prefabs, SDK surfaces, and future compatibility management

---

## Purpose

This document defines the versioning model for Live Scene Composer and related architecture surfaces. It exists because as the system grows, several things may evolve at different speeds:

- docs
- domain contracts
- module SDK
- mutation commands
- prefab definitions
- future custom widget specs

Without a versioning model, compatibility questions become messy and expensive.

---

## Versioning Principles

Versioning should optimize for:

- compatibility clarity
- explicit change meaning
- stable migration thinking
- safer evolution of protected contracts
- reduced ambiguity for tooling and contributors

Versioning is not only for release tags.
It is also for the internal shape of the system.

---

## What Should Be Versioned

At minimum, the project should think explicitly about versioning for:

- scene-related contracts
- widget and slot contracts
- prefab definitions
- mutation command contracts
- module SDK surfaces
- custom widget spec/API versions in future phases
- product release history

Not everything needs the same versioning granularity, but the sensitive surfaces should be version-aware.

---

## Contract Versioning

Protected contracts should evolve deliberately.

Examples include:

- scene document structure
- slot definition shape
- widget instance shape
- prefab definition shape
- mutation command schema
- module manifest shape

When these change materially, the change should be visible and reviewable.

---

## SDK Versioning

The Module SDK should have a compatibility story.

The system should eventually be able to answer:

- what SDK version a module targets
- whether that version is supported
- whether a module relies on deprecated seams
- whether a breaking SDK change has occurred

Even if formal semantic handling is lightweight at first, the concept should be present now.

---

## Prefab Versioning

Prefabs may evolve over time, but the system should avoid pretending that all prefab changes are harmless.

Versioning helps answer:

- is this the same prefab definition or a new shape
- should existing widget instances remain untouched
- do migration rules exist
- is this only a visual default improvement or a structural change

This matters more as the prefab system becomes richer.

---

## Mutation Contract Versioning

Mutation commands and their payload expectations should remain stable enough for trust.
If mutation contracts change meaningfully, that should be visible.

Useful concerns include:

- new command introduction
- payload shape changes
- validation expectation changes
- safe mode compatibility changes
- deprecation of older command styles

The bridge is a protected area and version awareness helps preserve discipline.

---

## Documentation Versioning

The documentation set should reflect the evolving system, but docs should not drift silently.
When major semantic changes occur, docs should be updated as part of the change rather than “later.”

A practical approach is:

- keep canonical docs current
- use `CHANGELOG.md` for release-visible evolution
- use `ARCHITECTURAL_DECISIONS.md` for key decision history
- note version relevance where it matters for contracts or APIs

---

## Release Versioning

The project should maintain a release/version story that is understandable to engineering and product stakeholders.

A healthy release versioning approach should help answer:

- what changed
- what is compatible
- what is deprecated
- what requires migration thought
- what is still experimental

The exact release scheme may follow repo or organization conventions, but the meaning of versions should remain clear.

---

## Compatibility Mindset

The project should distinguish between:

- additive change
- compatible refinement
- deprecation
- breaking change

These distinctions matter especially for:

- SDK surfaces
- mutation contracts
- prefab structures
- future custom widget APIs

Not every change is equally disruptive.

---

## Versioning Anti-Patterns

The system must reject:

- changing protected contracts with no visible compatibility story
- pretending a breaking change is “just cleanup”
- evolving the SDK with no signal to module authors
- mutating prefab meaning invisibly
- release notes that hide meaningful architecture or capability changes

---

## Summary

The Versioning Model exists to keep Live Scene Composer evolvable without becoming ambiguous. Contracts, SDK surfaces, prefab definitions, mutation schemas, and releases all benefit from explicit version thinking. Versioning is one of the tools that helps the project grow without losing clarity.
