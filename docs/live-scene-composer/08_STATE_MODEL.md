# 08_STATE_MODEL

## Document Status

- Status: Canonical
- Audience: Architecture, Engineering, Validation
- Scope: State categories, ownership, transitions, and trust model

---

## Purpose

This document defines how state should be understood and categorized in Live Scene Composer. It exists because state confusion is one of the fastest ways to create invalid behavior, broken preview semantics, accidental persistence bugs, and impossible-to-debug authoring workflows.

The goal is to make state explicit, layered, and testable.

---

## State Model Summary

The system should reason about state in at least five categories:

1. **Baseline State**
2. **Draft State**
3. **Preview State**
4. **Ephemeral UI State**
5. **Runtime-Observed State**

These categories are related, but not interchangeable.

---

## Baseline State

### Definition

Baseline State is the accepted reference state against which current authoring changes are evaluated.

### Responsibilities

Baseline State exists to:

- preserve a trusted reference point
- support compare and diff
- support discard semantics
- reduce fear during live authoring
- define what “current accepted state” means for the user

### Characteristics

- stable until intentionally replaced
- not casually mutated by local UI behavior
- suitable for comparison and recovery workflows

### Examples

- last accepted scene composition
- last approved set of visual styles
- current accepted widget arrangement

---

## Draft State

### Definition

Draft State is the mutable working state where authoring changes accumulate before acceptance.

### Responsibilities

Draft State exists to:

- hold current in-progress edits
- allow experimentation
- isolate unaccepted changes from baseline
- support preview and compare workflows

### Characteristics

- mutable
- user-driven
- reversible
- may be promoted to accepted state later
- should remain coherent even after multiple local edits

### Examples

- moved widget not yet committed
- typography changes under review
- inserted prefab not yet accepted into baseline state

---

## Preview State

### Definition

Preview State is the rendered presentation of a Draft or pending change within the live editing experience.

### Why it matters

The user sees the preview, not abstract state categories.
If preview semantics are wrong, trust collapses.

### Responsibilities

Preview State exists to:

- show what the user is about to accept
- provide immediate visual feedback
- allow compare with baseline
- support a safe iterative editing loop

### Characteristics

- visible
- reactive
- sometimes transient
- should not be confused with accepted persistence

### Important rule

A previewed change is not necessarily a committed or accepted change.

---

## Ephemeral UI State

### Definition

Ephemeral UI State is short-lived interaction state used by the authoring experience.

### Examples

- current selection
- hovered node
- drag in progress
- resize handles
- focused inspector section
- expanded structure tree nodes
- guide visibility
- snap candidate state

### Characteristics

- local
- short-lived
- frequently changing
- not itself part of composition truth

### Important rule

Ephemeral UI State must not become the accidental source of domain truth.

---

## Runtime-Observed State

### Definition

Runtime-Observed State is runtime-derived information that the composer reads in order to understand or align with the actual rendered system.

### Examples

- visual bounds
- runtime node identifiers
- actual render tree relationships relevant to inspection
- diagnostics useful for alignment
- measured dimensions

### Purpose

This state helps the composer align with the real runtime but does not automatically become the authoring truth model.

### Important rule

Observed runtime state is informative, but not an excuse for uncontrolled runtime writes.

---

## State Ownership Summary

### Scene model owns

- baseline composition data
- draft composition data
- structural relationships among scene, layout, slots, widgets
- accepted scene metadata

### Interaction systems own

- selection
- hover state
- local manipulation state
- transient view/UI interaction states

### Runtime adapter layers own

- mapping between authoring concepts and runtime-observed facts
- runtime node/bounds lookups
- translation between render world and authoring world

### Mutation bridge owns

- validation and routing decisions about write-capable changes
- it does not own all state, but it governs sensitive transitions

---

## State Transition Model

A healthy editing flow should follow a disciplined progression:

1. user selects a target
2. user performs an action
3. action generates mutation intent
4. mutation is validated
5. draft state is updated
6. preview reflects draft
7. user compares or continues editing
8. user commits or discards
9. baseline is updated only after accepted commit semantics

This path should be legible in code and behavior.

---

## Commit Semantics

### Commit

Commit means the system now treats a previously in-progress change as accepted state for the relevant workflow.

### Important note

Commit does not necessarily mean “persisted everywhere forever” in the broadest platform sense. But it must mean that from the composer’s perspective, the change has passed from unaccepted draft to accepted state.

---

## Revert Semantics

### Revert

Revert means returning some scope of state to a previously accepted or previously captured state.

Possible scopes may include:

- selected entity reset
- current module reset
- whole draft discard
- snapshot restore

These scopes should remain explicit.

---

## Reset Semantics

Reset should be narrower than full discard when possible.

Examples:

- reset selected widget style
- reset a slot’s local visual treatment
- reset layout node adjustments
- reset current module contribution

The system should distinguish reset from full draft discard.

---

## State Invariants

The following invariants should hold:

1. Baseline and Draft are not silently the same thing.
2. Preview reflects Draft or pending state, not some hidden mix of unrelated data.
3. Ephemeral UI State does not overwrite domain truth directly.
4. Write-capable changes do not bypass validation.
5. Selection state does not define ownership or persistence.
6. Runtime-observed facts may inform authoring but do not replace the scene model.
7. Revert paths must remain coherent.

---

## Common State Failures to Avoid

- writing directly from UI controls into runtime-facing state with no draft layer
- storing composition truth inside React-local component state only
- merging selection and domain state until they cannot be separated
- pretending preview equals commit
- reusing debug runtime state as authoring truth
- losing the baseline, then pretending compare/revert still exists
- allowing mutation without target scope clarity

---

## Summary

The Live Scene Composer state model must distinguish Baseline State, Draft State, Preview State, Ephemeral UI State, and Runtime-Observed State. State clarity is not optional: it is what makes compare, revert, trust, and controlled authoring possible. The system should be built so that state categories remain understandable in code, behavior, and testing.
