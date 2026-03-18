# 11_SELECTION_STORE_CONTRACT

## Document Status

- Status: Proposed Canonical
- Audience: Architecture, Engineering, Validation
- Scope: Canonical store contract for selection state in Live Scene Composer

---

## Purpose

This document defines the **Selection Store** that operationalizes the existing selection contract.

The prior contract established what SelectionState means.
This document defines how that state should be owned, updated, observed, invalidated, and synchronized across authoring surfaces.

The Selection Store exists so the product does not fall back into these failure modes:

- canvas and structure tree each owning their own secret selection
- inspector holding stale local target assumptions after a structure refresh
- mutation composition quietly depending on the last clicked thing rather than an explicit target
- revision changes invalidating the current target without any observable stale state
- ad hoc local fixes introducing a second canonical selection source

---

## Store Role

The Selection Store is the single in-memory authority for current authoring focus.

It owns:

- the current `SelectionState`
- selection change events
- stale marking and recovery transitions
- subscriber notification
- origin-aware diagnostics metadata

It does **not** own:

- scene composition data
- widget props
- draft or baseline payloads
- runtime-observed bounds
- hover or drag state
- mutation execution

---

## Core Responsibilities

The Selection Store must:

1. expose the current snapshot synchronously
2. support subscription for canvas, structure tree, and inspector
3. accept explicit selection requests by typed ref
4. support clear, stale, and recover transitions
5. preserve revision tokens for stale detection
6. emit deterministic transition metadata for debugging and tests

---

## Canonical Operations

### `select(ref, kind, origin, revision, context?)`

Creates or replaces an active selection.

### `clear(reason, origin)`

Resolves the store to `none`.

### `markStale(reason, revision?)`

Preserves the last known target but marks it unsafe for editing.

### `recover(nextSelection, reason)`

Allows explicit recovery from stale to a new active selection.

### `replaceRevision(nextRevision, policy)`

Reconciles the current selection against a newer model revision.

### `getSnapshot()`

Returns the canonical immutable snapshot.

### `subscribe(listener)`

Allows surfaces to react to changes without owning a second store.

---

## Snapshot Model

A healthy snapshot should include:

- `selection`: current `SelectionState`
- `version`: monotonically increasing store-local event version
- `lastTransition`: transition metadata
- `updatedAtUtc`: deterministic event timestamp or injected clock value

This makes debugging easier without inflating selection into domain truth.

---

## Transition Requirements

Every transition must record:

- previous status
- next status
- transition kind
- reason
- origin
- store version

That data is useful for:

- integration debugging
- UI reconciliation bugs
- flaky surface synchronization diagnosis
- future audit-friendly tooling

---

## Store Invariants

### SS1

There is exactly one canonical active selection snapshot at a time.

### SS2

Subscribers must observe transitions in the same order they were committed.

### SS3

Store notifications must never expose mutable internal references.

### SS4

A stale selection may preserve the last known ref for diagnostics, but surfaces must not treat it as editable truth.

### SS5

A revision replacement policy must never silently retarget to a different entity unless an explicit recovery path is applied.

### SS6

Selection origin is diagnostic metadata, not semantic identity.

---

## Allowed Store Inputs

The store may accept inputs from:

- canvas hit selection
- structure tree selection
- inspector-initiated reselection actions
- system initialization
- system invalidation / recovery rules

The store must not accept opaque anonymous inputs such as raw DOM nodes or component instances.

---

## Integration Guidance

### Canvas

Canvas should subscribe and render overlays from the store snapshot.
Canvas may request `select()` and `clear()`.
Canvas must not keep a hidden authoritative selected DOM node.

### Structure Tree

Structure Tree should subscribe and map the current selection ref to the visible node state.
It may request `select()` when the user chooses a tree node.
It must not preserve a private active node that diverges from the store.

### Inspector

Inspector should subscribe and derive `InspectorTarget` from the current snapshot.
Inspector-local tab or section state may exist, but it must reset safely when the underlying selected target changes.

---

## Failure Modes To Reject

- canvas selection surviving after the selected entity was removed
- structure tree auto-selecting a sibling with no explicit recovery reason
- inspector continuing to edit the last valid widget after selection is stale
- a drag handle becoming the canonical target
- revision refresh mutating selection behind the user’s back

---

## Summary

The Selection Store is the canonical runtime owner of current authoring focus inside Live Scene Composer. It exists to keep canvas, structure tree, and inspector synchronized on one explicit truth without elevating selection into domain ownership or mutation authority.
