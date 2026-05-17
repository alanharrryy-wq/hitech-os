# PRISMA Charts Baseline Before Wiring

Run date: 2026-05-11
Repository root: F:\repos\hitech-os
Project root: F:\repos\hitech-os\apps\terminal-de-venta-system

## Baseline Decision

The existing PRISMA ECharts pack is a safe preview pack. It is feature-flagged off by default and enabled by:

- `?preview=charts`
- `?charts=1`
- `PRISMA_CHARTS_ENABLED=true` plus the surface flag

The current implementation uses deterministic mock data through `shared/prisma-charts/prismaChartAdapters.ts`. This pass wires real safe sources first, while preserving deterministic fallback for charts whose safe source is unavailable or ambiguous.

## Current Chart Foundation

- Shared chart root: `shared/prisma-charts`
- ECharts loader: `shared/prisma-charts/prismaEchartsLoader.ts`
- Common wrapper: `shared/prisma-charts/PrismaEChart.tsx`
- Theme: `shared/prisma-charts/prismaChartTheme.ts`
- Contracts: `shared/prisma-charts/prismaChartContracts.ts`
- Registry: `shared/prisma-charts/prismaChartRegistry.ts`
- Mocks: `shared/prisma-charts/prismaChartMocks.ts`
- Adapters: `shared/prisma-charts/prismaChartAdapters.ts`
- Options: `shared/prisma-charts/prismaChartOptions.ts`
- Quality helpers: `shared/prisma-charts/prismaChartQuality.ts`
- Flags: `shared/prisma-charts/prismaChartFlags.ts`

## Preview Surfaces

PC:

- Route: `products/pc/app/app/prisma-insights`
- Page: `products/pc/app/app/prisma-insights/page.tsx`
- Grid: `products/pc/app/app/prisma-insights/PrismaPcInsightsGrid.tsx`
- Charts: 6

Tablet:

- Route: `products/tablet/app/app/prisma-pulse`
- Page: `products/tablet/app/app/prisma-pulse/page.tsx`
- Panel: `products/tablet/app/app/prisma-pulse/PrismaTabletPulsePanel.tsx`
- Charts: 2

Mobile:

- Route: `products/mobile/app/app/prisma-command`
- Page: `products/mobile/app/app/prisma-command/page.tsx`
- Deck: `products/mobile/app/app/prisma-command/PrismaMobileCommandDeck.tsx`
- Charts: 6

## Existing Chart List

PC:

- `pc.causal-flow-ribbon` / `PcCausalFlowRibbon`
- `pc.operational-density-field` / `PcOperationalDensityField`
- `pc.service-dependency-graph` / `PcServiceDependencyGraph`
- `pc.inventory-risk-treemap` / `PcInventoryRiskTreemap`
- `pc.decision-ledger-timeline` / `PcDecisionLedgerTimeline`
- `pc.financial-operational-waterfall` / `PcFinancialOperationalWaterfall`

Tablet:

- `tablet.shift-pulse-strip` / `TabletShiftPulseStrip`
- `tablet.sync-outbox-status-matrix` / `TabletSyncOutboxStatusMatrix`

Mobile:

- `mobile.owner-pulse-timeline` / `MobileOwnerPulseTimeline`
- `mobile.action-inbox-priority-stack` / `MobileActionInboxPriorityStack`
- `mobile.health-radar-compact` / `MobileHealthRadarCompact`
- `mobile.freshness-beacon-grid` / `MobileFreshnessRings`
- `mobile.incident-spark-cards` / `MobileIncidentSparkCards`
- `mobile.confidence-meter-bands` / `MobileConfidenceMeterBands`

## Baseline Safety Notes

- No app surface should import ECharts directly. ECharts belongs inside `shared/prisma-charts`.
- No client component should read the database or credentials.
- PC may use server-side canonical Prisma summaries and sanitized bridge status.
- Tablet may use server-side local runtime/sync snapshots.
- Mobile may use snapshot/data-plane view models and must remain read-only.
- The Control Center clean score remains text-only. This chart pass must not add donuts, gauges, meters, rings, or score ornaments around it.
- React runtime aliases must not be mapped in `tsconfig.json`, especially not to `node_modules/@types/react`.

## Known Safe Existing Sources

- PC canonical dashboard: `products/pc/app/src/lib/backoffice/dashboard.ts`
- PC bridge status: `products/pc/app/src/server/services/tri-db-status.service.ts`
- Tablet runtime snapshot: `products/tablet/app/src/server/tablet-runtime-snapshot`
- Tablet pending sync panel: `products/tablet/app/src/server/pos-sync-panel/index.ts`
- Mobile snapshot/data plane: `products/mobile/app/src/lib/prisma-app/mobile-data-plane`
- Mobile intelligence engines: `products/mobile/app/src/lib/prisma-app/mobile-intelligence`
- Sanitized bridge status artifact: `shared/tri-db/status.latest.json`

## Baseline Risk

Some charts are intentionally broader than the currently exposed safe summaries. Those charts must stay `partial` or `mock` until a safe canonical source exists. No chart should claim `real` unless its values are derived from an existing server/API/view-model source.
