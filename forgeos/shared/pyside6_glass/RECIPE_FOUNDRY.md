# Recipe Foundry

`foundry.py` adds a declarative experience layer on top of `pyside6_glass`.

The goal is not "more widgets".
The goal is **beautiful, varied, workstation-grade recipes** that stay structurally sane.

## Why this exists

Hand-building every screen leads to recurring problems:

- resize behavior turns fragile
- overlay layers start blocking controls
- visual polish gets copied inconsistently
- tabs and detail panes are wired differently in each app
- states (`loading`, `empty`, `error`) get treated as afterthoughts
- "pretty" experiments bypass the shell/runtime contracts

The foundry fixes that by making the *experience* declarative:

- beauty profile
- color story
- motion profile
- region composition
- surface registry
- layout presets
- runtime visibility rules
- quality guardrails

## Design guardrails

The foundry is intentionally biased toward safe composition.

### 1. No absolute positioning as a recipe primitive
Recipes compose through the shell slots and panel/tab primitives. This avoids layer collisions and "button blocked by overlay" regressions.

### 2. Layout presets over manual resize juggling
Recipes define named layout presets such as `focus`, `inspect`, and `wallboard`. Builders switch layouts instead of hardcoding geometry per screen.

### 3. Deferred side panes
Inspector and utility panes can start deferred so heavy content is not created until needed.

### 4. Lazy tabs
Tab groups can defer creation of their content surfaces until the tab becomes active.

### 5. Beauty is first-class data
The schema encodes visual language instead of leaving it implicit in handwritten widget code.

## Top-level recipe sections

- `meta`
- `experience`
- `shell`
- `regions`
- `surfaces`
- `behavior`
- `data`
- `quality`

## Core tokens

### Beauty profiles
- `premium_focus`
- `cinematic_glass`
- `industrial_precision`
- `executive_signal`

### Color stories
- `graphite_cyan`
- `obsidian_violet`
- `frosted_emerald`
- `ember_gold`

### Motion profiles
- `none`
- `subtle`
- `snappy_deluxe`
- `expressive_glass`

## Surface types

- `hero_banner`
- `metric_strip`
- `data_grid`
- `chart`
- `inspector_panel`
- `activity_feed`
- `control_stack`
- `diagnostics`
- `state_gallery`
- `text_block`
- `tab_group`

## Recommended usage pattern

1. Register built-in foundry resources.
2. Start from a built-in recipe that is already close to the target mood.
3. Clone and override the recipe payload.
4. Preview it in the catalog or app adapter.
5. Keep app-specific behavior outside the shared framework.

## Minimal example

```python
from forgeos.shared.pyside6_glass.foundry import (
    build_foundry_preview,
    register_builtin_foundry,
)

register_builtin_foundry()
widget = build_foundry_preview("recipe.ops_console_premium")
```

## Safety principles for beautiful UIs

A "fancy" UI is acceptable only if it still respects:

- shell ownership
- panel/tab states
- runtime visibility policy
- predictable focus paths
- empty/loading/error surfaces
- controllable density
- controllable motion

If a new recipe needs hand-patched geometry or ad-hoc overlay fixes, it should be treated as a design smell and reworked at the recipe/surface level instead.
