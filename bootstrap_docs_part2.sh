#!/usr/bin/env bash
set -euo pipefail

DOCS_DIR="${1:-docs}"
mkdir -p "$DOCS_DIR"

cat > "$DOCS_DIR/11_MODULE_SYSTEM.md" <<'EOF'
# 11_MODULE_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation
- Scope: Module architecture, boundaries, lifecycle, and governance for Live Scene Composer

---

## Purpose

This document defines the module system for Live Scene Composer. Its purpose is to ensure that feature growth happens through bounded, removable, testable units rather than through uncontrolled expansion of product logic across the codebase.

The module system is not a convenience pattern. It is one of the core architectural defenses that keeps the Composer from becoming a monolith.

---

## Why a Module System Exists

Live Scene Composer is expected to grow across multiple domains:

- layout
- typography
- backgrounds
- effects
- charts
- prefabs
- structure tooling
- snapshots
- future themes and variants
- future bounded custom widget support

Without a module system, these concerns tend to collapse into a single application layer, which creates:

- hidden coupling
- unbounded imports
- high blast radius changes
- difficult removability
- accidental ownership confusion
- weak validation surfaces

A module system exists to make growth governable.

---

## Module System Goals

The module system must achieve the following:

1. allow feature growth without collapsing boundaries
2. make feature ownership explicit
3. support registration discipline
4. support selective enablement or removal
5. provide a clean place for feature-specific panels, actions, and schema
6. support validation and cleanup
7. reduce system-wide breakage when one module fails

---

## Module Definition

A module is a bounded feature unit that extends the Composer through approved seams.

A module may contribute:

- inspector sections
- canvas tools or overlays
- structure actions
- widget-type support
- slot-aware behaviors
- mutation helpers
- validation hooks
- local state or lifecycle behavior
- feature-specific configuration or schema

A module is not just a folder of code. It is a declared, governed unit of capability.

---

## Module Design Principles

### 1. Modules must be explicit

A module should have clear identity, declared capabilities, clear registration behavior, and clear ownership.

### 2. Modules must remain bounded

A module should only depend on what it truly needs. It should not reach across the system and acquire broad authority by convenience.

### 3. Modules must be removable

If a module proves unstable, irrelevant, or poorly designed, it should be possible to disable or remove it without dismantling the product.

### 4. Modules must fail locally where possible

A broken module should not crash the whole Composer shell or corrupt unrelated authoring state.

### 5. Modules must obey product boundaries

Modules are part of Live Scene Composer. They are not allowed to reintroduce runtime-debug coupling or bypass mutation governance.

---

## Module Categories

The system may support multiple kinds of modules.

### Authoring modules

Examples:

- typography module
- backgrounds module
- chart appearance module
- layout tools module
- effects module

These primarily extend editing capability.

### Structural modules

Examples:

- structure tree helpers
- slot management helpers
- selection refinement tooling

These primarily extend scene understanding or composition structure.

### Widget capability modules

Examples:

- text widget support
- chart widget support
- KPI widget support
- image widget support

These help the system handle widget-specific authoring behavior.

### Workflow modules

Examples:

- compare/revert tools
- snapshots
- presets
- future variants

These extend the authoring workflow around change management and reuse.

---

## What a Module May Own

A module may own:

- feature-specific UI surfaces
- feature-specific local state
- feature-specific validation rules
- feature-specific mutation wrappers
- feature-specific defaults and schemas
- feature-specific cleanup logic

A module should not quietly become the owner of core product architecture or unrelated feature domains.

---

## What a Module Must Not Own

A module must not own:

- global mutation bypass
- shared infrastructure responsibilities that belong in console-core
- the entire scene model
- runtime-debug-only concerns
- unrestricted runtime access
- unrelated module state by stealth
- product-wide registry power without approval

---

## Module Registration

Modules should register through explicit Composer registration seams.

Registration should be capable of describing:

- module identity
- module version
- module capabilities
- inspector contributions
- widget or slot relevance
- required dependencies
- optional dependencies
- cleanup hooks
- enablement flags
- safe mode compatibility
- advanced mode compatibility

Module registration must be deterministic and testable.

---

## Module Lifecycle

A healthy module lifecycle should include:

1. declaration
2. registration
3. activation
4. runtime contribution
5. disposal / cleanup

The exact mechanics may vary, but lifecycle clarity matters because dynamic or optional modules otherwise become a source of leaks and inconsistent behavior.

### Declaration

The module states what it is and what it contributes.

### Registration

The system decides whether the module may participate in the current Composer environment.

### Activation

The module becomes live and can contribute approved behaviors or surfaces.

### Disposal

The system removes the module cleanly and tears down any local state, subscriptions, or ephemeral UI effects.

---

## Module Manifest Expectations

Each module should have a declared manifest or equivalent typed registration structure that answers:

- what is this module called
- what category is it
- what capabilities does it contribute
- what parts of the system can it extend
- what prerequisites does it need
- what modes can it run in
- what cleanup is required
- what validation should apply if it changes

The goal is to make module behavior explicit instead of tribal.

---

## Safe Mode and Module Participation

Not all modules need the same authority.

Some modules are Safe Mode compatible by default, such as:

- typography
- backgrounds
- simple layout tools
- visual effects within policy
- prefab browsing

Some future modules may require stronger gating and should not appear as default capabilities.

The module system should be able to distinguish:

- always-safe modules
- conditionally safe modules
- advanced-only modules
- disabled modules

---

## Failure Isolation

Failure isolation must be a design requirement.

Expected behavior:

- a broken inspector section from one module should not blank the entire inspector
- a widget capability module failure should degrade locally
- a module should not corrupt unrelated state on activation failure
- the Composer shell should remain stable if a non-core module fails

This is one of the main reasons the system is modular at all.

---

## Dependency Discipline

Modules should depend inward on allowed Composer seams, not outward into unrelated system internals.

Preferred dependency style:

- module -> composer contracts
- module -> scene model contracts
- module -> mutation wrappers
- module -> shared UI primitives where appropriate

Disallowed dependency style:

- module -> runtime internals directly
- module -> runtime-debug-console
- module -> hidden route-binding hacks
- module -> sibling module private internals without explicit contract

---

## Minimum Initial Modules

The early Composer should likely begin with a modest module set such as:

- layout module
- typography module
- backgrounds module
- effects module
- chart appearance module
- prefab library module

This gives strong authoring value while preserving manageable scope.

---

## Module System Anti-Patterns

The module system must reject:

- modules with no declared ownership
- modules that directly mutate runtime state
- one module importing everything and behaving like a hidden monolith
- “temporary” modules that bypass registration
- putting feature logic into console-core because multiple people use it
- modules that cannot be removed because they secretly own core flows

---

## Validation Expectations

The module system should support:

- registration tests
- allowed dependency checks
- module manifest checks
- enable/disable checks
- failure-isolation tests
- mode compatibility checks

This is how the module system becomes a real architecture tool rather than a naming convention.

---

## Summary

The Live Scene Composer module system is the mechanism by which the product grows without collapsing. Modules must be explicit, bounded, removable, and governable. They should contribute capability through approved seams, remain subject to dependency discipline, and fail locally where possible. A healthy module system is one of the strongest defenses against long-term product and architecture decay.
EOF

cat > "$DOCS_DIR/12_MODULE_SDK.md" <<'EOF'
# 12_MODULE_SDK

## Document Status

- Status: Canonical
- Audience: Engineering, Architecture, Tooling
- Scope: Module-facing APIs, registration contracts, and contribution surfaces

---

## Purpose

This document defines the shape and intent of the Module SDK for Live Scene Composer. The SDK is the formal interface between the Composer platform and feature modules.

Its purpose is to answer a simple but critical question:
How may modules extend the Composer without destabilizing it?

---

## Why an SDK Exists

A module system without an SDK devolves into informal imports, private assumptions, and duplicated patterns. The Module SDK exists so that modules can be built against explicit, stable seams rather than against whichever internal component happened to be available at the time.

The SDK is what turns modularity from aspiration into practice.

---

## SDK Goals

The Module SDK should:

1. provide a stable registration seam
2. define contribution points explicitly
3. limit what modules can see and do
4. reduce coupling to internal application implementation details
5. make future refactoring safer by preserving a formal extension contract
6. support tooling and validation
7. allow safe feature growth without encouraging product sprawl

---

## SDK Scope

The Module SDK should cover:

- module identity and manifest contracts
- registration contracts
- capability declarations
- contribution APIs
- context access rules
- mutation helper access
- cleanup lifecycle
- mode compatibility
- validation expectations

It should not expose unrestricted access to the full Composer internals.

---

## Core SDK Principle

Modules should be able to do useful work through a narrow, explicit surface.
They should not need privileged access to accomplish normal extension tasks.

A powerful narrow API is healthier than a vague giant one.

---

## Manifest Contract

A module should declare a manifest or equivalent typed descriptor that includes concepts such as:

- id
- display name
- version
- category
- capabilities
- supported targets
- safe mode compatibility
- advanced mode compatibility
- dependencies
- optional dependencies

The manifest exists so the system can reason about the module before loading it deeply.

---

## Registration Contract

The registration contract should answer:

- what the module contributes
- where the contributions belong
- what lifecycle hooks are required
- what contexts it may access
- what cleanup must occur on disable/unmount
- what validations are needed

Registration should be declarative and inspectable.

---

## Expected Contribution Types

A module may contribute some combination of the following.

### Inspector contributions

A module may contribute inspector sections or controls for relevant targets.

Examples:

- typography controls for text widgets
- background controls for containers or scenes
- chart appearance controls for chart widgets

### Canvas contributions

A module may contribute overlays, guides, handles, or interaction aids relevant to its domain.

These should remain bounded and not become hidden global behavior.

### Structure contributions

A module may contribute structure actions, icons, metadata, or structure-specific editing affordances.

### Validation contributions

A module may contribute validation rules or constraints relevant to its domain.

### Mutation wrapper contributions

A module may expose typed helper calls that route through approved mutation channels, rather than doing direct writes.

### Widget support contributions

A module may enhance authoring support for specific widget types.

---

## Module Context

The SDK may expose a module context object or equivalent, but that context must be carefully limited.

A healthy module context may include:

- current selection
- current scene id or scene reference
- read-only access to relevant scene model views
- approved mutation request helpers
- registration-time extension surfaces
- mode awareness
- logging or diagnostics hooks appropriate for the module
- cleanup helpers

A healthy module context must not include:

- unrestricted runtime internals
- direct low-level bridge bypass handles
- write-anything methods
- hidden backdoors to sibling products
- full ownership of unrelated module state

---

## Mutation Access Through SDK

The SDK should not give modules direct raw mutation authority.
Instead, it should provide one or more safe patterns such as:

- typed mutation helper factories
- scoped mutation request builders
- target-aware helper wrappers

The intent is that modules remain productive without bypassing runtime-mutation-bridge or inventing their own mutation semantics.

---

## Lifecycle Hooks

The SDK should support a small, explicit lifecycle.

Typical lifecycle hooks may include:

- register
- activate
- dispose

Optional lifecycle concepts may include:

- onSelectionChanged
- onModeChanged
- onSceneChanged

These should remain bounded and not turn into a giant event soup.

---

## Cleanup Expectations

The SDK must make cleanup part of the module contract.

Modules should clean up:

- subscriptions
- overlays
- temporary state
- listeners
- timers
- structure decorations
- canvas contributions

A module that contributes to the environment but cannot clean up after itself is not production-ready.

---

## Mode Awareness

The SDK should allow modules to declare and inspect mode compatibility.

Examples:

- safe-only
- safe-and-advanced
- advanced-only

This matters because not every module should be active under all authority levels.

---

## Versioning and Compatibility

The SDK should be versioned or at least compatibility-conscious.

The system should be able to answer:

- what SDK version a module targets
- whether a manifest is still compatible
- whether a module relies on deprecated extension points

Even if formal semantic versioning comes later, the concept must be anticipated now.

---

## Validation and Tooling

The SDK should be designed so tooling can validate:

- required manifest fields
- illegal contribution surfaces
- mode compatibility declarations
- missing cleanup
- dependency rule violations
- unsupported capabilities

The easier the SDK is to validate, the more safely the module ecosystem can grow.

---

## What the SDK Must Not Become

The SDK must not become:

- a disguised full internal API export
- a convenience portal to unstable product internals
- a mutation bypass surface
- a place where permissions are assumed instead of declared
- a dumping ground for arbitrary helper methods

If the SDK becomes “just import whatever you need,” it has failed.

---

## Minimal Early SDK Direction

The initial SDK can stay focused.

A small but strong v1 SDK might provide:

- module manifest type
- registration entry point
- inspector contribution API
- selection-aware context
- typed mutation helper access
- cleanup registration
- mode inspection

That is enough to support real modules without over-designing the system.

---

## Summary

The Module SDK is the formal extension contract between Live Scene Composer and its modules. It should provide stable, narrow, useful APIs for registration, context access, inspector contribution, mutation helpers, and cleanup—without exposing unrestricted internals. A strong SDK is what allows modularity to scale without turning into chaos.
EOF

cat > "$DOCS_DIR/13_WIDGET_SYSTEM.md" <<'EOF'
# 13_WIDGET_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product, Design
- Scope: Widget definition, lifecycle, capabilities, and authoring behavior

---

## Purpose

This document defines the Widget System for Live Scene Composer. Widgets are the concrete renderable units users see and manipulate inside slots. The system exists to make widget behavior structured, composable, and governable.

Widgets are one of the most visible parts of the product, so ambiguity here quickly becomes product confusion.

---

## Widget System Summary

A Widget is a renderable composition unit hosted inside a Slot.
Widgets are not layout owners, not scenes, and not mutation authorities.
They are concrete content or visual blocks with type-specific behavior, props, style, and runtime binding context.

The Widget System should support:

- clear widget identity
- predictable placement in slots
- widget-type capabilities
- widget props and style separation
- prefab-origin support
- safe editing through inspector and mutation flows
- future bounded custom widget support

---

## Widget Responsibilities

A Widget is responsible for:

- representing a concrete visual/content block
- rendering according to widget type and configuration
- owning widget-level props
- owning widget-level style data
- exposing widget-type capabilities to the authoring system
- participating in preview and selection

A Widget is not responsible for:

- defining scene-wide structure
- owning layout tree logic
- bypassing mutation governance
- operating as unrestricted code execution

---

## Widget Identity

Each widget should have a stable identity.

Expected identity concerns include:

- widget id
- widget type
- owning slot id
- optional originating prefab id
- optional runtime binding info
- visibility / lock state

Stable identity matters for:

- selection
- structure view
- mutation targeting
- compare / revert
- testability

---

## Widget Types

Early widget types may include:

- text
- rich text
- image
- KPI
- chart
- table
- container widget
- custom widget

The system should treat widget type as a first-class concept, because type influences:

- inspector surface
- allowed props
- allowed styles
- slot compatibility
- rendering behavior
- future validation behavior

---

## Widget Capabilities

Each widget type should imply or declare capabilities.
Capabilities are useful for reasoning about what the system may do with a widget.

Possible capabilities include:

- textual
- media
- metric
- chart
- layout-container
- custom

Capabilities may inform:

- slot acceptance
- inspector sections
- prefab compatibility
- module activation
- validation rules

---

## Widget Props vs Widget Style

The Widget System must distinguish between props and style.

### Widget props

Props describe semantic or functional content relevant to the widget type.

Examples:

- text content
- chart dataset reference
- image source
- KPI label/value
- table configuration

### Widget style

Style describes appearance and treatment.

Examples:

- typography
- colors
- spacing
- backgrounds
- border treatment
- glow, shadow, opacity
- chart palette and card chrome

This separation matters because content and visual treatment often evolve differently and need different validation and reset semantics.

---

## Widget Placement

Widgets live inside Slots.
This is a non-negotiable structural rule.

A widget should not exist in the scene with no host relationship.
This is important because:

- slots define insertion rules
- slots define bounded composition regions
- slots support safe prefab and future custom widget behavior
- structure view becomes much clearer when widget placement is explicit

---

## Widget Lifecycle

A healthy widget lifecycle includes:

1. creation or insertion
2. hosting within a valid slot
3. optional selection and editing
4. preview changes
5. accepted updates
6. optional movement or replacement
7. eventual removal

The lifecycle should remain legible to support validation, compare, and removability.

---

## Widget Selection and Editing

Widgets are common authoring targets.

The system should support:

- selection on canvas
- selection from structure
- inspector surfaces tailored to widget type
- move and reorder where valid
- style updates
- prop updates
- replacement by compatible prefab or widget type in controlled flows

Selection should not imply direct mutation. It should expose eligible editing flows through governed channels.

---

## Widget Validation

Widgets should be validated against:

- slot compatibility
- required props
- supported style shape
- widget type constraints
- runtime rendering constraints
- mode restrictions if relevant

This is especially important for complex widgets like charts and future custom widgets.

---

## Widget and Prefab Relationship

A prefab may create or initialize a widget, but the resulting live widget instance is distinct from the prefab definition.

This distinction is important because:

- the widget is mutable in the scene
- the prefab is a reusable template
- compare/revert works at instance level
- changing a live widget should not silently rewrite prefab definitions

---

## Container Widgets

The system may support container-style widgets, but care is required.

A container widget may visually group content or provide widget-level local structure, but it must not erase the distinction between:

- layout structure
- slot hosting
- widget rendering

Container widgets are useful, but should not become hidden layout engines that bypass the main layout model.

---

## Chart Widgets

Chart widgets deserve special care.

Users often need more than simple color editing. Chart widgets may require:

- chart-type changes
- palette changes
- label changes
- padding adjustments
- chrome or card treatment changes
- title/subtitle adjustments
- replacement with a different chart or metric representation

This should be handled as a serious widget capability area, not as a footnote.

---

## Custom Widgets

Custom widgets are a special widget type with stricter boundaries.

They should:

- render within bounded slot regions
- use restricted APIs
- fail locally
- avoid unrestricted DOM, filesystem, or runtime access
- remain visibly part of the Widget System, not a loophole around it

Custom widgets matter, but the base Widget System must be strong before they expand.

---

## Widget Anti-Patterns

The Widget System must reject:

- widgets with no stable identity
- widgets that directly own layout tree truth
- widgets that mutate runtime state directly
- widgets that exist outside valid slots
- widget instances that secretly rewrite prefab definitions
- “special widgets” that bypass system rules without explicit contract

---

## Summary

The Widget System defines the concrete units that users compose inside Live Scene Composer. Widgets live in slots, expose typed capabilities, separate props from style, and are edited through governed authoring flows. A strong Widget System is essential for meaningful composition, selection, validation, and future extensibility.
EOF

cat > "$DOCS_DIR/14_SLOT_SYSTEM.md" <<'EOF'
# 14_SLOT_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product
- Scope: Slot definitions, policies, hosting rules, and bounded composition behavior

---

## Purpose

This document defines the Slot System for Live Scene Composer. Slots are the bounded host regions that connect layout structure to concrete widget composition.

They are one of the most important concepts in the system because they prevent composition from collapsing into anonymous containers and uncontrolled placement.

---

## Slot System Summary

A Slot is a bounded composition region that accepts one or more widgets according to explicit policy.

Slots exist to provide:

- host semantics
- insertion rules
- capacity constraints
- bounded custom widget regions
- structure clarity
- safe replacement and composition flows

Without slots, widget placement becomes ambiguous and the system loses one of its strongest architecture anchors.

---

## Why Slots Exist

Slots solve several problems at once:

1. they create bounded composition regions
2. they connect layout structure to content placement
3. they define insertion compatibility
4. they support prefab insertion discipline
5. they provide the future host model for bounded custom widgets
6. they improve scene readability in structure view and mutation targeting

Slots are not UI decoration. They are part of the domain.

---

## Slot Responsibilities

A slot is responsible for:

- defining a host region
- identifying what kinds of widgets it accepts
- defining how many widgets it may host
- identifying whether custom widgets are allowed
- providing a stable target for insertion and replacement
- participating in layout/structure mapping

A slot is not responsible for:

- rendering concrete content by itself
- owning the whole layout tree
- replacing widget type semantics
- bypassing scene or mutation governance

---

## Slot Identity

Each slot should have a stable identity.

Expected concerns include:

- slot id
- slot name or label
- slot kind
- accepted capabilities or types
- max item count
- current widget ids
- lock state
- policies such as custom widget allowance

Stable identity matters for:

- structure view
- insertion
- mutation targeting
- compare/revert
- mapping between layout and composition

---

## Slot Kinds

The system may support multiple slot kinds such as:

- content
- media
- chart
- metric
- container
- custom

Slot kind helps express intent and constraints.
It should influence, but not wholly replace, explicit compatibility rules.

---

## Slot Acceptance Policy

A slot should express what kinds of widgets it may host.

This may be modeled through:

- accepted widget types
- accepted widget capabilities
- explicit allowlists
- capacity rules
- mode restrictions where relevant

Examples:

- a chart slot may accept chart widgets and maybe metric widgets
- a text slot may accept text-oriented widgets only
- a custom slot may allow custom widgets if policy permits

Acceptance policy is important because it keeps authoring understandable and prevents structurally incoherent scenes.

---

## Capacity and Ordering

Slots should define how many widgets they can host.

Examples:

- single-item slot
- multi-item stack-like slot
- bounded collection slot

Ordering rules matter whenever a slot can host multiple widgets.
These rules must remain explicit so reorder behavior is predictable.

---

## Slot and Layout Relationship

A slot is not the same as a layout node.

This distinction matters a lot.

### Layout node

- describes structural position in the layout tree

### Slot

- describes the host region for widget composition

A layout node may reference a slot, but they should not be fused into one anonymous concept.
This separation keeps the system flexible and structurally legible.

---

## Slot and Widget Relationship

A slot hosts widgets.
A widget belongs to a slot.

This relationship should remain explicit because it supports:

- insertion validation
- move/reparent operations
- replacement
- custom widget containment
- targeted reset and compare semantics

---

## Slot Visibility in the Product

Slots should be visible enough in the authoring experience that users can reason about structure.

Possible visibility mechanisms include:

- structure tree nodes
- canvas outlines during selection or insertion
- insertion affordances
- bounded region overlays
- slot labels in advanced structure views

A system with slots but no way to reason about them becomes confusing.

---

## Slot Editing

Slot editing should remain bounded.

Possible editable attributes include:

- label or display name
- acceptance policy
- capacity
- lock state
- visual placeholder treatment
- custom widget allowance

Slot editing should not become a side door for breaking layout or bypassing widget validation.

---

## Slots and Prefabs

Slots are one of the main things prefabs should target.

A healthy insertion flow is:

1. user selects or focuses a slot
2. system shows compatible prefabs
3. prefab is instantiated into widget instance(s)
4. slot capacity and policy are validated
5. preview and acceptance follow normal mutation rules

This is much safer than arbitrary free placement.

---

## Slots and Custom Widgets

Slots are the correct host concept for custom widgets.

A custom widget should:

- live inside an explicitly approved slot
- render inside slot bounds
- obey slot policy
- fail locally within that region

This is one of the strongest reasons the Slot System matters.

---

## Slot Anti-Patterns

The Slot System must reject:

- slots that are indistinguishable from widgets
- slots with no policy or bounded meaning
- placing widgets without a valid slot
- using layout nodes as secret slot substitutes
- creating “magic slots” that bypass validation
- custom widget placement without explicit slot approval

---

## Summary

The Slot System is the bounded host layer that connects layout to widgets. Slots define valid composition regions, acceptance policy, capacity, and future custom widget containment. They are essential to structural clarity, insertion safety, and long-term product coherence.
EOF

cat > "$DOCS_DIR/15_LAYOUT_SYSTEM.md" <<'EOF'
# 15_LAYOUT_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product, Design
- Scope: Layout structure, spatial organization, and layout editing behavior

---

## Purpose

This document defines the Layout System for Live Scene Composer. Layout is the structured spatial organization of the scene. It answers how regions are arranged, how composition is positioned, and how spatial structure is represented independently from content.

Layout must remain a first-class system because users need to author structure, not just content appearance.

---

## Layout System Summary

The Layout System is responsible for:

- structural composition
- region hierarchy
- ordering
- placement and sizing
- alignment and spatial relationships
- layout node tree management
- slot references within structure

The Layout System is not the same thing as widgets, slots, or scene metadata, even though it interacts with all of them.

---

## Why Layout Exists as Its Own System

Without an explicit Layout System, products tend to collapse into a flat set of components with ad hoc positioning rules. That quickly leads to:

- inconsistent structure
- fragile drag/drop behavior
- confused ownership
- unclear mutation semantics
- hard-to-maintain responsive behavior later
- hidden layout logic inside widgets or panels

Layout deserves its own model because spatial structure is a real part of authoring.

---

## Core Layout Concepts

The Layout System should represent structure through layout nodes.
Common conceptual node types may include:

- root
- stack
- grid
- container
- slot reference

Exact node types may evolve, but the system must preserve the distinction between structural nodes and content nodes.

---

## Responsibilities of Layout Nodes

A layout node may be responsible for:

- parent/child structural relationships
- ordering among children
- sizing constraints
- alignment rules
- spacing rules
- reference to a slot where content may appear
- layout-level visual treatment where appropriate

A layout node should not automatically become a widget or slot.
Those concepts remain distinct.

---

## Layout and Scene Relationship

A scene has a root layout.
The layout defines the structural organization of the scene.

This means:

- layout changes affect structure
- layout changes may change slot placement and widget presentation
- layout does not by itself define content semantics

---

## Layout and Slot Relationship

A layout node may reference a slot.
That reference tells the system where a host region exists within the structural arrangement.

This relationship is powerful because it lets the system separate:

- spatial structure
from
- content hosting

That separation improves clarity and future extensibility.

---

## Layout Editing Requirements

The Layout System should support meaningful authoring behavior such as:

- move
- resize
- reorder
- align
- snap
- grid-aware placement
- spacing adjustments
- structural reorganization

These should feel visual and immediate, while still producing governed mutations.

---

## Drag, Resize, and Reorder

These are central layout operations and should be treated seriously.

### Drag

Drag should move eligible structural targets in ways consistent with layout rules.

### Resize

Resize should alter size-related constraints within valid bounds.

### Reorder

Reorder should preserve structural clarity and not become arbitrary DOM shuffling.

All three should remain consistent with mutation policies, draft workflows, and compare/revert behavior.

---

## Guides, Grid, and Snapping

A strong layout authoring experience often needs:

- alignment guides
- snapping
- visible bounds
- optional grid systems
- insertion hints

These are not cosmetic luxuries. They are part of what makes layout editing precise instead of frustrating.

---

## Layout Mutations

Typical layout mutations may include:

- move layout node
- resize layout node
- reorder layout node
- change layout constraints
- reparent a layout node within valid rules

These mutations should be typed and routed through approved mutation flows rather than enacted as hidden component-local side effects.

---

## Layout Constraints

The Layout System should support explicit constraints where needed.

Potential constraints include:

- minimum/maximum dimensions
- stacking rules
- grid placement rules
- allowed child types
- slot-ref constraints
- mode restrictions for certain operations

The system does not need to solve every possible responsive rule on day one, but it should leave room for disciplined expansion.

---

## Layout Visibility in the Product

Users need enough visibility into layout structure to reason about it.

Helpful surfaces include:

- structure tree
- canvas outlines
- parent/child highlighting
- drop previews
- reordering markers
- selected bounds

A layout system hidden behind invisible assumptions becomes hard to trust.

---

## Layout and Widgets

Widgets may appear visually central to the user, but they do not replace layout structure.
A chart widget inside a slot inside a structural container is not itself the layout tree.

This distinction is essential to prevent a product where content blocks accidentally become the only structural truth.

---

## Layout and Container Widgets

Container widgets may provide local visual grouping, but should not erase the primary layout model.
Where container widgets exist, their relationship to layout must remain explicit and bounded.

The danger is letting container widgets smuggle in a second unofficial layout engine.

---

## Layout Anti-Patterns

The Layout System must reject:

- treating widgets as the only structure
- storing layout truth purely in transient UI state
- using DOM order as the only layout model
- confusing slot definitions with structural nodes
- “temporary” direct manipulations that never formalize into governed mutations
- hidden layout logic inside unrelated modules

---

## Summary

The Layout System is the structural spine of scene composition. It defines how regions are arranged, how slot references are placed, and how users manipulate spatial structure. It must remain distinct from widgets and slots, visible enough to reason about, and governed through typed mutation flows rather than informal UI side effects.
EOF

cat > "$DOCS_DIR/16_PREFAB_SYSTEM.md" <<'EOF'
# 16_PREFAB_SYSTEM

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Product, Design
- Scope: Prefab definitions, insertion behavior, compatibility, and reuse

---

## Purpose

This document defines the Prefab System for Live Scene Composer. Prefabs are reusable composition templates that accelerate authoring and create consistency without hard-coding the scene into inflexible layouts.

The Prefab System exists to make composition fast, structured, and reusable.

---

## Prefab System Summary

A Prefab is a reusable definition that can instantiate one or more widget instances, optionally with default structure, props, and style assumptions.

Prefabs should support:

- fast insertion
- repeatable composition patterns
- compatibility with valid slots
- sensible defaults
- safe replacement or reuse workflows
- structured growth of the authoring ecosystem

A Prefab is not the same thing as a live widget instance.

---

## Why Prefabs Exist

Prefabs solve several real authoring needs:

- users should not build every scene element from scratch
- common blocks should be reusable
- composition should move faster
- structure and visual quality should improve through good defaults
- insertion should remain governed instead of arbitrary

Without prefabs, authoring becomes slower, less consistent, and more vulnerable to low-quality ad hoc assembly.

---

## Prefab Responsibilities

A prefab is responsible for:

- naming a reusable composition unit
- declaring its intended category
- declaring what slot kinds it can be inserted into
- defining default props and style
- optionally defining multi-widget or compound structure
- enabling repeatable composition patterns

A prefab is not responsible for:

- being the live mutable instance in the scene
- bypassing slot validation
- bypassing mutation flows
- owning unrelated scene state

---

## Early Prefab Categories

Early useful prefab categories may include:

- text
- rich text
- image
- KPI
- chart
- table
- badge / status
- hero / header
- spacer / divider
- container / stack

Compound prefabs may later include:

- executive KPI section
- chart + KPI stack
- hero + summary
- comparison block
- checklist or audit card

The key is that prefabs should represent meaningful authoring value, not just a random list of components.

---

## Prefab Definition Shape

A healthy prefab definition should include concepts such as:

- prefab id
- display name
- category
- widget type or composite definition
- default props
- default style
- accepted slot kinds
- tags or search metadata
- version

This helps the system reason about insertion, compatibility, search, and migration later.

---

## Prefab and Widget Relationship

A prefab is a template.
A widget is the live scene instance.

This distinction must stay explicit because:

- prefabs are reusable definitions
- widgets are mutable scene instances
- compare/revert operates on scene instances
- editing a widget should not silently rewrite prefab definitions
- prefab evolution and widget evolution are related but not identical concerns

---

## Prefab Insertion Flow

A healthy prefab insertion flow looks like this:

1. user selects or focuses a target slot
2. system filters compatible prefabs
3. user picks a prefab
4. prefab is instantiated into widget instance(s)
5. slot acceptance and capacity are validated
6. preview is shown
7. user continues editing, commits, or discards as usual

This flow is far safer and clearer than unrestricted free insertion.

---

## Compatibility Rules

Prefabs should declare compatibility explicitly.

Compatibility may depend on:

- slot kind
- slot capacity
- widget capabilities
- current mode
- composition constraints
- whether the prefab is single-widget or compound

The system must not assume “everything can go everywhere.”

---

## Compound Prefabs

The system may support compound prefabs that create more than one widget or create a local structured grouping.

This can be useful, but must remain disciplined.

Compound prefabs should still:

- target valid slots
- obey slot policy
- remain representable in structure view
- produce understandable scene instances
- avoid smuggling a hidden second composition model into the system

---

## Prefab Library

The Prefab Library is the discovery and insertion surface for prefabs.

A good prefab library should support:

- search
- category browsing
- compatibility filtering
- preview or description
- quick insertion into current selection

The library should feel like a practical composition tool, not a random component catalog.

---

## Prefab Quality

Prefabs should be opinionated enough to be useful.
Bad prefabs create clutter and low-quality output.

A strong prefab should provide:

- good defaults
- visual coherence
- valid structure
- meaningful use case
- clear insertion expectations

The goal is not maximum prefab count.
The goal is meaningful reusable building blocks.

---

## Prefab Evolution

Prefab definitions may evolve over time, but the system should avoid coupling that makes all existing widgets fragile whenever a prefab changes.

The relationship between prefab versioning and existing widget instances should be approached deliberately.
Even if full migration mechanics come later, the system should preserve the conceptual separation now.

---

## Prefab Anti-Patterns

The Prefab System must reject:

- prefabs that are indistinguishable from live widget state
- inserting prefabs into invalid slot contexts
- giant prefab catalogs with no compositional logic
- prefabs used as a substitute for a scene model
- compound prefabs that secretly own broad layout truth
- editing flows that rewrite prefab definitions unintentionally

---

## Summary

The Prefab System exists to make composition fast, reusable, and structured. Prefabs are reusable templates that instantiate widget instances into valid slots. They must be compatibility-aware, well-categorized, and clearly distinct from live widget state. A strong Prefab System is one of the fastest ways to make Live Scene Composer genuinely useful.
EOF

cat > "$DOCS_DIR/17_CUSTOM_WIDGET_SANDBOX.md" <<'EOF'
# 17_CUSTOM_WIDGET_SANDBOX

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Security, Validation
- Scope: Bounded custom widget execution, sandbox model, and safe extension rules

---

## Purpose

This document defines the sandbox model for custom widgets in Live Scene Composer. It exists because custom extension is valuable, but unrestricted code inside a live authoring and runtime-aware system is one of the fastest ways to destroy safety, trust, and maintainability.

Custom widgets matter, but they must be bounded.

---

## Sandbox Model Summary

A custom widget is a widget type that renders inside an approved Slot using a restricted API and an isolated execution model.

The sandbox must ensure that a custom widget:

- renders only within its designated region
- cannot freely mutate the system
- cannot escape into unrestricted global surfaces
- fails locally rather than globally
- uses only approved capabilities
- remains compatible with the mutation and validation model

---

## Why a Sandbox Exists

Without a sandbox, custom widgets become a loophole around the architecture.

A sandbox exists to prevent:

- direct access to runtime internals
- arbitrary filesystem access
- unrestricted DOM or global state access
- silent bridge bypass
- one broken custom widget crashing the whole scene
- accidental or malicious side effects across the broader product

The sandbox is not optional polish.
It is the condition under which custom widgets can exist safely.

---

## Core Sandbox Principles

### 1. Region-bounded rendering

A custom widget must render only within the bounds of its host slot.

### 2. Capability-based access

A custom widget should only be able to do what it has been explicitly allowed to do.

### 3. Local failure isolation

If a custom widget fails, the failure should remain local to that widget or slot region.

### 4. No direct runtime mutation authority

A custom widget must not gain unrestricted write access to runtime-facing state.

### 5. No silent policy bypass

The custom widget path is not allowed to become a loophole around the rest of the system.

---

## Custom Widget Hosting Model

The correct hosting model for custom widgets is:

- an approved Slot
- bounded rendering surface
- restricted execution environment
- approved API surface
- local error boundary
- explicit lifecycle

The key concept is a **Custom Widget Slot** or equivalent policy-approved slot configuration.

---

## What a Custom Widget May Do

A custom widget may be allowed to do bounded things such as:

- render visual content within its region
- read approved scoped data
- request local resize within policy
- apply local visual treatment through approved APIs
- render approved chart or visual primitives through safe wrappers

The exact API may evolve, but it must remain capability-based.

---

## What a Custom Widget Must Not Do

A custom widget must not:

- access the filesystem
- access unrestricted engine internals
- mutate arbitrary runtime state directly
- escape its slot bounds
- mutate unrelated widgets
- mutate the global DOM freely
- call privileged private interfaces by accident or by convenience

These restrictions are the foundation of the sandbox.

---

## Safe API Philosophy

The system should expose safe, purpose-specific APIs rather than raw power.

Examples of safe conceptual APIs may include:

- set local background
- set local text
- render approved chart
- request bounded resize
- read approved scoped data
- request approved effects

The right question is not “how much can a custom widget do?”
The right question is “what specific safe things should a custom widget be able to do well?”

---

## Sandbox Execution Strategy

The concrete technical mechanism may vary, but the execution strategy should aim for:

- isolation
- message-based communication where appropriate
- explicit lifecycle management
- local error boundaries
- capability allowlists
- controlled resource access

Common strategies may involve iframe-like or worker-like isolation patterns depending on product constraints, but the architecture should remain faithful to the principles above.

---

## Custom Widget Identity and Spec

A custom widget should be defined through a spec or manifest that includes concepts such as:

- custom widget id
- name
- api version
- entry point or render definition
- declared capabilities
- sandbox restrictions
- compatibility requirements

The system should know what it is loading before it loads it.

---

## Lifecycle Expectations

A custom widget should have a bounded lifecycle such as:

1. spec resolution
2. policy validation
3. slot compatibility check
4. activation inside sandbox
5. rendering within bounds
6. local event or data interaction through approved API
7. local disposal and cleanup

Custom widgets must not become immortal background processes.

---

## Data Access

Custom widgets may need data, but data access must remain scoped.

Approved data access should prefer:

- read-only scoped data
- approved queries or resolved data contracts
- explicit capability gating

Disallowed data access includes:

- arbitrary global data reads
- hidden access to unrelated product state
- secret backdoors into runtime internals

---

## Mutation Interaction

If custom widgets need to request changes, they should do so through a bounded request surface that remains subject to the broader mutation model.

A custom widget should not receive unrestricted direct mutation authority.
Requests from custom widgets should remain:

- typed
- scoped
- validated
- policy-aware

This keeps custom extension compatible with the overall system architecture.

---

## Failure Isolation

The system must assume that custom widgets will sometimes fail.

Failure handling should aim for:

- local rendering fallback
- visible but contained failure state
- cleanup of widget-specific resources
- preservation of shell and scene stability
- no unrelated state corruption

This is one of the most important reasons to sandbox them at all.

---

## MVP Direction

For an early Composer MVP, custom widgets should remain intentionally constrained.

A reasonable MVP posture is:

- define the concept
- define slot policy support
- define safe spec shape
- define restricted API intent
- delay broad authoring/editor surfaces for custom code until the core system is stable

This prevents custom widgets from dominating the early product before the foundation is sound.

---

## Sandbox Anti-Patterns

The sandbox model must reject:

- arbitrary code execution in the main application context
- unrestricted DOM access
- direct bridge bypass
- custom widgets that can mutate anything because “they’re advanced”
- no-capability, do-anything extension models
- custom widget failures that crash the whole composer

---

## Summary

The Custom Widget Sandbox exists to let Live Scene Composer support extension without sacrificing safety. Custom widgets must render inside bounded slot regions, use restricted APIs, fail locally, and remain subject to capability-based control. The sandbox is what makes custom extension viable instead of reckless.
EOF

cat > "$DOCS_DIR/18_RUNTIME_MUTATION_BRIDGE.md" <<'EOF'
# 18_RUNTIME_MUTATION_BRIDGE

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation, Tooling
- Scope: Mutation governance boundary, validation role, and bridge responsibilities

---

## Purpose

This document defines the role of `runtime-mutation-bridge` in Live Scene Composer. It exists because the bridge is the central safety boundary between authoring intent and runtime-facing write effect.

The bridge is not an optional abstraction. It is the mechanism that makes the Composer governable.

---

## Bridge Summary

`runtime-mutation-bridge` is the controlled write boundary for the Composer.

It should be responsible for:

- receiving typed mutation requests
- validating source, target, and mutation type
- enforcing mode policy
- distinguishing preview from accepted commit paths
- routing approved effects through explicit adapters
- rejecting unsafe or invalid changes clearly

The bridge prevents the Composer from mutating runtime-facing state directly and informally.

---

## Why the Bridge Exists

The bridge exists to solve several problems:

1. direct UI-to-runtime writes are too fragile
2. safety mode policy must be enforceable somewhere explicit
3. mutation validation must be centralized enough to stay real
4. reversibility expectations need a visible boundary
5. future custom and modular extension must not become write bypasses
6. diagnostics and authoring must not share the same mutation habits

Without the bridge, mutation safety becomes a social preference instead of an architectural fact.

---

## Core Bridge Principle

All write-capable Composer mutations that affect runtime-facing state must pass through `runtime-mutation-bridge`.

This principle must remain true in naming, import paths, implementation, tests, and review decisions.

---

## Bridge Responsibilities

The bridge should own:

- typed mutation intake
- source validation
- target validation
- allowlist checks
- safe mode / advanced mode gating
- preview vs commit semantics
- routing to runtime-facing adapters
- structured rejection and error reporting
- optional inverse/revert metadata handling

The bridge should not own:

- the full authoring UI
- the whole scene model
- debug tooling
- every detail of rendering
- all business logic everywhere

It is a governance boundary, not a giant application layer.

---

## Mutation Intake

The bridge should receive typed mutations with explicit metadata such as:

- source
- type
- target
- mode
- scope
- payload
- reversibility expectations

The bridge should not accept vague “update anything” requests as the default pattern.

---

## Source Validation

The bridge should validate who is asking for the change.

Possible approved sources may include:

- live-scene-composer shell
- approved composer modules
- future bounded custom widget request wrappers

This matters because not every caller should have equal authority.

---

## Target Validation

The bridge should validate what the mutation targets.

Potential targets may include:

- scene
- layout node
- slot
- widget
- draft-level operations

The bridge must reject or flag ambiguous targets.
A write without a clear target is an architecture risk.

---

## Mode Policy

The bridge is the place where operational mode becomes enforceable policy.

### Safe Mode

Allows only approved, understandable, bounded changes.

### Advanced Mode

May eventually allow broader operations, but still under typed, explicit, validated rules.

Mode must not remain a cosmetic label in the UI.
It should influence bridge behavior.

---

## Preview vs Commit

The bridge should understand whether a mutation is:

- preview-only
- commit-capable
- draft-reset or discard-related
- accepted-state transition related

This is essential for:

- trust
- compare/revert behavior
- testing
- preventing “everything visible becomes accepted automatically” bugs

---

## Adapter Routing

The bridge should route approved changes toward downstream runtime-facing effects through explicit adapters or equivalent seams.

This matters because:

- runtime specifics should remain bounded
- bridge policy should not depend on every runtime detail
- integration becomes easier to test and evolve

The bridge is therefore both a policy boundary and a routing boundary.

---

## Rejection Behavior

The bridge must reject clearly when a mutation is not allowed.

Rejection behavior should aim for:

- explicit reason
- no hidden fallback path
- no unrelated state corruption
- preserved draft/baseline integrity where possible
- useful diagnostics for validation and tooling

A rejected mutation that still partially writes is worse than an obvious failure.

---

## Early Bridge Command Direction

The early bridge should remain intentionally small.

A reasonable early typed command surface may include:

- scene look update
- layout move
- layout resize
- layout reorder
- widget insert
- widget remove
- widget props update
- widget style update
- draft discard
- draft commit
- selected element reset

This is enough to support a useful early Composer without building an enormous mutation universe too early.

---

## Bridge and Modules

Modules should not bypass the bridge.
Instead, modules should access mutation ability through approved, typed helper seams that eventually route through the bridge.

This keeps modular growth compatible with mutation governance.

---

## Bridge and Custom Widgets

Custom widgets must not receive raw bridge access.
At most, they should be allowed to request bounded actions through safe wrappers that remain subject to bridge validation.

This prevents custom widgets from becoming a hidden authority tier.

---

## Bridge Anti-Patterns

The bridge model must reject:

- direct UI writes that skip the bridge
- giant untyped mutation payloads
- hidden privileged callers
- preview actions that silently become accepted commits
- route-level runtime mutation hacks
- bridge implementations that are policy-free pass-through shells

A bridge that does not enforce policy is only pretending to exist.

---

## Validation Expectations

The bridge should be validated through:

- command contract tests
- source/target validation tests
- mode policy tests
- rejection-path tests
- adapter routing tests
- no-bypass architecture guard assertions where feasible

The bridge must be observable enough that teams can prove it is still doing its job.

---

## Summary

`runtime-mutation-bridge` is the central safety boundary between Live Scene Composer and runtime-facing write effects. It validates, gates, scopes, and routes mutations so the Composer can be powerful without becoming reckless. It is one of the most important pieces of the system and must remain a real enforcement boundary, not a symbolic directory name.
EOF

cat > "$DOCS_DIR/19_DEPENDENCY_POLICY.md" <<'EOF'
# 19_DEPENDENCY_POLICY

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation
- Scope: Allowed and forbidden dependency relationships across the core system boundaries

---

## Purpose

This document defines the dependency policy for Live Scene Composer and its sibling boundaries. It exists because architecture boundaries are only meaningful if dependency direction is explicit and enforceable.

A dependency policy turns “please keep this clean” into something reviewable and testable.

---

## Policy Summary

The system must preserve a small number of high-value top-level boundaries:

- `console-core`
- `runtime-debug-console`
- `live-scene-composer`
- `runtime-mutation-bridge`
- runtime-facing integration areas such as `pitch/*`
- scene-related integration areas such as `scene-studio/*`

The policy defines which of these may depend on which others, and under what conditions.

---

## Dependency Principles

### 1. Shared infrastructure must stay shared

`console-core` is the only shared infrastructure layer and must not absorb product-specific logic.

### 2. Sibling products must not collapse into one another

`runtime-debug-console` and `live-scene-composer` are sibling products and should not import or register each other’s product logic.

### 3. Write-capable authority must remain explicit

`live-scene-composer` must not take direct runtime write shortcuts.
Write-capable flows must go through `runtime-mutation-bridge`.

### 4. Adapters are better than accidental privilege

Where integration is needed, explicit adapter seams are preferred over direct low-level imports.

### 5. Convenience is not a dependency policy

A dependency is not allowed simply because it saves time today.

---

## Top-Level Allowed Dependency Matrix

### console-core

May depend on:

- stable low-level shared UI/utilities
- generic shared internal primitives appropriate to repo conventions

Must not depend on:

- `runtime-debug-console`
- `live-scene-composer`
- product-specific authoring logic
- product-specific debug logic
- `runtime-mutation-bridge` product semantics

Reason:
`console-core` must remain product-neutral shared infrastructure.

---

### runtime-debug-console

May depend on:

- `console-core`
- approved runtime-facing read/diagnostic integration seams
- approved debug-oriented helpers and contracts

Must not depend on:

- `live-scene-composer` product logic
- composer module registration
- composer widget/slot/prefab systems
- composer-specific authoring flows

Reason:
Debug tooling must remain diagnostics-oriented and not become an editor host.

---

### live-scene-composer

May depend on:

- `console-core`
- `runtime-mutation-bridge`
- approved adapter seams into runtime-facing or scene-facing systems
- its own internal scene/layout/slot/widget/module contracts

Must not depend on:

- `runtime-debug-console`
- debug-only product internals
- direct low-level runtime write paths that bypass the bridge
- hidden route-binding shortcuts

Reason:
The Composer is the authoring product and must preserve both sibling separation and mutation discipline.

---

### runtime-mutation-bridge

May depend on:

- typed contracts
- policy helpers
- adapter seams required to route approved changes
- approved validation helpers

Must not depend on:

- broad Composer UI internals
- Runtime Debug Console product logic
- arbitrary runtime internals without explicit adapter or contract purpose
- convenience imports that collapse its role into a generic shared service

Reason:
The bridge is a mutation governance boundary, not a broad application layer.

---

### pitch/* or runtime-facing systems

May depend on:

- their own runtime internals
- approved shared utilities
- explicit adapter contracts where needed

Must not depend on:

- `live-scene-composer` as a required core dependency
- composer UI internals as runtime prerequisites

Reason:
The runtime must not become dependent on the Composer.

---

### scene-studio/* or scene-related systems

May depend on:

- approved scene-related contracts
- approved adapters
- their own product concerns

Must not depend on:

- hidden Composer-only assumptions unless made explicit through stable integration contracts

Reason:
Scene-related systems may integrate with the Composer ecosystem, but should not collapse into it by accidental import drift.

---

## Gray Areas Requiring Care

Some relationships are possible but require deliberate design.

### Composer to runtime observation

The Composer may need read-oriented adapters for bounds, render mapping, or scene runtime state relevant to authoring.
This must be bounded and should not silently become write authority.

### Bridge to runtime adapters

The bridge may need adapter-level knowledge to route approved changes.
These adapters should remain explicit and not evolve into raw unrestricted internals.

### Shared contracts

Some low-level contracts may be shared, but only if they are genuinely shared.
A “shared” contract that exists only because one product imported another’s internals is not healthy sharing.

---

## Forbidden Dependency Patterns

The following are explicitly forbidden:

1. `runtime-debug-console` importing composer product logic
2. `live-scene-composer` importing runtime-debug product logic
3. direct composer-to-runtime write paths outside `runtime-mutation-bridge`
4. `console-core` becoming a container for product-specific concerns
5. duplicate shared-core paths or aliases that reintroduce ambiguity
6. route-binding shortcuts that mount or wire composer through debug paths
7. module code importing unrelated private internals because they happened to be nearby

---

## Dependency Review Questions

When reviewing a dependency change, ask:

1. Which top-level boundary owns this code?
2. Which boundary is it importing from?
3. Is that relationship allowed, adapter-based, or forbidden?
4. Is this read-oriented, write-oriented, or mixed?
5. Is there a more explicit seam that should exist instead?
6. Does this make future wiring easier or more dangerous?

These questions should become habitual.

---

## Enforcement Recommendations

The dependency policy should be reinforced through:

- architecture guard rules
- focused regression tests
- allowed-dependency documentation
- protected-node review expectations
- code review discipline
- module registration checks

Documentation alone is not enough.

---

## Legacy Path Discipline

Legacy shared-core path ambiguity must be blocked.
Only canonical shared infrastructure paths should remain active.

The system should fail verification if obsolete or duplicate shared-core paths are reintroduced.

This matters because path ambiguity creates hidden architecture drift very quickly.

---

## Summary

The dependency policy preserves the integrity of the Live Scene Composer ecosystem by making dependency direction explicit. `console-core` remains the only shared infrastructure layer. `runtime-debug-console` and `live-scene-composer` remain siblings. `runtime-mutation-bridge` remains the explicit write boundary. Runtime-facing systems do not become Composer dependents. These rules are central to long-term architecture health.
EOF

cat > "$DOCS_DIR/20_PROTECTED_NODES.md" <<'EOF'
# 20_PROTECTED_NODES

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Tooling, Validation, Reviewers
- Scope: High-impact files, contracts, and seams that require elevated care

---

## Purpose

This document defines the concept of protected nodes for Live Scene Composer and related boundaries. Protected nodes are high-impact files, contracts, directories, or seams whose changes can create disproportionate architectural, behavioral, or integration risk.

The goal is not to freeze the system.
The goal is to make high-impact change visible and deliberate.

---

## What Is a Protected Node

A protected node is any file, contract, seam, or architectural surface that has unusually high leverage over:

- dependency direction
- mutation authority
- scene model integrity
- module registration
- runtime integration
- product boundary preservation
- system-wide safety or trust

Changes to protected nodes should receive stronger review and validation than ordinary feature work.

---

## Why Protected Nodes Matter

Large systems fail less often because a random button changed and more often because a foundational seam drifted silently.

Protected nodes help the team answer:

- what should not be changed casually
- what requires stronger validation
- what carries large impact cones
- what future workers must treat carefully

They are a governance tool, not a bureaucratic ritual.

---

## Protected Node Categories

The system should treat the following categories as protected by default.

### 1. Shared infrastructure boundaries

Examples:

- `console-core` shell primitives
- `console-core` registry foundations
- `console-core` contracts
- `console-core` lifecycle primitives

Why protected:
These affect both sibling products and can create broad architecture drift quickly.

---

### 2. Mutation governance boundaries

Examples:

- `runtime-mutation-bridge/contract.ts`
- validation rules in bridge logic
- mutation policy helpers
- source/target validation seams

Why protected:
These define who may change what and how, and therefore directly affect safety.

---

### 3. Scene composition contracts

Examples:

- scene model contracts
- slot contracts
- widget contracts
- layout contracts
- prefab contracts

Why protected:
These define the shape of the authoring domain. Drift here affects many modules and workflows.

---

### 4. Registration seams

Examples:

- module registration contracts
- module SDK registration entry points
- shell registration boundaries
- inspector contribution seams

Why protected:
These control how capability enters the system. Weak registration seams create monolithic drift.

---

### 5. Provider and adapter seams

Examples:

- `LiveSceneComposerProvider` location and dependencies
- runtime adapter seams
- scene-related adapter seams
- bridge-to-runtime adapter seams

Why protected:
These are where integration pressure tends to reintroduce bad coupling.

---

### 6. Dependency policy enforcement surfaces

Examples:

- architecture guard rules
- dependency policy artifacts
- path-blocking rules for legacy shared-core aliases

Why protected:
These are the mechanical means by which boundaries stay real.

---

## Core Protected Nodes in This Project

The following should be treated as protected in principle, even if exact filenames evolve:

1. `console-core` contracts and registry foundations
2. `runtime-mutation-bridge` command and policy contracts
3. scene model root contracts
4. layout node contracts
5. slot definition contracts
6. widget instance contracts
7. prefab definition contracts
8. module manifest and module SDK contracts
9. Composer provider seam
10. runtime integration adapter seams
11. dependency policy and architecture guard assertions

These are high-impact seams.

---

## What Makes a Change High Risk

A change should be considered high risk if it:

- alters dependency direction
- widens mutation authority
- changes scene/layout/slot/widget identity or relationship rules
- changes registration mechanics
- changes runtime adapter ownership
- introduces a new path around the bridge
- reintroduces debug/composer coupling
- invalidates compare/revert assumptions
- weakens failure isolation

Even a small diff can be high risk if it touches one of these areas.

---

## Review Expectations for Protected Nodes

Changes touching protected nodes should typically require:

- architectural review
- contract review
- stronger reasoning than “it works locally”
- focused tests
- verification of affected guards
- explicit consideration of blast radius

Protected node changes should be explainable, not merely executable.

---

## Validation Expectations for Protected Nodes

Depending on the node, validation may include:

- typecheck
- focused unit tests
- boundary tests
- architecture guard
- dependency policy checks
- mutation rejection-path tests
- registration seam tests
- adapter behavior tests

The exact set depends on the node, but “no extra validation” should be rare.

---

## Worker Ownership Guidance

Protected node work should skew toward core architecture and validation ownership.

Typical patterns:

- core architecture workers define or modify domain contracts
- tooling workers strengthen enforcement and scaffolding
- validation workers verify blast radius and rule integrity
- feature workers should usually consume protected seams rather than casually redefining them

This does not prohibit changes by feature workers, but it makes review responsibility explicit.

---

## Protected Nodes and Multi-Step Work

When work touches protected nodes, the preferred sequence is:

1. make the intended change explicit
2. explain why the seam must change
3. update related docs or policy if necessary
4. run focused validation
5. inspect impact cone before continuing adjacent feature work

This reduces hidden cascading damage.

---

## Anti-Patterns Around Protected Nodes

The system must reject:

- casual contract changes with no blast-radius review
- “temporary” bypasses around protected seams
- duplicate contract definitions in parallel paths
- rewriting provider or adapter seams as part of unrelated feature work
- widening mutation permissions without explicit review
- changing scene/slot/widget relationships because it simplifies one local implementation

---

## Minimal Protected-Node Review Checklist

Before merging a protected-node change, verify:

1. what boundary this node belongs to
2. why the change is necessary
3. what downstream areas are affected
4. what tests or guards prove safety
5. whether the change weakens policy or boundary clarity
6. whether related docs need updates

If those answers are unclear, the change is not ready.

---

## Summary

Protected nodes are the high-impact seams of the Live Scene Composer ecosystem: shared-core foundations, mutation governance contracts, scene/layout/slot/widget contracts, registration seams, provider seams, adapter seams, and dependency enforcement rules. Treating them explicitly as protected helps the project evolve without repeatedly damaging its foundation.
EOF

echo "[OK] Generated Part 2 docs in: $DOCS_DIR"
echo "[OK] Files created:"
ls -1 "$DOCS_DIR"/11_MODULE_SYSTEM.md \
      "$DOCS_DIR"/12_MODULE_SDK.md \
      "$DOCS_DIR"/13_WIDGET_SYSTEM.md \
      "$DOCS_DIR"/14_SLOT_SYSTEM.md \
      "$DOCS_DIR"/15_LAYOUT_SYSTEM.md \
      "$DOCS_DIR"/16_PREFAB_SYSTEM.md \
      "$DOCS_DIR"/17_CUSTOM_WIDGET_SANDBOX.md \
      "$DOCS_DIR"/18_RUNTIME_MUTATION_BRIDGE.md \
      "$DOCS_DIR"/19_DEPENDENCY_POLICY.md \
      "$DOCS_DIR"/20_PROTECTED_NODES.md