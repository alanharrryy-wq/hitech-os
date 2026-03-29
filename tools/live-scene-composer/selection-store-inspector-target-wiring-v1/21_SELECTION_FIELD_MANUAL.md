# 21_SELECTION_FIELD_MANUAL

## This is the operator's version

If the product feels weird around selection, the usual culprits are boring and brutal:

1. two surfaces think they own the selected target
2. inspector is editing stale assumptions
3. actions are firing against implicit global state
4. revision changes are not turning into explicit stale state

This manual gives the team a practical checklist.

---

## Smell: canvas and inspector disagree

### Usually means
- store subscription gap
- inspector target derived from stale local props
- overlay state not driven from canonical snapshot

### Check
- inspect the last store transition
- log current `selectionRefToKey()` in canvas and inspector
- verify only one committed selection snapshot exists

---

## Smell: user deletes a widget and inspector still edits it

### Usually means
- stale transition not emitted
- inspector target cached too aggressively
- widget editor not resetting on target identity change

### Check
- confirm `active(widget) -> stale(widget)` happened
- ensure unavailable editor path exists
- ensure actions list is empty under stale state

---

## Smell: tree silently jumps to a sibling

### Usually means
- a local fallback tried to hide the stale problem
- active-node state is not fully derived from the store

### Check
- look for nearest-sibling or nearest-visible fallback code
- require explicit recovery reason if a new target is chosen

---

## Smell: mutation changed the wrong target

### Usually means
- payload built from hidden global current selection at execution time
- action rendered under one target and executed under another

### Check
- inspect the mutation payload
- require target `kind` and ref id in the command itself
- compare payload target against the selection snapshot used to render the button

---

## Smell: stale target is invisible to logs

### Usually means
- transition metadata too weak
- version / reason / origin not recorded

### Check
- store version increments
- transition reason captured
- updated revision captured
- recovery event also visible

---

## Daily sanity checks

- `none` means no kind and no ref
- `stale` means no editable target actions
- `InspectorTarget` is never independently authored
- hover is never selection
- handles are never the selected target
- selection origin is diagnostic only

---

## Summary

Selection bugs are less magical when the contracts are explicit. Use the store, honor stale state, derive the inspector, and force explicit mutation targets.
