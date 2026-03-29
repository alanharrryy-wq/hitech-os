# 32_WORKFLOW_GUIDE

## Document Status

- Status: Canonical
- Audience: Users, Operators, Product, Enablement
- Scope: Recommended workflows and practical usage patterns in Live Scene Composer

---

## Purpose

This guide explains recommended ways to work inside Live Scene Composer. It is not just a list of features; it is a practical guide to using the product effectively and safely.

A good workflow reduces mistakes, improves output quality, and helps users trust the system.

---

## Workflow Philosophy

The Composer should be used as a structured authoring workspace.
The best workflows are those that:

- preserve scene clarity
- use valid structure
- avoid random edits without context
- take advantage of preview and compare behavior
- favor reusable building blocks
- keep changes understandable

The recommended mental loop is:

**Select -> Inspect -> Change -> Preview -> Compare -> Commit or Revert**

---

## Workflow 1: Edit Existing Widget Content

Use this when a scene already contains the widget you need to update.

### Recommended steps

1. locate the widget in Canvas or Structure
2. select the widget
3. confirm the Inspector target is correct
4. edit content or style
5. review the result in context
6. continue refining or commit/discard as needed

### Best use cases

- text updates
- KPI value presentation tweaks
- image swapping
- chart appearance refinement
- local style corrections

---

## Workflow 2: Reorganize Layout

Use this when the structure exists but the arrangement needs improvement.

### Recommended steps

1. identify the affected layout region
2. select the relevant layout node or containing structure
3. use drag, resize, reorder, alignment, or spacing tools
4. watch visual guides and structure updates
5. check that slot hosting still makes sense
6. compare against baseline if the change is broad

### Good practice

Do not treat layout changes like arbitrary freehand movement.
Always keep structure legibility in mind.

---

## Workflow 3: Insert a Prefab

Use this when a scene needs a new block that matches an approved composition pattern.

### Recommended steps

1. identify a valid target slot
2. open the Prefab Library
3. review compatible options
4. insert the selected prefab
5. adjust content and style
6. confirm the resulting structure is still coherent

### Best use cases

- standard KPI sections
- chart cards
- headers
- visual dividers
- common information blocks

---

## Workflow 4: Improve Visual Treatment

Use this when structure is already acceptable but visual quality needs refinement.

### Recommended steps

1. select the scene, container, or widget
2. use Inspector controls for typography, color, background, effects, or chart appearance
3. review the effect on the live scene
4. compare against baseline if needed
5. reset or discard if the treatment degrades clarity

### Good practice

Visual treatment should support readability and hierarchy, not just decoration.

---

## Workflow 5: Compare and Revert

Use this when you have made meaningful draft changes and need to confirm quality before accepting them.

### Recommended steps

1. pause editing
2. compare draft against baseline
3. identify what actually changed
4. decide whether to:
   - keep everything
   - reset a local scope
   - discard the draft
   - continue refining

### Why it matters

This workflow is central to user trust.
A live editor without good compare/revert habits becomes risky quickly.

---

## Workflow 6: Work Through Structure First

Use this when the canvas is visually dense or ambiguous.

### Recommended steps

1. open Structure
2. find the relevant scene region
3. select the correct slot or widget
4. use Inspector from a structurally clear target
5. confirm the canvas selection matches expectations

### Best use cases

- complex nested scenes
- multiple similar widgets
- dense chart or metric regions
- layout debugging from an authoring perspective

---

## Workflow 7: Replace a Visual Block

Use this when the current block is structurally valid but visually or semantically wrong.

### Recommended steps

1. locate the current widget and its host slot
2. confirm slot compatibility requirements
3. replace with a valid prefab or widget configuration
4. review visual and structural coherence
5. verify that surrounding layout remains sound

### Good practice

Prefer controlled replacement over destructive ad hoc rebuilding.

---

## Workflow 8: Safe Incremental Editing

Use this when changing high-visibility scenes or large layouts.

### Recommended steps

1. make one coherent change cluster at a time
2. review preview after each cluster
3. compare against baseline frequently
4. avoid mixing unrelated edits into one draft unless necessary
5. commit in deliberate stages where product workflow allows

This keeps risk low and reviewability high.

---

## Workflow 9: Chart Improvement Workflow

Charts often need more careful treatment than other widgets.

### Recommended steps

1. select the chart widget
2. review the chart’s role in the scene
3. adjust chart type, palette, labels, padding, and chrome
4. compare readability before and after
5. ensure the chart still fits its slot and surrounding hierarchy
6. commit only when the result is visually and semantically stronger

---

## Workflow 10: Prepare for Future Custom Region Work

When future bounded custom widget support exists, the correct workflow should be:

1. identify an approved custom-capable slot
2. confirm the slot’s purpose and bounds
3. choose custom widget path deliberately
4. work within restricted capabilities
5. verify local containment and integration quality

This is intentionally different from arbitrary code insertion.

---

## Workflow Anti-Patterns

Avoid these patterns:

- editing without understanding what is selected
- making large visual changes with no compare step
- treating every problem like a layout problem when it is really a slot or widget issue
- forcing structure through visual hacks
- rebuilding reusable blocks manually when a prefab exists
- using the Composer as an operations or diagnostics console

---

## Team Workflow Guidance

For collaborative or multi-role environments:

- align on scene purpose before editing
- use canonical prefabs where possible
- avoid broad edits without structural review
- treat baseline comparison as a normal quality step
- document or communicate broad scene revisions clearly

---

## Summary

The best way to use Live Scene Composer is through structured workflows: select clearly, inspect context, make bounded changes, preview in context, compare against baseline, and then commit or revert deliberately. Strong workflows are how users get power without chaos.
