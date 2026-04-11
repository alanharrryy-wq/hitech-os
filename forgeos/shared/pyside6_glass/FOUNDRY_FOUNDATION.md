# Foundry Foundation Core

`foundry_foundation.py` is the platform base layer for premium recipe-driven UI composition on top of `pyside6_glass`.

This is not a theme pack.
This is not a loose pile of widgets.
This is not another starter template that turns feral after the third resize.

The purpose of the foundation layer is to make beautiful interfaces *systemic*.

## What this layer establishes

- a declarative premium recipe schema
- registries for beauty profiles, color stories, motion profiles, layout packs and shell packs
- governed surface hosts
- a safe page host for single-active-page composition
- layout contracts that keep minimums and ratios explicit
- a runtime state object so screens are not driven by random booleans
- built-in recipe catalog entries
- preset and theme registration helpers

## Why it matters

When UI work stays ad hoc, the same failures keep showing up:

- one screen uses a nice density rhythm, another jams everything together
- tabs are managed one way in one app and another way in the next
- loading/empty/error are treated like last-minute emergencies
- metrics walls get built as custom snowflakes
- inspectors have no structural contract
- shell ownership gets bypassed for one-off experiments
- gorgeous experiments slowly turn into geometry debt

The foundation layer makes those concerns data.

## Core design stance

### Beauty is part of the contract
A recipe declares:
- beauty profile
- color story
- motion profile
- layout pack
- shell pack

That means “premium” is not a paint job at the end.
It is a structured choice upstream.

### Surfaces instead of anonymous widgets
A recipe composes named surfaces such as:
- hero banner
- data grid
- chart
- inspector panel
- activity feed
- tab group
- command palette

That makes composition legible, testable and easier to preview.

### Layout is explicit
A recipe can say:
- main minimum width
- side minimum width
- preferred ratio
- stretch policy
- deferred side pane
- named layout presets

This keeps resize behavior from turning into folklore.

### States are first-class
Every serious surface should know what to do when it is:
- loading
- empty
- error
- deferred
- ready

This avoids the classic “we made the happy path beautiful and the rest looks like a stack trace”.

## Top-level recipe sections

### `meta`
Identity, catalog semantics and audience.

### `experience`
Beauty profile, color story, motion profile, density and visual language.

### `shell`
Global shell settings such as frameless vs framed, status bar visibility, window radius and navigation model.

### `regions`
Optional region-level overrides for hero, main, side, status and overlay.

### `surfaces`
The workhorse of the schema. Each surface gets:
- id
- type
- region
- title/subtitle
- variant
- lazy/deferred flags
- layout constraints
- states
- metadata

### `behavior`
Layouts, persistence, runtime visibility policy, shortcuts and performance posture.

### `data`
Data sources and state treatments.

### `quality`
Validation posture and render checks.

### `variants`
Named override packs for the same structural recipe.

## Built-in tokens

### Beauty profiles
- `premium_focus`
- `cinematic_glass`
- `industrial_precision`
- `executive_signal`
- `editorial_dashboard`
- `neon_command`
- `warm_editorial`

### Color stories
- `graphite_cyan`
- `obsidian_violet`
- `frosted_emerald`
- `ember_gold`
- `carbon_ruby`
- `pearl_azure`
- `moonstone_teal`
- `paper_plum`

### Motion profiles
- `none`
- `subtle`
- `snappy_deluxe`
- `soft_cinematic`
- `operator_tight`
- `expressive_glass`

### Layout packs
- `balanced_split`
- `operator_dense`
- `analyst_focus`
- `wallboard`
- `inspector_heavy`
- `editorial_dual`

### Shell packs
- `frameless_glass`
- `framed_productive`
- `ops_console`
- `editorial_light`

## Built-in premium recipes

- `foundation.ops_console_premium`
- `foundation.analytics_cinematic`
- `foundation.inspector_precision`
- `foundation.executive_signal`
- `foundation.form_workbench`
- `foundation.asset_browser_glass`
- `foundation.timeline_review`
- `foundation.command_center_neon`

These are not meant to be final apps.
They are meant to be *strong starting stances*.

## Recommended workflow

1. Register foundation built-ins.
2. Pick the nearest built-in recipe.
3. Clone the payload.
4. Override only what you actually mean.
5. Preview the recipe through the catalog.
6. Add app-specific wiring outside the shared foundation.

## Anti-patterns this layer tries to starve out

- direct hand-authoring of every screen
- manual geometry nudging as a default practice
- style pasted inline into random widgets
- loading/error/empty implemented inconsistently per screen
- tabs created ad hoc with no recipe data
- one-off shell experiments bypassing presets and registry

## Example

```python
from forgeos.shared.pyside6_glass.foundry_foundation import (
    build_foundry_preview,
    register_builtin_foundry_foundation,
)

register_builtin_foundry_foundation()
widget = build_foundry_preview("foundation.ops_console_premium")
```

## What this layer does **not** solve by itself

This foundation layer does not yet fully solve:
- click-through safety for decorative overlays
- hard interaction audits
- keyboard-focus policy enforcement
- screenshot regression harnesses
- studio/editor tooling
- advanced state machine orchestration

Those belong in the next injectors.

That split is deliberate.
The foundation establishes the platform spine first.
