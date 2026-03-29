# 17_SELECTION_TEST_PLAN

## Document Status

- Status: Working Plan
- Audience: QA, Engineering, Validation
- Scope: Test coverage expectations for selection store and inspector target behavior

---

## Contract-level checks

- selecting `scene`, `layout-node`, `slot`, and `widget` yields valid active snapshots
- `none` strips kind/ref
- `stale` preserves last known kind/ref but blocks editing
- invalid inputs fail fast instead of mutating the store silently

## Store behavior checks

- subscribers observe ordered transitions
- clearing selection emits `active -> none` or `stale -> none`
- revision change can mark current selection stale
- explicit recovery can move `stale -> active`
- origin metadata changes do not redefine target identity

## Inspector derivation checks

- `none -> empty-editor`
- `stale -> unavailable-editor`
- `scene -> scene-editor`
- `layout-node -> layout-node-editor`
- `slot -> slot-editor`
- `widget -> widget-editor`
- property groups never leak across entity kinds

## Surface sync checks

- canvas clears overlays on `none` and `stale`
- structure tree reflects active target only from the store
- inspector target resets when target identity changes

## Mutation boundary checks

- inspector actions compose explicit typed targets
- selection changes between render and action execution do not retarget the mutation silently

---

## Failure signals worth treating seriously

- wrong editor kind for the selected entity
- stale widget still showing editable content controls
- structure tree and canvas highlighting different entities
- write-capable action missing an explicit target payload
