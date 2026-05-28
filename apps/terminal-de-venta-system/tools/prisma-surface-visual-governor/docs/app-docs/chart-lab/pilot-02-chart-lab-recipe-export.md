# PRISMA Surface Visual Governor · Pilot 02 · Chart Lab Recipe Export

## What this installed

Pilot 02 adds a public-safe recipe export contract to Chart Lab. It lets Chart Lab begin consuming the Materiality Catalog as a governed recipe source instead of copying visual CSS by hand.

## Installed public outputs

`products/chart-lab/app/public/surface-visual-governor/recipe-export/latest/`

- `chart.recipe.json`
- `visual.recipe.json`
- `motion.recipe.json`
- `background.recipe.json`
- `surface.compatibility.json`
- `ultra-codex.index.json`
- `index.json`

## Installed source helper

`products/chart-lab/app/src/prisma-surface-governor/chart-lab-recipe-export.ts`

This helper exposes stable paths and a small fetch function for Chart Lab UI integration in a later patch.

## Guardrails

- POS remains blocked.
- Tablet defaults are light-first.
- Background image assets are treated as Atmosphere Engine sources.
- The files are public-safe and should not contain local absolute paths, DB paths, Cloudflare tokens or local machine evidence.

## Verification

Run from repo root:

```powershell
node products\chart-lab\app\scripts\verify-surface-visual-governor-pilot02.mjs
```

The installer also writes a result ZIP to `<OUTPUT_DIR>` with logs, generated recipe copies and backup manifest.
