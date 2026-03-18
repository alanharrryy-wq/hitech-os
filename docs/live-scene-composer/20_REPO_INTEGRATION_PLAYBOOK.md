# 20_REPO_INTEGRATION_PLAYBOOK

## Goal

This playbook explains how to land the Selection Store + InspectorTarget seam into the repo without collapsing boundaries.

## Intended integration direction

### Inside `docs/live-scene-composer`
Install the canonical docs immediately.

### Inside `tools/live-scene-composer/selection-store-inspector-target-wiring-v1`
Stage the pack even if source-root inference is ambiguous.

### Inside the detected composer source root
Only mirror source files when there is exactly one confident candidate or when the operator intentionally opts in.

---

## Safe landing order

1. install docs
2. review staged source pack
3. verify candidate composer src root
4. mirror `selection/` into that root
5. wire tree and inspector first
6. wire canvas next
7. wire mutation-intent helpers after surface synchronization

---

## Proposed folder seam inside composer source

```text
selection/
  contracts.ts
  selection-store.ts
  selection-selectors.ts
  inspector-target.ts
  selection-sync.ts
  mutation-intent.ts
  react-hooks.ts
  surface-adapters.ts
  selection-fixtures.ts
  __tests__/
```

This keeps the seam explicit and avoids mixing selection logic into unrelated panels or runtime adapters.

---

## Review checklist before wiring

- Does the store remain the single canonical selection authority?
- Does inspector derivation avoid reading hidden local identity state?
- Do action payloads include explicit target refs?
- Does canvas clear affordances on stale immediately?
- Does tree active state come from the store rather than a private local flag?
- Do bridge-facing commands remain outside the selection store?

---

## Suggested ownership split

### selection/
- contracts
- store
- selectors
- sync helpers

### inspector/
- renders `InspectorTarget`
- owns presentation only

### structure/
- maps tree node click to typed ref
- derives active highlight from store snapshot

### canvas/
- maps hit test to typed ref
- renders overlays from store snapshot

### mutation-client/
- composes explicit typed target commands
- routes toward bridge-facing APIs

---

## Common bad shortcuts to reject

- inspector reducer quietly becoming the real selected-target owner
- canvas overlay state being treated as authoritative selection
- mutation client reading a global `currentSelectionRef` at call time instead of receiving an explicit target
- stuffing widget props into selection context for convenience

---

## Summary

The repo integration should treat this pack as a seam, not a one-off patch. The point is to make future canvas, tree, inspector, and mutation work easier, safer, and more testable.
