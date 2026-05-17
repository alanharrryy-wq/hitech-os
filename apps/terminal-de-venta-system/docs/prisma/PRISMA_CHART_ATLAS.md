# PRISMA Chart Atlas

Run date: 2026-05-11

## Decision

PRISMA charts are governed by ChartOps:

`Dato real -> Adapter -> Contract -> Option Builder -> Visual Recipe -> Chart Component -> Surface Profile -> Atlas -> Passport -> Inspector`

The atlas lives at:

- `shared/prisma-charts/prismaChartAtlas.ts`

The passports live at:

- `shared/prisma-charts/passports/*.passport.ts`

The Chart Lab governance maps live at:

- `products/chart-lab/app/src/prisma-charts/maps/chart-lab-maps.ts`

The PC inspector lives at:

- `/prisma-insights/chart-lab?preview=charts`

Feature flags remain off by default. Preview still uses `?preview=charts` or `?charts=1`.

## Chart Inventory

| chartId | Surface | Family | Status | Adapter | Real-source status |
|---|---|---|---|---|---|
| `pc.causal-flow-ribbon` | PC | flow | partial_real | `buildPcCausalFlowRibbonViewModel` | partial |
| `pc.operational-density-field` | PC | density | partial_real | `buildPcOperationalDensityFieldViewModel` | partial |
| `pc.service-dependency-graph` | PC | network | partial_real | `buildPcServiceDependencyGraphViewModel` | partial |
| `pc.inventory-risk-treemap` | PC | treemap | partial_real | `buildPcInventoryRiskTreemapViewModel` | partial |
| `pc.decision-ledger-timeline` | PC | timeline | partial_real | `buildPcDecisionLedgerTimelineViewModel` | partial |
| `pc.financial-operational-waterfall` | PC | waterfall | partial_real | `buildPcFinancialOperationalWaterfallViewModel` | partial |
| `tablet.shift-pulse-strip` | Tablet | strip | partial_real | `buildTabletShiftPulseStripViewModel` | partial |
| `tablet.sync-outbox-status-matrix` | Tablet | matrix | partial_real | `buildTabletSyncOutboxStatusMatrixViewModel` | partial |
| `mobile.owner-pulse-timeline` | Mobile | timeline | partial_real | `buildMobileOwnerPulseTimelineViewModel` | partial |
| `mobile.action-inbox-priority-stack` | Mobile | stack | partial_real | `buildMobileActionInboxPriorityStackViewModel` | partial |
| `mobile.health-radar-compact` | Mobile | radar | partial_real | `buildMobileHealthRadarCompactViewModel` | partial |
| `mobile.freshness-beacon-grid` | Mobile | rings | partial_real | `buildMobileFreshnessRingsViewModel` | partial |
| `mobile.incident-spark-cards` | Mobile | sparks | partial_real | `buildMobileIncidentSparkCardsViewModel` | partial |
| `mobile.confidence-meter-bands` | Mobile | bands | partial_real | `buildMobileConfidenceMeterBandsViewModel` | partial |

## Atlas Helpers

The atlas exposes helpers to find charts by:

- chart id: `getChartPassport(chartId)`
- family: `findChartsByFamily(family)`
- surface: `findChartsBySurface(surface)`
- route: `findChartsByRoute(route)`
- contract: `findChartsByContract(contractType)`

## How To Edit A Chart

1. Find the `chartId` in `prismaChartAtlas.ts`.
2. Open its passport under `shared/prisma-charts/passports/`.
3. Decide edit type:
   - Visual edit: recipe + option builder.
   - Data edit: adapter + source map.
   - Contract edit: contract + adapter + mock + verifier.
   - Layout edit: surface deck/card.
4. Run:
   - `pnpm run prisma:charts:atlas:verify`
   - app typecheck/build for the touched surface.

## Guardrails

- Do not import ECharts outside `shared/prisma-charts`.
- Do not add client-side DB access.
- Do not expose secrets.
- Do not make Mobile mutate business records.
- Do not turn Tablet into executive analytics.
- Do not add React runtime aliases.
- Do not add donuts, gauges, meters, or score rings around the Control Center clean score.

## Lab Factory

The canonical workshop is `F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app`.

Use:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify:all
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:promote -- --chart=pc.causal-flow-ribbon --target=pc --dry-run
```
