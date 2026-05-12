# PRISMA Data Flow And Authority

Status: factual map before implementation.
Scope: apps/terminal-de-venta-system.
Run date: 2026-05-11.

## Governing Product Law

Tablet operates.
PC governs.
Mobile supervises.
Core records through the Prisma-governed canonical database flow.
Control audits.

## Selected Primary Architecture

Tablet offline-first local operation
-> durable semantic OutboxEvent
-> PC sync ingest
-> validation pipeline
-> event ledger status on OutboxEvent
-> Prisma ORM projectors
-> canonical Prisma-governed database
-> Mobile /api/mobile/snapshot
-> chart view models, alerts, and notifications
-> Control audit and traceability

The TRI-DB direct bridge is present but is not the primary future sync path. It is classified as rescue, backfill, diagnostic, migration, constraint inspection, emergency projection, or self-test tooling only.

## App Surfaces

### Tablet

Primary root:

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app`

Observed surfaces:

- `app\api\pos\sales\complete\route.ts`: completes local sale through `posEngineRepository.completeLocalSale`.
- `src\server\pos-engine\repository.prisma.ts`: writes Sale, SaleLine, Product stock decrement, StockMovement, and OutboxEvent in a Prisma transaction.
- `src\server\pos-engine\event-factory.ts`: emits semantic sale and stock events.
- `src\server\pos-outbox\index.ts`: reads outbox state for reports and exports.
- `app\api\pos\shift\open\route.ts` and `app\api\pos\shift\close\route.ts`: local cash session routes.
- `src\server\pos-shift\repository.prisma.ts`: writes CashSession, CashMovement, and shift outbox events.

Local database:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\data\tablet-pos.db`

Tablet schema authority for local autonomy:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\prisma\schema.prisma`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\prisma\migrations\20260504190000_tablet_pos_durable_fields\migration.sql`

Tablet currently has a local SQLite schema with durable sale fields, `Sale.clientRequestId`, richer payment fields, OutboxEvent `terminalId`, `source`, `schemaVersion`, and `syncedAt`. This local schema is allowed for Tablet autonomy and must not require PC connectivity to sell.

### PC

Primary root:

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app`

Observed surfaces:

- `app\api\sync\ingest\route.ts`: compatibility sync ingest route that classifies or persists events.
- `app\api\backoffice\sync\ingest\route.ts`: backoffice sync ingest route with license guard and audit metadata.
- `src\server\services\sync-ingest.service.ts`: persists sync ingest into OutboxEvent.
- `src\server\validators\sync-event-contract.ts`: validates event envelope and detects conflicts.
- `src\lib\backoffice\sync-ingest-store.ts`: older/parallel backoffice ingest persistence path.
- `src\lib\backoffice\event-contract.ts`: older/parallel backoffice event contract.
- `app\api\backoffice\dashboard\route.ts`: backoffice dashboard route.
- `app\api\sync\tri-db\run\route.ts`: operator route that invokes the TRI-DB bridge.
- `src\server\prisma\client.ts`: resolves the canonical database URL for PC.

Canonical database path used by PC:

- `F:\repos\hitech-os\tools\_local\data\terminal-de-venta-system\canonical.db`

Current PC ingest persists valid events to `OutboxEvent` and marks conflicts/rejections, but the observed implementation is not yet the complete selected architecture because it does not consistently run Prisma projectors for canonical Sale, StockMovement, CashSession, CashMovement, and ReplenishmentSignal state after validation.

### Mobile

Primary root:

`F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app`

Observed surfaces:

- `app\api\mobile\snapshot\route.ts`: Mobile king endpoint.
- `src\lib\prisma-app\mobile-data-plane\state-loader.ts`: fetches Tablet, PC, Control, and Black-box source data.
- `src\lib\prisma-app\mobile-data-plane\payload-builders.ts`: builds legacy Mobile payloads plus intelligence snapshot.
- `src\lib\prisma-app\mobile-intelligence\snapshot-engine.ts`: builds intelligence snapshot.
- `src\lib\prisma-app\mobile-intelligence\chart-series-engine.ts`: produces chart view models.
- `src\lib\prisma-app\mobile-intelligence\alert-engine.ts`: builds deduplicated evidence-backed alerts.
- `src\components\prisma-app\PrismaMobileDashboard.tsx`: Mobile supervisor shell.
- `src\components\prisma-app\PrismaMobileCrystalCommand.tsx`: consumes `chartViewModels`.
- `src\components\prisma-app\PrismaMobilePremiumNavigator.tsx`: supervisor navigation.

Mobile does not own sales, cash, checkout, or inventory mutation. It supervises through `/api/mobile/snapshot` and view models.

### Control / Audit

Observed Control root:

`F:\repos\hitech-os\apps\terminal-de-venta-system\prisma-control-center`

Observed surfaces:

- `internal\web\index.html`
- `internal\web\app.js`
- `internal\py\prisma_control_center.py`
- `internal\py\health_checks.py`
- `internal\py\report_writer.py`
- `internal\config\services.json`
- `internal\config\safety_policy.json`

Control exists as an operational control center with service health, reports, wrappers, and public/local supervision support. For this architecture it is classified as audit and traceability surface, not a sales or canonical-write owner.

## Prisma ORM And Database Authority

Canonical Prisma ORM authority:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\schema.prisma`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\migrations\20260425000000_canonical_foundation\migration.sql`

Canonical engine:

- SQLite is the physical engine.
- Prisma ORM is the model authority.

Observed canonical models include:

- Business
- Store
- Terminal
- Product
- Barcode
- PriceList
- PriceListItem
- TaxRate
- StockSnapshot
- StockMovement
- Supplier
- PurchaseOrder
- PurchaseOrderLine
- GoodsReceipt
- GoodsReceiptLine
- ReplenishmentSignal
- CashSession
- CashMovement
- Sale
- SaleLine
- SaleReturn
- AuditCount
- OutboxEvent

Critical observed constraints:

- `CashSession` has a partial unique index in migration SQL:
  `uq_cashsession_single_open_per_terminal ON CashSession(businessId, terminalId) WHERE status = 'OPEN'`.
- This partial unique index must not be used as a normal SQLite UPSERT conflict target.
- Prisma schema represents the normal model, while migration SQL carries SQLite-specific partial indexes and triggers.

## Sync Routes

Tablet emits events into local OutboxEvent. Observed routes and readers:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\app\api\pos\sales\complete\route.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\app\api\pos\sync\panel\route.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\app\api\pos\sync\retry\route.ts`

PC ingest routes:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\app\api\sync\ingest\route.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\app\api\backoffice\sync\ingest\route.ts`

Bridge route:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\app\api\sync\tri-db\run\route.ts`

Mobile snapshot route:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\app\api\mobile\snapshot\route.ts`

## Event Types Observed

Machine-readable contract:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\contracts\sync-event-contract.v1.json`

Current canonical event topics in the contract:

- `sale.created`
- `sale.completed`
- `ticket.closed`
- `stock.decremented`
- `inventory.low_stock_detected`
- `sale.cancelled`
- `sale.refunded`
- `shift.opened`
- `shift.closed`
- `stock.adjusted`
- `catalog.product.created`
- `catalog.product.updated`
- `sync.event.sent`
- `sync.event.failed`
- `sync.conflict.detected`
- `sync.conflict.resolved`

Requested core projector topics:

- `sale.completed`
- `stock.decremented`
- `cash.session.opened`
- `cash.movement.recorded`
- `inventory.low_stock_detected`

Compatibility note: current Tablet shift code emits `shift.opened` and `shift.closed`, not `cash.session.opened` or `cash.movement.recorded`. A compatibility mapping is needed rather than inventing an incompatible flow.

## Current Outbox / Ledger Reality

Current canonical contract outbox states:

- `pending`
- `sent`
- `failed`
- `acked`
- `conflict`

Requested lifecycle states:

- `created_local`
- `queued`
- `sent`
- `received`
- `validated`
- `accepted`
- `projected`
- `reconciled`
- `conflict`
- `failed`
- `dead_letter`

Gap: existing app code uses `acked` as a compatibility outbox state. It must be mapped precisely and must not mean "fully reconciled" unless PC validation, projection, and reconciliation actually happened.

## TRI-DB Bridge Role

Bridge tool:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma\tri_db_bridge.py`

Latest bridge status artifact:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\tri-db\status.latest.json`

Observed role today:

- Direct SQLite row projection from Tablet DB to PC canonical DB.
- Backup and rollback.
- Partial unique index protection through non-partial unique index filtering.
- Self-test coverage for partial unique index behavior and idempotent rerun.

Required role from this architecture:

- rescue
- backfill
- diagnostic
- migration support
- constraint inspection
- emergency projection
- self-test harness

Rejected role:

- primary future sync path for normal business flow.

## Mobile Snapshot Role

Mobile king endpoint:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\app\api\mobile\snapshot\route.ts`

Mobile snapshot composes:

- Tablet operational reads.
- PC dashboard reads.
- Control health/incidents.
- Black-box health/incidents.
- local cache fallback on the client.

Mobile must emit null, unknown, unavailable, partial, stale, offline, or demo-disabled states when data is missing or uncertain. It must not invent production values.

Current chart view model keys observed:

- `operational-health-gauge`
- `sales-rhythm-hourly`
- `revenue-momentum`
- `inventory-risk-ranking`
- `alert-severity-donut`
- `sync-freshness-outbox`
- `cash-variance-bullet`
- `health-radar-dimensions`
- `top-products-ranking`

## Spreadsheet / Access / Manual Artifact Classification

Observed spreadsheet/export/support references include CSV exports in Tablet and PC reporting surfaces. No observed code path establishes Excel, CSV, XLSX, Access, `.mdb`, `.accdb`, pandas, or openpyxl as canonical truth.

Classification:

- CSV and JSON exports are child/support artifacts only.
- Excel/XLSX/Access/manual sheets are child/support artifacts only if introduced later.
- Canonical operational truth must remain Prisma ORM governed state plus validated semantic events.
- Spreadsheet data must never override Prisma-governed canonical state silently.

## Raw SQL Classification

Observed raw SQL is present in:

- migration SQL and SQLite-specific constraints/triggers.
- Tablet DB helper preflight for additive local SQLite repair.
- seed/diagnostic tooling.
- PC repository diagnostics such as operation repository raw query.
- Python bridge tooling.

Normal business projection path must use Prisma Client and Prisma transactions. Raw SQL can remain in migrations, diagnostic tools, validation tools, bridge/rescue tooling, and SQLite feature preflights where Prisma has no safe equivalent.

## Implementation Gaps To Close

1. Standardize event sync as primary in docs and labels.
2. Add deterministic lifecycle contract and precise `acked` compatibility mapping.
3. Ensure Tablet events include idempotency and enough payload for PC projectors.
4. Consolidate PC ingest so compatibility routes share one validation/projector pipeline.
5. Add Prisma Client projectors for core event types where business rules are known.
6. Keep unknown or unsafe business cases structured as conflict/unsupported diagnostics, not fake success.
7. Preserve TRI-DB bridge as secondary rescue/backfill/diagnostic tooling.
8. Align Mobile runtime mode and chart consumption with view models and honest source status.
9. Document traceability from Tablet producer to PC validator/projector, Prisma model, Mobile field/chart/alert, and Control audit.
