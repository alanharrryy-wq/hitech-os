# 31_USER_MANUAL

## Document Status

- Status: Canonical
- Audience: End Users, Operators, Designers, Internal Authors
- Scope: Practical use of Live Scene Composer from a user point of view

---

## Purpose

This manual explains how to use Live Scene Composer as an authoring product. It is written for users who need to compose, edit, preview, and manage scenes safely and efficiently.

This is not an engineering spec.
It is the practical user-facing guide for getting work done in the Composer.

---

## What Live Scene Composer Is

Live Scene Composer is a live visual authoring workspace for editing a structured scene model in real time.

It allows users to:

- view the live scene
- select visible elements
- edit text and typography
- move, resize, and reorganize layout
- insert prefabricated content blocks
- change styling and appearance
- compare and discard changes
- work within bounded visual structure

The Composer is meant for authoring and composition, not for runtime diagnostics.

---

## Main Areas of the Workspace

### Canvas

The Canvas shows the live rendered scene and is the primary visual interaction surface.

Users can generally:

- select visible items
- see outlines, handles, or guides
- drag or resize supported elements
- preview real visual changes

### Structure

The Structure view shows the composition hierarchy.

It helps users understand:

- scene organization
- layout relationships
- slots
- widgets
- ordering and visibility

### Inspector

The Inspector shows controls for the currently selected target.

Depending on selection, the Inspector may expose:

- text editing
- typography
- spacing
- color
- backgrounds
- effects
- chart appearance
- widget-specific properties

### Prefab Library

The Prefab Library allows fast insertion of approved reusable blocks into valid locations.

---

## Basic Authoring Flow

The intended editing flow is:

1. open a scene
2. select an item on the canvas or in structure
3. inspect the current selection
4. make changes
5. review preview state
6. compare against baseline if needed
7. commit, discard, or reset as appropriate

This should feel like a controlled live workspace, not a disconnected form editor.

---

## Selecting Items

You can select items from:

- the canvas
- the structure tree
- certain insertion or focus flows

Common selectable targets include:

- the scene
- layout regions or nodes
- slots
- widgets

Selection controls what the Inspector shows and what actions are available.

---

## Editing Text

For text-capable widgets, the Composer may allow:

- inline editing
- text content updates through the Inspector
- font family changes
- font size changes
- font weight changes
- line height changes
- letter spacing changes
- alignment changes
- color and opacity changes

Text editing should update preview quickly so the user can judge the result in context.

---

## Editing Appearance

Appearance editing may include:

- background changes
- color updates
- border or chrome treatment
- shadow or glow
- opacity
- card or container styling
- chart appearance controls

The goal is to make visual editing feel direct and understandable.

---

## Editing Layout

For supported targets, layout editing may include:

- move
- resize
- reorder
- alignment
- spacing adjustments
- snapping or guide-assisted placement

Layout changes should preserve scene structure rather than behave like arbitrary freeform DOM movement.

---

## Working with Prefabs

Prefabs are reusable building blocks.
A typical prefab workflow is:

1. select a slot or valid insertion target
2. open the Prefab Library
3. choose a compatible prefab
4. insert it
5. adjust props and styles as needed

If a prefab is not compatible with the selected slot, the system should prevent or clearly reject the insertion.

---

## Working with Charts

Chart-oriented widgets may allow editing of:

- chart type
- labels
- palette
- padding
- card chrome
- titles or supporting text
- local styling

Chart editing should be treated as a meaningful visual authoring workflow, not just a color picker.

---

## Draft and Preview

Changes are generally made into a draft-oriented workflow.
That means:

- you may see changes before they are treated as accepted
- some changes may be previewed immediately
- you may compare current changes against an earlier accepted baseline
- you may discard a bad draft

Users should understand that seeing a change does not always mean it has been permanently accepted.

---

## Reset, Discard, and Commit

### Reset

Reset usually means restoring a selected scope, such as a widget or local styling area, to a previous state.

### Discard Draft

Discard removes in-progress draft changes and returns to the accepted baseline.

### Commit

Commit accepts the current draft changes as the next approved working state in the Composer flow.

The exact UX may evolve, but users should always be able to distinguish these meanings.

---

## Safe Mode and Advanced Mode

### Safe Mode

Safe Mode is the normal editing mode and focuses on bounded, understandable authoring actions.

Typical Safe Mode actions include:

- visual editing
- text updates
- layout adjustments within supported rules
- prefab insertion
- style changes

### Advanced Mode

Advanced Mode is for more powerful future capabilities and should remain intentionally gated.
It should not be treated as normal editing with hidden extra power.

---

## Understanding Slots and Widgets

Users do not need to memorize the full architecture, but understanding the basics helps a lot.

### Slot

A Slot is a valid host region in the scene.

### Widget

A Widget is a concrete piece of content or visual rendering placed inside a slot.

This explains why some things can be inserted in some places and not others.

---

## Common Good Practices

- use Structure when the Canvas feels visually ambiguous
- select the smallest meaningful target before editing
- use prefabs instead of building repeated patterns manually
- compare against baseline when making broad visual changes
- prefer safe bounded edits over forcing a structure that the scene does not support

---

## Common Mistakes to Avoid

- trying to insert incompatible content into the wrong slot
- assuming preview always equals accepted commit
- confusing layout structure with widget content
- editing visually without checking Structure when the scene is complex
- using the Composer as if it were a debug console

---

## Summary

Live Scene Composer is a structured live authoring workspace built around canvas, structure, inspector, and controlled change workflows. Users should work by selecting, editing, previewing, and then committing or discarding changes with a clear understanding of scene structure, slots, widgets, and bounded authoring behavior.
