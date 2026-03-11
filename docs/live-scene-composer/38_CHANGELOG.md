# 38_CHANGELOG

## Document Status

- Status: Canonical
- Audience: Engineering, Product, Validation, Operators
- Scope: Significant changes to the project over time

---

## Purpose

This file records meaningful changes to Live Scene Composer and its core architecture.
It should prioritize changes that matter for:

- product capability
- architecture
- contracts
- dependency policy
- deployment and operations
- compatibility expectations

This file should not become a noisy dump of trivial edits.

---

## Changelog Principles

A useful changelog should:

- summarize meaningful changes
- group changes by release or milestone
- distinguish feature change from architecture hardening
- note breaking or compatibility-relevant changes
- remain readable over time

---

## Suggested Entry Structure

A healthy entry may include sections like:

- Added
- Changed
- Fixed
- Removed
- Deprecated
- Notes

This is a recommendation, not a rigid requirement.

---

## Pre-Release Foundation Phase

### Added

- canonical project definition for Live Scene Composer
- architectural separation from Runtime Debug Console
- canonical shared boundary via `console-core`
- explicit mutation governance boundary via `runtime-mutation-bridge`
- foundational documentation for:
  - project overview
  - product vision
  - goals and non-goals
  - scene/layout/slot/widget domain model
  - state model
  - runtime model
  - mutation model
  - module system and SDK
  - widget, slot, layout, and prefab systems
  - sandbox and security rules
  - dependency policy and protected nodes
  - development, testing, operations, deployment
  - product usage and workflow references

### Changed

- project framing from mixed console/editor concerns toward a clean sibling-product model
- shared infrastructure naming and role clarified around `console-core`
- explicit product intent defined for Composer as a visual authoring workspace rather than a diagnostics extension

### Fixed

- conceptual ambiguity between debug tooling and authoring responsibility
- lack of explicit mutation governance model
- lack of durable documentation baseline for future implementation work

### Notes

This phase is foundational and intentionally heavy on structure, rules, and architectural grounding rather than broad feature expansion.

---

## Guidance for Future Entries

Future entries should include things like:

### Feature additions

Examples:

- added chart appearance module
- added prefab insertion workflow
- added structure-aware reset action

### Architecture changes

Examples:

- hardened bridge validation rules
- introduced provider seam for Composer shell
- strengthened dependency policy enforcement

### Breaking or sensitive changes

Examples:

- changed widget style contract version
- removed deprecated mutation command path
- introduced stricter slot compatibility validation

---

## What Not to Put Here

Do not clutter the changelog with:

- trivial formatting edits
- routine local refactors with no semantic impact
- noise-level dependency bumps unless operationally significant
- every tiny UI tweak

The changelog should remain useful to humans.

---

## Summary

`CHANGELOG.md` records the meaningful evolution of Live Scene Composer. It should stay focused on architecture, capability, compatibility, and operationally relevant change rather than becoming an unreadable wall of minor edits.
