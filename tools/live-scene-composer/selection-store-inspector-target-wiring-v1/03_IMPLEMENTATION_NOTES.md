# Implementation Notes

## Guiding architecture truths

- `SelectionState` is ephemeral interaction state, not domain truth.
- `InspectorTarget` is derived from selection plus bounded capability context.
- the canonical domain model remains `Scene -> Layout -> Slots -> Widgets`.
- the inspector may show actions, but mutation targets must remain explicit and typed.
- runtime-facing writes still route through `runtime-mutation-bridge`.

## Why a store exists

Without a store, selection tends to fracture across:

- canvas highlight state
- structure tree expanded/active nodes
- inspector panel local state
- ad hoc selection inferred from DOM events

That fracture usually creates stale edits, wrong target affordances, and hidden coupling.

## Why capability context is separate

`InspectorTarget` should not need the whole scene model or runtime internals.
It only needs bounded capability inputs that answer questions like:

- is this entity editable?
- is it removable?
- which property groups are relevant?
- are we in safe mode or advanced mode?
- are there current warnings or blockers?

That keeps derivation deterministic and easier to test.
