# Rendering System - Round 3

This round introduces a dedicated rendering package for premium glass surfaces.

## What lands in this round

- `rendering/glass_painter.py`
  - deterministic painter-based surface composition
  - glass gradients
  - border pass
  - highlight pass
  - optional neon and noise pass
- `rendering/overlays.py`
  - non-invasive overlay renderer mounted on top-level surfaces
- `rendering/surface_renderer.py`
  - helpers for assigning roles and syncing overlays from an `AppearanceSnapshot`
- template integration
  - shell, hero, main, side, footer, status, and dynamic panels now receive visual roles
  - overlays are installed automatically

## Role model

Widgets do not pick colors directly. Widgets expose intent via properties:

- `visualRole`
- `visualVariant`
- `visualEmphasis`

The rendering layer converts those properties + the appearance snapshot into a real painted surface.

## Why overlays instead of rewriting every widget

This round is optimized for speed and safety. A child overlay gives the project painter-based premium rendering without forcing a mass rewrite of every reusable widget class.

## Contract for future rounds

- keep adding surface roles instead of hardcoded styles
- move one-off glow hacks into `effects.py` or `rendering/`
- remove legacy visual overrides once the new overlays are fully adopted
