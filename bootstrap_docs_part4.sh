#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="${1:-docs}"
mkdir -p "$DOCS_DIR"

cat > "$DOCS_DIR/31_USER_MANUAL.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/32_WORKFLOW_GUIDE.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/33_FEATURE_REFERENCE.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/34_UI_INTERACTION_MODEL.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/35_THEME_AND_STYLE_SYSTEM.md" <<'EOF'
# 35_THEME_AND_STYLE_SYSTEM

## Document Status

- Status: Canonical
- Audience: Product, Design, Engineering
- Scope: Styling model, theming concepts, visual consistency, and style application rules

---

## Purpose

This document defines the Theme and Style System for Live Scene Composer. It exists to ensure that visual styling is powerful, structured, and consistent rather than becoming an uncontrolled set of per-widget overrides with no design logic.

Styling should create quality, not visual entropy.

---

## Style System Summary

The style system should support multiple layers of visual control:

- scene-level visual context
- layout or container-level treatment
- widget-level style
- prefab defaults
- future themes and variants
- local overrides where appropriate

The system must preserve the distinction between:

- content
- structural layout
- style and treatment

---

## Why a Style System Matters

Without a structured style system, users end up with:

- inconsistent typography
- random color usage
- uneven spacing
- duplicated visual decisions
- hard-to-maintain scenes
- no clear path for theme reuse or variation

The style system exists to make visual editing scalable.

---

## Style Layers

### Scene-level style

This includes broad visual context such as:

- scene background
- overall theme context
- high-level visual treatment
- global presentation tone

### Layout/container style

This includes:

- region treatment
- spacing behavior
- panel or card chrome
- grouping treatment

### Widget-level style

This includes:

- typography
- color
- background
- spacing
- border treatment
- local effects

### Prefab defaults

Prefabs should carry opinionated style defaults that can then be refined at instance level.

---

## Typography System

Typography should be a first-class part of the style system.

Expected controls may include:

- font family
- size
- weight
- line height
- letter spacing
- alignment
- emphasis
- truncation or clamp behavior where relevant
- color and opacity

Typography is too central to be treated as an afterthought.

---

## Color and Background System

The style system should support:

- background color
- background treatment
- card or surface color
- contrast-conscious text and accent usage
- hierarchy through color, not just decoration

Users should be able to improve clarity and hierarchy through style, not merely change colors at random.

---

## Effects System

The style system may include bounded effects such as:

- shadow
- glow
- opacity
- blur where appropriate
- border emphasis
- depth treatment

Effects should enhance hierarchy and presentation, not degrade readability.

---

## Chart Appearance Styling

Charts often need style beyond data display.

Chart style capabilities may include:

- palette
- label treatment
- padding
- card or panel chrome
- title/subtitle styling
- contrast treatment

Chart appearance should be treated as a legitimate styling domain, not a special-case hack.

---

## Themes

Themes are higher-level style configurations that influence multiple parts of the scene consistently.

A theme may affect:

- palette
- typography family or rhythm
- card treatment
- default spacing feel
- visual tone

Themes should be layered in a way that does not destroy local editability.
They should guide appearance, not eliminate useful control.

---

## Variants

Variants are controlled visual alternatives within an approved pattern.

Examples:

- light vs dark treatment
- executive vs dense view
- emphasis variants for a prefab family

Variants are useful because they provide consistency with controlled difference.

---

## Style Inheritance and Override

The system should support a clear mental model for how style is applied.

A healthy model may include:

- scene-level defaults
- prefab defaults
- widget or container-level overrides
- local targeted changes

Overrides should remain understandable.
Users should not have to reverse-engineer why a color or font is coming from somewhere.

---

## Reset and Recovery

The style system should support bounded recovery actions such as:

- reset selected widget style
- reset local treatment
- discard draft style changes
- compare against baseline

If style control is powerful, recovery must also be strong.

---

## Style Anti-Patterns

The system must reject:

- uncontrolled override stacking with no clear precedence
- styling behavior hidden in unrelated modules
- treating content props and style props as the same thing
- theme systems that silently override everything without visibility
- style controls that create chaos faster than they create quality

---

## Summary

The Theme and Style System exists to give Live Scene Composer powerful visual control without visual entropy. It should support scene-level styling, typography, color, effects, chart appearance, prefab defaults, themes, and variants, while keeping precedence and local overrides understandable.
EOF

cat > "$DOCS_DIR/36_DATA_BINDING_MODEL.md" <<'EOF'
# 36_DATA_BINDING_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product
- Scope: Conceptual data binding rules, boundaries, and future-safe handling of data-driven widgets

---

## Purpose

This document defines the Data Binding Model for Live Scene Composer. It exists because many widgets and visual elements may eventually depend on data, but the system must not let data flows become a hidden second architecture that bypasses the scene model, widget model, or mutation rules.

Data binding should remain structured and explicit.

---

## Data Binding Summary

The Composer should support the idea that some widgets render data-driven content, but binding must remain:

- bounded
- typed where possible
- understandable
- compatible with widget identity
- separate from raw unrestricted runtime access
- consistent with draft and preview semantics

The system should treat data binding as an explicit concern, not as a hidden implementation accident.

---

## What Data Binding Means Here

Data binding means associating a widget or widget property with some approved data source, derived value, or structured payload so the widget can render meaningful content.

Examples include:

- KPI value binding
- chart series binding
- table data source binding
- text widget binding to approved structured content
- conditional visual states from approved status data

---

## What Data Binding Is Not

Data binding is not:

- unrestricted query execution
- arbitrary runtime code access
- hidden implicit data mutation
- direct access to all available platform data
- a replacement for widget props
- a secret way around authoring constraints

The Composer should not become a general-purpose unbounded data scripting environment.

---

## Binding Principles

### 1. Explicit over implicit

Bindings should be declared, not guessed from scattered runtime behavior.

### 2. Widget-aware

Bindings belong to widgets or widget sub-properties, not to random invisible global state.

### 3. Read-oriented by default

The default posture for binding should be reading approved data, not mutating data systems.

### 4. Bounded sources

Bindings should use approved data sources or contracts, not arbitrary access to anything reachable.

### 5. Preview-compatible

Bindings should behave in ways that make preview and accepted state understandable.

---

## Binding Targets

Bindings may apply to:

- widget props
- specific presentation fields
- chart series config
- KPI values and labels
- table content
- status indicators

Bindings should remain target-aware and not turn the widget into an opaque blob of remote behavior.

---

## Binding Sources

Binding sources should be approved and scoped.

Examples may include:

- scene-provided data context
- approved resolved dataset references
- stable view-model-style data contracts
- safe computed value providers

The system should avoid allowing each widget to reach anywhere it wants for data.

---

## Binding and Widget Props

A binding should not erase the existence of widget props.
Instead, bindings should be part of how props are supplied or resolved.

This matters because:

- widgets still need stable local identity
- compare/revert still needs to make sense
- authoring UX still needs visible, editable structure
- bindings should remain inspectable and understandable

---

## Binding Visibility in the Product

Users should be able to tell when a widget is data-bound.

Helpful UI signals may include:

- binding indicators
- binding source summary
- read-only or derived value cues
- explicit binding editor surfaces in future versions

Invisible binding logic is a recipe for confusion.

---

## Binding and Preview

The system should define what preview means for data-bound widgets.

Examples of important questions:

- is the preview using current live data
- is it using resolved sample data
- are some style changes previewed while data remains stable
- what does compare show if style changed but data is derived

These questions should be answered by design, not discovered by accident.

---

## Binding Mutations

Changes to bindings should be treated as governed authoring changes when supported.

Examples:

- change binding source
- change field mapping
- remove binding
- switch from static prop to bound prop

These actions should remain explicit and should not bypass the mutation model.

---

## Future Scope Discipline

Data binding is important, but should not be allowed to dominate early MVP scope.
The product should first establish:

- strong scene structure
- strong slot/widget model
- strong mutation governance
- strong authoring UX

Then richer binding behavior can grow on a more stable foundation.

---

## Data Binding Anti-Patterns

The system must reject:

- hidden data reads from arbitrary internals
- widgets with invisible business logic embedded in ad hoc binders
- bindings that mutate unrelated systems
- turning the Composer into a data scripting console
- binding behavior that cannot be inspected or reasoned about

---

## Summary

The Data Binding Model should allow data-driven widgets in a bounded, explicit, widget-aware way. Binding must remain understandable, source-scoped, and compatible with the rest of the Composer architecture. Data is important, but it must not become a loophole around structure, visibility, or governance.
EOF

cat > "$DOCS_DIR/37_VERSIONING_MODEL.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/38_CHANGELOG.md" <<'EOF'
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
EOF

cat > "$DOCS_DIR/39_ROADMAP.md" <<'EOF'
# 39_ROADMAP

## Document Status

- Status: Canonical
- Audience: Product, Architecture, Engineering, Leadership
- Scope: Planned evolution of Live Scene Composer from foundation through mature capability growth

---

## Purpose

This document defines the roadmap for Live Scene Composer at a strategic level. It exists to guide sequencing, keep scope disciplined, and avoid mixing foundational work with future ambition in a way that destabilizes the product.

A roadmap should preserve direction, not create fantasy commitments.

---

## Roadmap Principles

The roadmap should prioritize:

- strong foundations first
- MVP usefulness before broad expansion
- safety before power
- structural clarity before advanced complexity
- modular growth before feature sprawl
- contract stability before extension explosion

The Composer should grow in layers, not as a pile of simultaneous ambitions.

---

## Phase 0: Foundation and Boundary Hardening

### Goals

- establish canonical project identity
- separate Composer from Runtime Debug Console
- establish `console-core` as shared infrastructure
- establish `runtime-mutation-bridge` as controlled write boundary
- document the core system thoroughly
- define dependency policy and protected nodes
- create hardening guardrails

### Outcomes

- strong conceptual model
- clear ownership boundaries
- durable foundation for implementation work

---

## Phase 1: Minimum Safe Composer MVP

### Goals

- render a dedicated Composer shell
- support scene-aware selection
- support Canvas + Structure + Inspector interaction loop
- support basic layout movement and resizing where appropriate
- support text and typography editing
- support basic styling and background editing
- support prefab insertion into valid slots
- support a small typed bridge command set
- support draft, compare, discard, and commit basics

### MVP Success Criteria

The MVP is successful when a user can make real visual composition changes safely and understand what changed.

### Out of Scope for MVP

- large custom widget platform
- broad scripting
- advanced responsive rules
- heavy data-binding complexity
- giant plugin ecosystem

---

## Phase 2: Strong Authoring Modules

### Goals

- deepen module-based authoring
- improve chart appearance tools
- improve layout tooling
- improve visual styling system
- improve structure operations
- strengthen reset/revert granularity

### Expected Additions

- richer typography controls
- stronger chart editing surfaces
- better alignment and guide support
- improved visual treatment modules
- stronger module registration and isolation behavior

---

## Phase 3: Reuse, Presets, and Variation

### Goals

- strengthen prefab system
- introduce presets and reusable composition states
- introduce stronger compare and snapshot workflows
- begin richer variants and theme logic

### Outcomes

- faster authoring
- more reusable composition patterns
- stronger scene consistency

---

## Phase 4: Bounded Advanced Capability

### Goals

- introduce carefully governed advanced authoring paths
- deepen bridge policy where needed
- introduce stronger future-ready custom widget surfaces
- expand mode-aware capability safely

### Important Rule

This phase should happen only after foundation and safe workflows are proven.
It must not become a shortcut that rewrites the earlier discipline.

---

## Phase 5: Mature Extension and Ecosystem Integration

### Goals

- strengthen extension points
- improve tooling and validation around modules and bindings
- support richer future integrations
- allow the Composer to function as a durable platform rather than only a first-party tool

### Preconditions

- protected seams remain strong
- mutation governance remains intact
- dependency policy remains enforced
- extension safety is proven, not assumed

---

## Current Strategic Priority

The current highest priority is not “maximum feature count.”
The highest priority is:

- strong Composer foundation
- clear provider and wiring seams
- minimum safe bridge commands
- useful MVP authoring loop
- preserved boundary discipline

This is the right order because it avoids paying for undisciplined growth later.

---

## Roadmap Risks

The roadmap can fail if the team:

- inflates the MVP
- reintroduces debug/composer coupling
- weakens bridge discipline
- ignores slot/widget/layout contract clarity
- over-prioritizes advanced power before safe usability
- lets extension needs dominate before the base system is stable

---

## Summary

The roadmap for Live Scene Composer begins with boundary hardening and a safe useful MVP, then grows into richer authoring modules, reuse systems, variation tools, and eventually bounded advanced extension. The roadmap is intentionally disciplined so the product can become powerful without becoming chaotic.
EOF

cat > "$DOCS_DIR/40_ARCHITECTURAL_DECISIONS.md" <<'EOF'
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
EOF

echo "[OK] Generated Part 4 docs in: $DOCS_DIR"
echo "[OK] Files created:"
ls -1 "$DOCS_DIR"/31_USER_MANUAL.md \
      "$DOCS_DIR"/32_WORKFLOW_GUIDE.md \
      "$DOCS_DIR"/33_FEATURE_REFERENCE.md \
      "$DOCS_DIR"/34_UI_INTERACTION_MODEL.md \
      "$DOCS_DIR"/35_THEME_AND_STYLE_SYSTEM.md \
      "$DOCS_DIR"/36_DATA_BINDING_MODEL.md \
      "$DOCS_DIR"/37_VERSIONING_MODEL.md \
      "$DOCS_DIR"/38_CHANGELOG.md \
      "$DOCS_DIR"/39_ROADMAP.md \
      "$DOCS_DIR"/40_ARCHITECTURAL_DECISIONS.md