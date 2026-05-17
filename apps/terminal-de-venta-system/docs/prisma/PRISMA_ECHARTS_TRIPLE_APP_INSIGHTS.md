# PRISMA ECharts Triple-App Insights Pack

## Decision

This pack adds a shared PRISMA chart foundation and three preview surfaces:

- PC Backoffice: governance and analysis at `/prisma-insights`.
- Tablet Operations: two touch-first operational charts at `/prisma-pulse`.
- Mobile Owner Command: supervision charts at `/prisma-command`.

The pack follows the PRISMA product law:

- Tablet operates.
- PC governs.
- Mobile supervises.
- Core records.
- Control audits.

The Control Center health score remains plain text only. This work does not add a chart, ring, gauge, meter, or visual ornament around the main score.

## Feature Flags

All charts are off by default.

- `PRISMA_CHARTS_ENABLED=true`
- `PRISMA_CHARTS_PC=true`
- `PRISMA_CHARTS_TABLET=true`
- `PRISMA_CHARTS_MOBILE=true`
- `PRISMA_CHARTS_MOCKS_FALLBACK=false` disables deterministic fallback data.

Safe preview can also be enabled route by route with:

- `?preview=charts`
- `?charts=1`

## Shared Foundation

Shared code lives in `shared/prisma-charts/`.

- `PrismaEChart.tsx`: client-only ECharts wrapper with lazy loading, empty/loading/error states, ARIA label, and click focus callback.
- `prismaEchartsLoader.ts`: the only place that imports and registers ECharts modules.
- `prismaChartContracts.ts`: typed view models and chart contracts.
- `prismaChartTheme.ts`: PRISMA white/silver/crystal theme with electric blue status accents.
- `prismaChartRegistry.ts`: chart registry, purpose, visual encoding, filters, interactions, accessibility, and responsive notes.
- `prismaChartMocks.ts`: deterministic mock data for all fourteen charts.
- `prismaChartAdapters.ts`: typed adapter seam for future real data sources.
- `prismaChartOptions.ts`: ECharts option builders for each chart.

Apps must not import ECharts directly. They consume shared contracts, wrappers, registry data, and option builders.

## Chart Inventory

### PC Backoffice

1. Causal Flow Ribbon
   - Contract: `CausalFlowRibbonDatum[]`.
   - Purpose: connect source module, cause, effect, and action target.
   - Visual form: Sankey ribbon.
   - Data source candidate: Control Center incidents, sync ledger, audit trail.
   - Fallback: deterministic mock adapter.

2. Operational Density Field
   - Contract: `OperationalDensityCell[]`.
   - Purpose: reveal pressure concentration by module and time.
   - Visual form: heatmap.
   - Data source candidate: PC sync and operational telemetry summaries.
   - Fallback: deterministic mock adapter.

3. Service Dependency Graph
   - Contract: service nodes and edges.
   - Purpose: show app, endpoint, service, DB, and Control dependencies.
   - Visual form: force graph.
   - Data source candidate: runtime health probes and route registry.
   - Fallback: deterministic mock adapter.

4. Inventory Risk Treemap
   - Contract: `InventoryRiskNode[]`.
   - Purpose: expose stockout and revenue risk by category/SKU.
   - Visual form: treemap.
   - Data source candidate: canonical inventory projection.
   - Fallback: deterministic mock adapter.

5. Decision Ledger Timeline
   - Contract: `DecisionLedgerPoint[]`.
   - Purpose: audit decisions, incidents, actions, evidence, and resolution history.
   - Visual form: time line plus scatter events.
   - Data source candidate: Control audit and PC decision ledger.
   - Fallback: deterministic mock adapter.

6. Financial / Operational Waterfall
   - Contract: `OperationalWaterfallStep[]`.
   - Purpose: connect operational deltas to money impact.
   - Visual form: waterfall bars.
   - Data source candidate: sales, refunds, inventory incident, and cost projections.
   - Fallback: deterministic mock adapter.

### Tablet Operations

1. Shift Pulse Strip
   - Contract: `ShiftPulseBucket[]`.
   - Purpose: answer if the current shift can keep operating.
   - Visual form: bar plus line strip.
   - Data source candidate: Tablet local POS shift summaries.
   - Fallback: deterministic mock adapter.

2. Sync Outbox Status Matrix
   - Contract: `SyncOutboxMatrixCell[]`.
   - Purpose: show pending, failed, retrying, and blocking local sync items.
   - Visual form: heatmap matrix.
   - Data source candidate: Tablet local semantic outbox.
   - Fallback: deterministic mock adapter.

### Mobile Owner Command

1. Owner Pulse Timeline
   - Contract: `OwnerPulsePoint[]`.
   - Purpose: show whether the operation is improving or degrading.
   - Visual form: line plus incident points.
   - Data source candidate: `/api/mobile/snapshot`.
   - Fallback: deterministic mock adapter.

2. Action Inbox Priority Stack
   - Contract: `ActionPriorityStackDatum[]`.
   - Purpose: show action load by responsible owner and priority.
   - Visual form: horizontal stacked bars.
   - Data source candidate: mobile action inbox view model.
   - Fallback: deterministic mock adapter.

3. Health Radar Compact
   - Contract: `HealthRadarAxis[]`.
   - Purpose: reveal weak operating dimensions behind owner supervision.
   - Visual form: compact radar chart.
   - Data source candidate: mobile health radar engine.
   - Fallback: deterministic mock adapter.

4. Freshness Rings
   - Contract: `FreshnessBeacon[]`.
   - Purpose: show fresh, aging, stale, offline, or unknown source state by module.
   - Visual form: compact freshness beacon bars.
   - Data source candidate: mobile source status and snapshot freshness.
   - Fallback: deterministic mock adapter.

5. Incident Spark Cards
   - Contract: `IncidentSparkCard[]`.
   - Purpose: show incident microtrends and next action without turning Mobile into PC.
   - Visual form: small multiple spark cards.
   - Data source candidate: mobile alert and incident engines.
   - Fallback: deterministic mock adapter.

6. Confidence Meter Bands
   - Contract: `ConfidenceBand[]`.
   - Purpose: explain the trust level of the mobile snapshot.
   - Visual form: linear confidence bands only.
   - Data source candidate: mobile data quality engine.
   - Fallback: deterministic mock adapter.

## Data Feeding Model

The first implementation intentionally uses deterministic typed mock view models. Real data should be connected through `prismaChartAdapters.ts`, keeping these rules:

- Do not invent backend endpoints.
- Do not let Mobile mutate sales, cash, checkout, or inventory.
- Do not bypass `/api/mobile/snapshot` for Mobile supervision data.
- Do not duplicate business rules in React components.
- Keep missing data explicit as empty, partial, stale, offline, or unknown.

## Validation

Run:

```powershell
pnpm run prisma:echarts:verify
pnpm -C products/pc/app typecheck
pnpm -C products/tablet/app typecheck
pnpm -C products/mobile/app typecheck
```

Build commands can be run app by app after typecheck if local dependencies and current unrelated worktree state allow it.
