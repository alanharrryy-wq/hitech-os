# PRISMA POS Visual Control Plane v01

This package installs the first real control layer after the masterplan.

## Purpose

Create one governed place for POS visual values:

- glass blur and opacity
- glow and highlights
- card radius and depth
- packshot scale and lift
- ticket thumbnail and spacing
- checkout CTA emphasis
- motion timings
- shell haze and blur

## Runtime behavior

This package is intentionally conservative. It installs token files and inserts CSS-module-safe bridge blocks into:

- `products/tablet/app/components/pos/pos.module.css`
- `products/tablet/app/components/tablet-shell/prisma-tablet-shell.module.css`

The visible design should not jump wildly yet. The next ZIP, Surface Lock, will make cards and ticket consume these tokens more aggressively.

## Forbidden scope

No PC, no Mobile, no shared-kernel, no backend, no `/prisma-dark-pos-reference`.
