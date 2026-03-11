# 33_FEATURE_REFERENCE

## Document Status

- Status: Canonical
- Audience: Users, Product, Support, Enablement
- Scope: Reference-style description of the product's major features and behavior categories

---

## Purpose

This document provides a structured reference for Live Scene Composer features. It is intended as a stable catalog of what the product is expected to support conceptually.

This is not a marketing page.
It is a practical feature map.

---

## Feature Categories

The Composer feature set is best understood in categories:

1. workspace and navigation
2. selection and targeting
3. structure and layout editing
4. content editing
5. visual styling
6. widget and prefab workflows
7. draft and recovery workflows
8. extension and safety mechanisms

---

## Workspace and Navigation Features

### Canvas Workspace

The Canvas is the real visual authoring surface where users interact with the rendered scene.

Expected capabilities:

- live preview
- selection
- visible bounds or handles where relevant
- direct manipulation for supported targets
- immediate visual context for edits

### Structure View

Structure provides a hierarchical view of the scene composition.

Expected capabilities:

- tree-based navigation
- selection sync
- visibility into layout, slots, and widgets
- ordering awareness
- clearer targeting in dense scenes

### Inspector

The Inspector shows contextual controls for the current selection.

Expected capabilities:

- target-aware editing panels
- relevant controls only
- property grouping by feature area
- direct connection to preview state

---

## Selection and Targeting Features

Expected capabilities:

- select from canvas
- select from structure
- reflect selected target consistently
- show contextual inspector content
- support editing of scene, layout, slot, or widget level targets as appropriate

Selection is the activation point for most authoring behavior.

---

## Layout and Structure Features

Expected capabilities:

- move supported layout targets
- resize supported layout targets
- reorder supported layout targets
- align and space elements where supported
- show guides or snapping
- preserve structural clarity
- keep slot placement and hierarchy understandable

Layout editing is one of the core product capabilities.

---

## Content Editing Features

Expected capabilities:

- text updates
- rich text style adjustments where supported
- image or media source changes where supported
- metric and label editing
- widget prop editing through bounded controls

The product should support meaningful content changes without requiring users to work through raw internal data structures.

---

## Typography Features

Expected capabilities:

- font family
- font size
- font weight
- line height
- letter spacing
- alignment
- color
- opacity
- truncation or clamp behavior where supported

Typography is a first-class feature area, not a secondary afterthought.

---

## Visual Styling Features

Expected capabilities:

- backgrounds
- color changes
- border or chrome treatment
- shadow
- glow
- opacity
- spacing and padding adjustments
- card treatment
- scene or container visual refinement

These features give users direct control over presentation quality.

---

## Chart Features

Expected capabilities:

- chart widget selection
- chart type changes where supported
- palette updates
- label adjustments
- spacing and padding tuning
- card chrome changes
- presentation improvement workflows

Chart authoring should be treated as a serious feature area because it is often a high-value visual component in a scene.

---

## Widget Features

Expected capabilities:

- select widget
- edit widget props
- edit widget style
- show widget-specific inspector controls
- move or reorder within valid structural contexts
- replace or remove within governed flows

Widgets are the concrete building blocks users interact with most directly.

---

## Prefab Features

Expected capabilities:

- browse prefab library
- search prefabs
- filter by compatibility or category
- insert compatible prefab into a valid slot
- start from strong defaults
- edit resulting widget instances after insertion

Prefabs are an acceleration mechanism for composition.

---

## Slot Features

Expected capabilities:

- make slot structure visible enough to reason about
- target slot for insertion
- understand compatibility constraints
- host widgets within bounded rules
- eventually host bounded custom widgets in approved flows

Slots are part of the authoring model even if users do not always think about them explicitly.

---

## Draft, Compare, and Recovery Features

Expected capabilities:

- draft editing
- preview changes
- compare against baseline
- reset selected scope where supported
- discard draft
- commit accepted changes

These features are essential for trust in a live authoring product.

---

## Module-Based Feature Growth

The product should also support modular growth such as:

- typography module
- backgrounds module
- effects module
- chart appearance module
- prefab browsing module
- future snapshots/presets modules

This is important because the product is expected to expand without becoming monolithic.

---

## Safety and Governance Features

Expected capabilities include system-level rules such as:

- Safe Mode operation
- bounded mutation paths
- bridge validation
- architecture-preserving extension
- protected authoring flows

These are not always visible as “features” to end users, but they are crucial to product correctness.

---

## Future Extension Features

The long-term system may include:

- more advanced variants and themes
- richer snapshots
- stronger compare workflows
- bounded custom widgets
- advanced but governed authoring capabilities

These should be introduced deliberately, not by weakening the existing architecture.

---

## Summary

The feature set of Live Scene Composer spans workspace navigation, selection, structure, layout editing, content and visual styling, widgets, prefabs, draft workflows, and governed extensibility. This feature reference exists to keep product capabilities legible as the system evolves.
