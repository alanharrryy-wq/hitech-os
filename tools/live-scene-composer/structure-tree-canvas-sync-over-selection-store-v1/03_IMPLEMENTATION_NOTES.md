
# Implementation Notes

## Key idea

Structure Tree and Canvas should not each own their own truth.
They should be two projections of the same authoring focus and scene structure.

## What this pack intentionally does not do

- it does not perform runtime writes
- it does not replace the Selection Store pack
- it does not pretend overlays are domain state
- it does not flatten scene, layout, slot, and widget into anonymous nodes

## Main seam

The heart of the pack is the `surface-coordinator.ts` seam.
It receives typed surface events, updates or queries selection state, derives per-surface instructions, and emits diagnostics that make drift debuggable.

## Why this is safe

Because the source seam is split into projection, coordination, navigation, and intent-building layers, it becomes much harder for Canvas-only hacks or Structure-only hacks to silently become canonical behavior.
