# 11_SELECTION_AND_INSPECTOR_CONTRACT

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Canonical selection semantics and inspector derivation rules for Live Scene Composer

---

## Purpose

This document defines the canonical contracts for **SelectionState** and **InspectorTarget** in Live Scene Composer.

It exists because selection bugs are one of the fastest ways to corrupt authoring behavior:

- canvas and structure tree disagree
- inspector shows the wrong editor
- mutations infer the wrong target
- stale UI focus survives after structure changes
- ephemeral interaction state gets mistaken for domain truth

This contract exists to prevent that class of failure.

Selection is important, but it is not the scene model.
Inspector behavior is important, but it is not allowed to invent its own truth.
Both must remain explicit, bounded, and testable.

---

## Core Principles

### Principle 1: Selection is explicit state

Selection must exist as a first-class, explicit model.
It must not be inferred ad hoc from DOM nodes, React-local state, or whichever panel was clicked most recently.

### Principle 2: Selection is not domain truth

Selection identifies the current authoring focus.
It does not own scene composition, widget props, layout structure, slot policy, draft state, or accepted state.

### Principle 3: InspectorTarget is derived, not independently authored

Selection answers:

- what is currently selected

InspectorTarget answers:

- what editing context should be presented for the current selection

InspectorTarget must be derived from SelectionState plus bounded capability/context lookups.
It must not become a second competing source of truth.

### Principle 4: Mutations must not depend on implicit selection

Selection may help the user choose a target.
It may help UI compose mutation intent.
But no write-capable mutation may rely on “whatever is selected right now” as its only target definition.

Mutation targets must remain explicit and typed.

### Principle 5: Selection remains ephemeral but high-value

Selection is interaction state, not persisted composition truth.
However, it is high-value ephemeral state and must be treated with architectural discipline.

---

# SelectionState

## Definition

SelectionState is the canonical representation of the user’s current authoring focus.

It identifies a single currently active entity, or the absence of one, in a way that is:

- typed
- explicit
- source-aware
- safe under staleness
- usable across canvas, structure tree, and inspector

---

## Responsibilities

SelectionState is responsible for:

- identifying the currently focused authoring entity
- preserving the entity kind explicitly
- recording which surface initiated the current selection change
- allowing surfaces to synchronize on one shared truth
- supporting clean handoff to InspectorTarget derivation
- supporting safe invalidation when the selected entity disappears or becomes stale

SelectionState is **not** responsible for:

- holding widget props
- holding scene/layout/slot domain truth
- storing draft or baseline content
- deciding commit semantics
- applying mutations
- storing hover or drag-in-progress interaction details

---

## Allowed Selection Kinds

SelectionState may target exactly one of the canonical authoring entity kinds:

- `scene`
- `layout-node`
- `slot`
- `widget`

These kinds are aligned with the domain model and must remain explicit.

SelectionState must not target vague anonymous concepts such as:

- `panel`
- `element`
- `thing`
- `current node`
- raw DOM element references

If a surface cannot map its click/focus target into one of the allowed entity kinds, it does not yet have a valid selection target.

---

## Canonical Shape

SelectionState must contain the following concepts:

### 1. `status`

Allowed values:

- `none`
- `active`
- `stale`

Meaning:

- `none`: nothing is currently selected
- `active`: the selection refers to a currently valid entity
- `stale`: the selection used to be valid but can no longer be safely resolved

### 2. `kind`

Allowed values:

- `scene`
- `layout-node`
- `slot`
- `widget`

Required when `status = active` or `status = stale`.

### 3. `ref`

A typed entity reference.

This must be a stable identity reference appropriate to the entity kind.
It must not be a DOM node, component instance, or visual handle id.

Examples of acceptable conceptual forms:

- scene id
- layout node id
- slot id
- widget id

### 4. `origin`

The surface that most recently authored the selection change.

Allowed values:

- `canvas`
- `structure-tree`
- `inspector`
- `system`

Purpose:

- diagnostics
- reconciliation understanding
- UX nuance where needed

Origin must not change the meaning of the selection itself.
A widget selected from canvas and the same widget selected from structure tree must resolve to the same canonical selection.

### 5. `revision`

A lightweight revision marker or comparable freshness token tied to the authoring model snapshot used to resolve the selection.

Purpose:

- stale detection
- invalidation after structure refresh
- validation and debugging

### 6. `context` (minimal, optional)

Minimal metadata useful for UX continuity only.

Examples:

- breadcrumb hints
- parent slot ref hint
- last visible path hint

This field is optional and must never become a backdoor for storing domain truth.

---

## Invariants

The following invariants must always hold:

### Invariant S1

If `status = none`, then `kind` and `ref` must be absent.

### Invariant S2

If `status = active`, then `kind`, `ref`, `origin`, and `revision` must be present.

### Invariant S3

If `status = stale`, then `kind` and the last known `ref` may remain present for diagnostics and recovery behavior, but no editing surface may treat the target as fully valid.

### Invariant S4

SelectionState may represent **at most one active selected entity**.
Multi-select is out of scope for this contract.

### Invariant S5

SelectionState must not contain mutable domain payloads such as:

- widget props
- slot policy objects
- full layout node data
- draft scene content

### Invariant S6

A change in `origin` alone must not alter the semantic identity of the selected target.

### Invariant S7

SelectionState must be valid across all major authoring surfaces.
No surface may maintain a hidden second canonical selection.

---

## Valid Transitions

Exactly these transition categories are valid:

### Transition T1: `none -> active`

Occurs when the user or system selects a valid entity.

Examples:

- clicking a widget on canvas
- selecting a slot from structure tree
- system selecting the scene root on initial load

Expected result:

- SelectionState becomes `active`
- `kind`, `ref`, `origin`, and `revision` are set
- other surfaces reconcile to the same target

---

### Transition T2: `active -> active` with different target

Occurs when the current valid selection is replaced by another valid selection.

Examples:

- switching from widget to slot
- switching from one layout node to another
- selecting the scene root after editing a widget

Expected result:

- previous selection is replaced cleanly
- no residual inspector state from the prior target survives
- overlays/handles update to the new target only

---

### Transition T3: `active -> none`

Occurs when selection is intentionally cleared.

Examples:

- clicking empty safe area
- explicit “clear selection” action
- surface reset after scene unload

Expected result:

- SelectionState becomes `none`
- inspector falls back to safe empty or shell state
- target-specific overlays disappear

---

### Transition T4: `active -> stale`

Occurs when the previously selected entity can no longer be resolved safely.

Examples:

- widget removed
- layout node reordered out of existence
- slot destroyed by structure change
- draft refresh invalidates prior ref

Expected result:

- SelectionState becomes `stale`
- the system must not silently retarget to a different entity
- inspector must stop offering unsafe editing for the missing target
- canvas and structure surfaces must clear target-specific controls

---

### Transition T5: `stale -> active` or `stale -> none`

Occurs after explicit recovery.

Examples:

- stale reference is remapped through a valid recovery rule
- system chooses safe fallback to scene
- user selects a new entity manually
- refresh determines no valid recovery exists

Expected result:

- recovery must be explicit and observable
- stale must not quietly mutate into an unrelated target with no signal

---

## Forbidden Transitions

The following are forbidden:

- implicit retargeting from stale widget to “nearest surviving widget”
- converting hover to selection without an explicit selection event
- letting drag handles become the canonical selected target
- restoring an old selection after model refresh without validating revision/ref
- allowing inspector-local state to override SelectionState

---

## Surface Responsibilities

### Canvas

Canvas may:

- request selection changes
- render active selection overlays
- clear overlays when selection becomes `none` or `stale`

Canvas must not:

- own the canonical selection separately
- infer authoritative selection from highlighted DOM alone
- store domain truth inside selection metadata

### Structure Tree

Structure Tree may:

- request selection changes by typed entity ref
- reflect canonical selection state visually

Structure Tree must not:

- preserve a separate hidden active node that disagrees with SelectionState
- force inspector behavior outside canonical derivation

### Inspector

Inspector may:

- react to SelectionState
- derive and render InspectorTarget
- request reselection only through explicit selection actions

Inspector must not:

- invent its own target identity
- continue editing a stale target as if valid
- mutate selection semantics locally

### System

The system may:

- initialize selection
- clear invalid selection on scene unload
- mark selection stale on authoritative model changes

The system must not:

- silently choose a different entity as replacement without an explicit recovery rule

---

# InspectorTarget

## Definition

InspectorTarget is the derived editorial interpretation of the current SelectionState.

It answers:

- what editing context should be shown
- what property groups are relevant
- what actions are valid
- what target framing the inspector should present

InspectorTarget is not authored directly as primary truth.
It is derived from:

- SelectionState
- entity kind
- bounded capability/context lookup
- operational mode if relevant

---

## Responsibilities

InspectorTarget is responsible for:

- choosing the correct inspector surface for the selected entity kind
- defining which property groups are visible
- defining which actions are enabled, disabled, or hidden
- providing editorial framing such as title, subtitle, breadcrumb, and capability grouping

InspectorTarget is not responsible for:

- identifying the selected entity independently of SelectionState
- mutating scene/layout/slot/widget data by itself
- replacing mutation policy
- deciding draft/commit semantics alone

---

## Canonical Shape

InspectorTarget must contain the following concepts:

### 1. `status`

Allowed values:

- `empty`
- `ready`
- `unavailable`

Meaning:

- `empty`: nothing selected
- `ready`: a valid target can be edited or inspected
- `unavailable`: a selection exists but cannot currently be edited safely

### 2. `selectionRef`

A direct derivation pointer back to the current SelectionState target.

Purpose:

- traceability
- diagnostics
- proof that inspector is derived from canonical selection

### 3. `editorKind`

Allowed values:

- `scene-editor`
- `layout-node-editor`
- `slot-editor`
- `widget-editor`
- `empty-editor`
- `unavailable-editor`

This is the inspector’s high-level UI mode.

### 4. `propertyGroups`

A bounded list of property group descriptors relevant to the selected target.

Examples:

- scene appearance
- layout structure
- slot policy
- widget content
- widget style

These groups must remain derived from target kind and capability rules, not arbitrary UI convenience.

### 5. `actions`

A bounded list of editor actions relevant to the target.

Examples:

- reset selected element
- remove widget
- move widget
- change slot policy
- adjust scene look

Actions shown here must still route through proper governed mutation flow where applicable.

### 6. `capabilities`

A derived capability summary.

Examples:

- editable
- removable
- resettable
- reorderable
- style-editable
- props-editable

Capabilities are UI-facing derivations.
They do not replace mutation allowlists or bridge validation.

### 7. `presentation`

Optional UI framing metadata such as:

- title
- subtitle
- breadcrumb
- warning badges
- stale/unavailable messaging

This is presentation context only.

---

## Invariants

The following invariants must always hold:

### Invariant I1

If SelectionState is `none`, InspectorTarget must be `empty`.

### Invariant I2

If SelectionState is `stale`, InspectorTarget must be `unavailable` unless an explicit validated recovery rule has already produced a new active selection.

### Invariant I3

InspectorTarget editor kind must match the selected entity kind.

Examples:

- `scene -> scene-editor`
- `layout-node -> layout-node-editor`
- `slot -> slot-editor`
- `widget -> widget-editor`

### Invariant I4

InspectorTarget must never expose property groups for a different entity kind than the current active selection.

### Invariant I5

Capabilities shown in InspectorTarget must be narrower than or equal to actual allowed behavior.
The inspector must never imply an action is safely available when mutation governance may reject it.

### Invariant I6

InspectorTarget must be derivable deterministically from the same SelectionState and the same capability context.

---

## Derivation Rules

### Rule D1

SelectionState `none` derives:

- `status = empty`
- `editorKind = empty-editor`
- no property groups
- no target actions

### Rule D2

SelectionState `active + scene` derives:

- `status = ready`
- `editorKind = scene-editor`
- scene-relevant property groups only

### Rule D3

SelectionState `active + layout-node` derives:

- `status = ready`
- `editorKind = layout-node-editor`
- layout-structure and layout-style relevant groups only

### Rule D4

SelectionState `active + slot` derives:

- `status = ready`
- `editorKind = slot-editor`
- slot policy and host-region relevant groups only

### Rule D5

SelectionState `active + widget` derives:

- `status = ready`
- `editorKind = widget-editor`
- widget props, style, and content relevant groups only

### Rule D6

SelectionState `stale` derives:

- `status = unavailable`
- `editorKind = unavailable-editor`
- no unsafe editing actions
- explicit message that the prior selection is no longer valid

---

## Capability Rules

InspectorTarget capabilities must be derived from bounded rules such as:

- entity kind
- current mode
- target existence
- target lock, visibility, and editability flags where applicable
- policy constraints already exposed by stable contracts

Capabilities must not be derived from:

- DOM affordances
- whether a button happens to be visible
- debug-only runtime privilege
- optimistic guesses

---

## Failure Behavior

When derivation fails or target context cannot be resolved safely:

- InspectorTarget must fall back to `unavailable`, not fake readiness
- the inspector must not continue editing cached data from an old target
- selection may remain `stale` until explicit recovery or replacement occurs
- the broader composer shell must remain stable

---

## Validation Expectations

The system should validate this contract with focused checks such as:

- same entity selected from canvas and structure tree yields same SelectionState
- same SelectionState always derives same InspectorTarget
- stale selection disables unsafe inspector actions
- clearing selection removes editor-specific overlays and controls
- inspector never displays widget controls for slot selection
- mutation requests still require explicit target even when selection exists

---

## Anti-Patterns

The following are architecture failures:

- storing canonical selection only inside a React panel state
- using DOM selection as domain identity
- letting inspector invent its own target
- letting stale targets remain editable
- using selection as the only mutation target source
- hiding different selection truths in canvas and structure tree
- packing domain payloads into SelectionState because it was convenient

---

## Summary

SelectionState is the canonical, typed, single-source representation of current authoring focus.
InspectorTarget is the deterministic editorial interpretation derived from that selection.

They must remain:

- separate
- explicit
- bounded
- testable
- aligned with the domain model
- compatible with governed mutation flow

If maintained seriously, this contract gives the Composer a clean nervous system:
selection tells the product what is focused,
inspector tells the product how that focus should be edited,
and neither one is allowed to impersonate domain truth or mutation authority.
