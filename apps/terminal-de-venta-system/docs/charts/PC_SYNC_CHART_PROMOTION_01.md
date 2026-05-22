# PC Sync Chart Promotion 01

Status: CLOSED by implementation and verifier when `verify:pc-sync-chart-promotion` passes.

## Purpose

Promote two PC sync charts from the shared PRISMA chart infrastructure into the real PC `/sync` operator workflow:

- `pc.tablet-catalog-freshness-grid`
- `pc.sync-command-lifecycle-timeline`

The first production mount is `/sync` because that is where PC operators already generate catalog delta, bootstrap, and resync actions for Tablet catalog pull.

## Data Sources

The PC product endpoints read server-side PC evidence:

- `AuditEvent` topic `pc.catalog.delta.exported`
- `AuditEvent` topic `pc.tablet.governance_command`
- `DeviceHeartbeat`
- `SyncCheckpoint`
- `SyncAttempt`
- `SyncConflict`
- `getPcCatalogDeltaStatus`
- shared stream `pc.catalog.delta.v1`

The implementation does not import Chart Lab runtime or Chart Lab shell into PC.

## Contracts

Shared contracts live in `shared/prisma-charts/prismaChartContracts.ts`.

New view models:

- `TabletCatalogFreshnessGridRow`
- `TabletCatalogEntityFreshness`
- `SyncCommandLifecycleEvent`
- `PcSyncLifecycleStatus`
- `TabletCatalogRecommendedAction`

Adapters live in `shared/prisma-charts/prismaChartAdapters.ts`:

- `buildPcTabletCatalogFreshnessGridViewModel`
- `buildPcSyncCommandLifecycleTimelineViewModel`

## Endpoints

PC chart data endpoints:

- `GET /api/charts/pc/tablet-catalog-freshness-grid`
- `GET /api/charts/pc/sync-command-lifecycle-timeline`

Both endpoints return a `PrismaInsightEnvelope` with sanitized errors. Production responses do not use shared mocks.

## Components

PC `/sync` mounts:

- `products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx`
- `products/pc/app/components/sync/pc-sync-chart-promotion-panel.module.css`

The panel fetches both PC endpoints, renders loading, empty, error, and success states, and disables refresh while loading.

## Feature Flags And Source Mode

The existing Chart Lab preview flag system remains off by default. The PC `/sync` panel is production-mounted because the endpoints are real PC server endpoints.

Source mode is intentionally honest:

- Product PC endpoint source: real PC server evidence, `dataStatus: partial`
- Chart Lab registry sourceMode: `recorded-real`
- Not claimed as Chart Lab `live-real`

Reason: PC can prove the export ledger and any Tablet evidence reported back into PC. Tablet-local checkpoint details remain partial unless they are present in `DeviceHeartbeat` or `SyncCheckpoint`.

## Chart Lab Boundary

Chart Lab remains a lab:

- PC does not import `PrismaChartLabShell`
- PC does not import `chart-lab-registry`
- PC does not use Lab screenshots as evidence
- Lab source metadata remains recorded-real/partial for these charts

The new chart IDs are listed in Chart Lab registry and source metadata only to keep the shared promotion system complete and verifier-backed.

## Fixtures

Fixtures live in `fixtures/charts/pc_sync_chart_promotion_01`.

Freshness fixtures:

- `freshness-all-tablets-fresh.json`
- `freshness-one-tablet-stale.json`
- `freshness-one-tablet-error.json`
- `freshness-mixed-entity-freshness.json`
- `freshness-resync-recommended.json`
- `freshness-empty-no-checkpoint-data.json`

Lifecycle fixtures:

- `lifecycle-successful-catalog-delta.json`
- `lifecycle-bootstrap.json`
- `lifecycle-resync.json`
- `lifecycle-rejected-payload.json`
- `lifecycle-conflict.json`
- `lifecycle-duplicate-replay.json`
- `lifecycle-empty.json`

## Verification

Primary verifier:

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:pc-sync-chart-promotion
```

Required sync regression:

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system verify:pc-to-tablet-catalog-sync
```

Chart Lab/source-mode verifiers should also pass after this promotion:

```powershell
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system chart-lab:verify:chart-source-modes
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system chart-lab:verify:promotion-readiness
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system chart-lab:verify:promotion
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system chart-lab:verify:passports
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system prisma:charts:atlas:verify
pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system prisma:echarts:verify
```

## Known Limitations

The PC charts are live in the PC product surface, but readiness remains partial because PC does not always have Tablet-local checkpoint detail unless Tablet reports it back. The UI labels that state through quality metadata and empty/unknown states.

## Final Closure

PC sync chart promotion pipeline is CLOSED for:

- `pc.tablet-catalog-freshness-grid`
- `pc.sync-command-lifecycle-timeline`
