# Appearance System Foundation

This document introduces the first dedicated appearance layer for `pyside6_glass`.

## Why this layer exists

The existing framework already has strong building blocks for configuration, theming,
template composition, runtime orchestration, and backdrop rendering. The missing piece
is a **single visual control plane** that can represent appearance choices without
spreading theme math and FX toggles across `template.py`, `runtime.py`, `backdrop.py`,
and widget-specific helpers.

Round 1 adds that control plane without changing runtime behavior yet.

## New modules

- `appearance/profile.py`
  - defines `AppearanceProfile`
  - defines `EffectsProfile`
  - defines `AppearanceSnapshot`
  - defines `AppearanceBundle`
- `appearance/tokens.py`
  - resolves appearance state into concrete numeric tokens
- `appearance/presets.py`
  - central registry for reusable appearance presets
- `appearance/coordinator.py`
  - owns state and emits snapshots
- `theme_resolver.py`
  - bridges existing `GlassTemplateConfig` resolution into the new appearance model

## Design intent

The appearance system is **not** a second theme engine.

It is a stable runtime-facing layer that:

1. consumes existing config and theme decisions,
2. normalizes the visual state into one object,
3. prepares later rounds to wire global updates into template, runtime, backdrop, and FX.

## What is intentionally deferred

Round 1 does not yet:

- mutate `GlassPanelTemplate` behavior,
- inject signals into runtime,
- rewire backdrop painting,
- replace existing shadow helpers,
- migrate widget-local styling.

Those steps are reserved for later rounds to keep the foundation safe and reviewable.
