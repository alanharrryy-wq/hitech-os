# Visual Runtime Integration

Round 02 turns the appearance model into an active runtime pipeline.

## What changed

- `GlassWorkspaceRuntime` now owns an `AppearanceCoordinator`.
- `GlassPanelTemplate` can bind directly to that coordinator.
- `FrostedGlassBackdrop` now accepts full appearance snapshots.
- Widget-level shadow application is derived from the same profile/effects snapshot as the stylesheet.

## Intentional limits

This round does not yet migrate every visual role to painter-driven rendering. It focuses on reliable propagation and one-source-of-truth wiring. The heavier rendering refactor lands in Round 03.
