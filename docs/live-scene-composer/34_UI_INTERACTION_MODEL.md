# 34_UI_INTERACTION_MODEL

## Document Status

- Status: Canonical
- Audience: Product, Design, Engineering
- Scope: Interaction principles, surface roles, and user-facing interaction behavior

---

## Purpose

This document defines how the user interface of Live Scene Composer should behave conceptually. It explains how the main surfaces work together, how users are expected to interact with the system, and what interaction patterns should feel consistent.

The Composer is not just a set of controls.
It is a structured interaction model.

---

## Interaction Model Summary

The Composer UI is centered around three main surfaces:

- Canvas
- Structure
- Inspector

Supporting surfaces include:

- Prefab Library
- compare/revert controls
- future snapshots or variants tools
- optional mode or state indicators

The key principle is that interaction should remain coherent across all these surfaces.

---

## Main Interaction Principle

The user should always be able to answer three questions quickly:

1. What am I looking at?
2. What is selected?
3. What kind of change am I making?

If the UI makes those answers unclear, the interaction model has failed.

---

## Canvas Interaction Model

The Canvas is the primary direct-manipulation surface.

The Canvas should support:

- visible selection feedback
- hover targeting where helpful
- drag and resize where allowed
- guides and snapping where useful
- real preview of changes

The Canvas should feel live and trustworthy.
It should not feel like a symbolic mock area disconnected from the real scene.

---

## Structure Interaction Model

The Structure surface is the primary hierarchy-navigation surface.

It should support:

- explicit selection
- hierarchy understanding
- ordering awareness
- understanding of scene, layout, slots, and widgets
- disambiguation in visually dense scenes

When the Canvas is visually ambiguous, Structure should restore clarity.

---

## Inspector Interaction Model

The Inspector is the contextual editing surface.

It should:

- reflect the current selection
- show only relevant controls
- group controls by conceptual area
- remain understandable at a glance
- avoid becoming a giant dumping ground of unrelated settings

The Inspector should help the user act confidently, not overwhelm them with unrelated controls.

---

## Cross-Surface Synchronization

Selection and context should remain synchronized across:

- Canvas
- Structure
- Inspector

If a user selects something in one surface, the other surfaces should reflect that change coherently.

This is one of the most important interaction rules in the whole product.

---

## Interaction Priority

When multiple interaction surfaces could theoretically do something, the product should prefer clarity and contextual fit.

Examples:

- direct manipulation belongs primarily on Canvas
- hierarchy clarification belongs primarily in Structure
- property editing belongs primarily in Inspector
- reusable insertion belongs primarily in Prefab Library

The system should not overload one surface with every possible responsibility.

---

## Direct Manipulation Rules

Where supported, direct manipulation should:

- feel visually responsive
- preserve structural meaning
- avoid arbitrary or misleading movement
- show guidance and boundaries where appropriate
- remain bounded by system rules

Drag and resize should feel intentional, not sloppy.

---

## Contextual Editing Rules

Contextual editing should:

- be target-aware
- distinguish between scene, layout, slot, and widget editing
- avoid showing controls that do not apply
- avoid implying unsupported behavior

A user should not be tricked into thinking a control applies to the wrong target.

---

## Visibility and Feedback

The UI should provide enough feedback to keep the user oriented.

Helpful feedback includes:

- active selection outline
- handles
- hover affordances
- insertion indicators
- guide lines
- preview changes
- compare/revert indicators where applicable
- compatibility messaging during insertion or replacement

The product should feel transparent, not mysterious.

---

## Interaction with Prefabs

The interaction model for prefabs should be:

- target-aware
- slot-aware
- compatible-first
- easy to browse
- fast to insert

The user should not have to guess where a prefab can go.
The product should make valid paths obvious.

---

## Compare and Recovery Interaction

The interaction model should make it easy to understand:

- what changed
- what is draft
- what can be reset
- what can be discarded
- what will be accepted on commit

Users should not feel like they are performing invisible state transitions.

---

## Safe Mode Interaction

Safe Mode should feel normal, not crippled.
It should provide the majority of useful visual authoring power in a bounded and trustworthy way.

The UI should not push users toward unsafe behavior just because safe behavior feels clumsy.

---

## Advanced Mode Interaction

If Advanced Mode is present, it should feel explicit and meaningfully different, not like a hidden privilege mode with unclear rules.
The UI should make mode implications clear enough to avoid accidental misuse.

---

## Interaction Anti-Patterns

The UI interaction model must reject:

- selection ambiguity with no clear feedback
- inspector overload
- visual interactions that ignore structure
- structure views disconnected from the canvas
- hidden state transitions between preview and accepted changes
- forcing users into debug-oriented mental models for authoring tasks

---

## Summary

The UI interaction model for Live Scene Composer is built around synchronized Canvas, Structure, and Inspector surfaces. It should make selection, editing, and change review clear and contextual. Strong interaction design is one of the main ways the product delivers power without confusion.
