# Package Contents

## High-value outcomes

1. Selection becomes a named, typed store instead of scattered local UI state.
2. InspectorTarget becomes deterministic derivation instead of a parallel truth source.
3. Canvas, structure tree, and inspector can synchronize on one canonical selection snapshot.
4. Staleness and recovery become explicit behaviors instead of accidental UI leftovers.
5. Mutation composition gains a clear boundary between **selection-assisted UX** and **explicit typed targeting**.

## What this package does not do

- It does not bypass `runtime-mutation-bridge`.
- It does not claim selection is persisted domain truth.
- It does not hardcode one repo layout as the only possible source root.
- It does not force direct runtime writes from canvas or inspector.
- It does not introduce multi-select.

## Recommended install result

### Always install

- docs under `docs/live-scene-composer`
- source bundle staging under `tools/live-scene-composer/selection-store-inspector-target-wiring-v1`

### Auto-install when confidently detected

- `selection/` source files into the composer source root

## Suggested next phase after this pack

Once this pack is in place, the most natural next implementation wave is:

1. wire structure tree to the shared store
2. wire canvas hit testing to the shared store
3. derive InspectorTarget from the store
4. compose mutation intents with explicit target refs
5. add bridge-facing mutation client wrappers
