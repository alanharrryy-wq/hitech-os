# 16_SELECTION_IMPLEMENTATION_SEQUENCE

## Document Status

- Status: Working Plan
- Audience: Engineering, Validation
- Scope: Recommended implementation order for the Selection Store + InspectorTarget wiring pack

---

## Recommended sequence

### Phase 1: Contracts and tests

- add the selection contracts
- add the store implementation
- add derivation logic for inspector target
- add store and derivation tests

### Phase 2: Structure Tree integration

- subscribe the tree to the shared store
- emit `select()` from typed tree node refs
- remove any hidden local authoritative active-node state

### Phase 3: Inspector integration

- derive `InspectorTarget` from the store snapshot
- reset target-local section state on target identity changes
- ensure stale selection becomes `unavailable-editor`

### Phase 4: Canvas integration

- wire typed hit selection into `select()`
- drive overlays from the shared snapshot
- clear affordances immediately on `none` or `stale`

### Phase 5: Mutation intent composition

- convert inspector and canvas actions to explicit typed targets
- remove any write path that depends on “whatever is selected now” at execution time

### Phase 6: Bridge-facing client wrappers

- add typed mutation client helpers that accept explicit targets
- keep write-capable flows aligned with `runtime-mutation-bridge`

---

## Why this order wins

This order optimizes for:

- deterministic contracts first
- low coupling early wins
- surface synchronization before mutation expansion
- visible progress without violating architecture boundaries

---

## Validation checkpoints

After each phase, validate:

1. one canonical selection snapshot exists
2. stale selection is observable and safe
3. inspector target is deterministic
4. no write action executes against an implicit target
