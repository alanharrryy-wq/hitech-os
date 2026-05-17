# PRISMA Chart Creation Kit

## Purpose

New PRISMA charts must start as governed system pieces, not loose components.

Required flow:

`question -> family -> chartId -> contract -> mock -> adapter -> option builder -> component -> passport -> atlas -> lab -> verifier`

## New Chart Request Contract

Minimum request fields:

- `name`
- `questionAnswered`
- `primaryUser`
- `surface`
- `dataSource`
- `entities`
- `timeRange`
- `statusStates`
- `interactionNeeded`
- `visualFamilyGuess`
- `productionRisk`

## Decision Tree

- Cause/effect/action: `flow`
- Pressure by time/module: `density`
- Dependencies: `network`
- Hierarchical impact: `treemap`
- Events over time: `timeline`
- Positive/negative accumulated impact: `waterfall`
- Shift states over time: `strip`
- Entity/status grid: `matrix`
- Priority load: `stack`
- Health dimensions: `radar`
- Freshness/confidence by source: `rings`
- Microtrend cards: `sparks`
- Confidence dimensions: `bands`

## Files To Create

Minimum:

- `shared/prisma-charts/passports/<chartId>.passport.ts`
- contract in `shared/prisma-charts/prismaChartContracts.ts`
- mock in `shared/prisma-charts/prismaChartMocks.ts`
- adapter in `shared/prisma-charts/prismaChartAdapters.ts`
- option builder in `shared/prisma-charts/prismaChartOptions.ts`
- component in the target surface route
- atlas registration in `shared/prisma-charts/prismaChartAtlas.ts`

If the family is new:

- `shared/prisma-charts/recipes/<family>Recipe.ts`
- `shared/prisma-charts/state-gallery/<family>States.ts` or state-gallery registration

Also update:

- `docs/prisma/PRISMA_CHART_ATLAS.md`
- `docs/prisma/PRISMA_CHART_REAL_DATA_SOURCE_MAP.md`
- `products/chart-lab/app/src/prisma-charts/maps/chart-lab-maps.ts`
- `products/chart-lab/app/src/prisma-charts/chart-lab-control-model.ts`
- `tools/verify_prisma_chart_atlas_01.mjs`

## Acceptance Criteria

A chart is not accepted unless it:

- has a stable unique `chartId`
- has a passport
- is in the atlas
- has a typed contract
- has deterministic mock fallback
- has a real adapter or explicit unavailable reason
- has an option builder
- uses a visual recipe
- supports empty, partial, stale, offline, unknown, and critical states where applicable
- appears in Chart Lab
- has runtime controls or an honest disabled reason
- has a visual tuning passport and map entries
- passes `pnpm run prisma:charts:atlas:verify`
- passes `pnpm -C products/chart-lab/app verify:all`
- does not import ECharts outside shared
- does not invent data
- does not touch React runtime aliases

## Chart 15 Walkthrough

1. Copy the request contract into `NEW_CHART_TEMPLATE.md`.
2. Add contract, mock, adapter, option builder, passport, atlas entry, Lab registry entry, control schema, source map entry, state coverage, and promotion manifest.
3. Run:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify:all
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" prisma:charts:atlas:verify
```

## Golden Rule

No chart exists because it looks nice.

Every chart must answer:

`Esta grafica existe para responder: ________`

If it cannot answer that in five seconds, it is not ready.
