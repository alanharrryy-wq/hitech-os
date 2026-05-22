# PC DB Sync Validation Report

## Schema changes

None. Existing canonical models already provide the required surfaces:

- `Sale`, `SaleLine`, `SalePaymentTender`, `SaleReturn`;
- `CashSession`, `CashMovement`, `CashAdjustment`;
- `OutboxEvent`, `SyncAttempt`, `SyncConflict`;
- `DeviceHeartbeat`, `SyncCheckpoint`, `SyncOutboxStatusBucket`, `DataSourceFreshness`;
- `AuditEvent`, `SupportIncident`.

## Index verification

Verified existing indexes in `prisma/schema.prisma` cover the requested lookup patterns:

- Sale by business/date and unique folio.
- SaleLine by business/sale and business/product.
- SalePaymentTender by business/sale and tender/date.
- CashSession by business/terminal/status.
- OutboxEvent by business/status/date, topic, lifecycle/date, idempotency.
- SyncAttempt by business/source/status/date, device/date, idempotency.
- SyncConflict by business/status/date, source/severity/date, device/status, idempotency.
- DeviceHeartbeat by business/device/lastSeen, source/status/lastSeen.
- DataSourceFreshness by business/source/status, business/device/lastSeen, observed status.

## Repository and service changes

`pc-command-center.service.ts` centralizes bounded data access and view-model calculations for:

- sales/cash KPIs;
- device health;
- sync lifecycle;
- tri-db parity;
- data quality;
- license/runtime;
- Tablet communication.

## Integrity checks

Implemented checks:

- orphan `SaleLine`;
- sale total versus line total;
- payment total versus sale total;
- sale with missing cash session reference;
- duplicate folio within business sample;
- stale heartbeats;
- open sync conflicts.

## Sync ingest changes

Existing ingest/projector/idempotency implementation was preserved. New PC-facing actions:

- `POST /api/backoffice/sync/conflicts/review`;
- `POST /api/backoffice/sync/retry`.

Both actions write non-secret `AuditEvent` rows.

## Migrations and backfills

No migration or backfill was required. No data was deleted or rewritten.

## Validation results

- `pnpm -C products/pc/app typecheck`: PASS.
- `pnpm -C products/pc/app check:all`: PASS.
- `pnpm -C products/pc/app build`: PASS.
- `pnpm -C products/pc/app db:canonical:validate`: PASS.
- `pnpm -C products/pc/app verify:pc-ingest-idempotency`: PASS.
- `pnpm -C products/pc/app verify:pc-uiux-300`: PASS.
- `node products/pc/app/tools/verify_pc_routes_01.mjs --root products/pc/app`: PASS.
- HTTP smoke: PASS, 23 probes, evidence at `F:\repos\hitech-os\tools\_local\logs\pc-tablet-http-smoke.json`.
