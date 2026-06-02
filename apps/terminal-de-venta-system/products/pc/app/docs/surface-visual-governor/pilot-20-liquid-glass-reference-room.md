
# Pilot 20 · Liquid Glass Reference Room

Installed at: `20260601_114434`

## Purpose

Create a safe PC-only reference room for PRISMA Liquid Glass. This route demonstrates:

- backdrop blur with saturation and brightness;
- inner rim light;
- glass specimen levels;
- SVG pseudo-refraction with `feTurbulence` and `feDisplacementMap`;
- reduced-motion compliant ambient movement;
- governed route budget and compatibility manifest.

## Route

`/referencia-visual/liquid-glass`

## Write boundary

Allowed:

- `products/pc/app/app/referencia-visual`
- `products/pc/app/app/prisma-liquid-glass.module.css`
- `products/pc/app/public/surface-visual-governor/liquid-glass`
- `products/pc/app/scripts/verify-surface-visual-governor-pilot20.mjs`

Forbidden:

- POS
- Checkout
- Tablet productive routes
- DB files
- package and lockfiles
- deploy configs

## Next possible phase

After visual approval, selectively adopt material pieces in Dashboard/Hoy:

- top header;
- hero cards;
- command/action bar;
- selected panels.

Do not apply the reference room directly to tables, POS, Checkout, or Tablet.
