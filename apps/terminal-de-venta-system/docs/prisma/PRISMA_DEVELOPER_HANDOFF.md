# PRISMA Developer Handoff

Run timestamp: 2026-05-11T01:55:09.6153907-06:00

## Architecture Standard

The selected architecture is:

Tablet offline-first -> OutboxEvent -> PC `/api/sync/ingest` -> validation pipeline -> event ledger -> Prisma ORM projectors -> canonical database -> Mobile `/api/mobile/snapshot` -> chart view models, alerts, notifications -> Control audit.

TRI-DB direct bridge remains secondary rescue/backfill/diagnostic tooling.

## Source Owners

Tablet producer:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\src\server\pos-engine\event-factory.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\src\server\pos-engine\repository.prisma.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app\src\server\pos-shift\repository.prisma.ts`

Shared event contract:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\contracts\sync-event-contract.v1.json`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\shared\twin-kernel\src\sync\events.ts`

PC validator/projector:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\src\server\validators\sync-event-contract.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\src\server\services\sync-ingest.service.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\src\server\services\sync-projectors.service.ts`

Canonical model:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\schema.prisma`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\migrations\20260425000000_canonical_foundation\migration.sql`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\prisma\migrations\20260511000000_event_ledger_lifecycle\migration.sql`

Mobile snapshot/view models:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\app\api\mobile\snapshot\route.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\lib\prisma-app\mobile-data-plane\state-loader.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\lib\prisma-app\mobile-data-plane\runtime-mode.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\lib\prisma-app\mobile-intelligence\chart-series-engine.ts`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\products\mobile\app\src\lib\prisma-app\mobile-intelligence\view-models.ts`

Bridge:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\tools\prisma\tri_db_bridge.py`

## Traceability Table

| Event type | Tablet producer | PC validator | PC projector | Canonical model | Mobile surface | Control/audit |
|---|---|---|---|---|---|---|
| `sale.completed` | `event-factory.ts`, `repository.prisma.ts` | `sync-event-contract.ts` | `projectSaleCompleted` | `Sale`, `SaleLine`, `OutboxEvent` | snapshot KPIs, sales rhythm, revenue momentum, top products | ingest diagnostics, event lifecycle row |
| `stock.decremented` | `event-factory.ts`, `repository.prisma.ts` | `sync-event-contract.ts` | `projectStockDecremented` | `Product`, `StockMovement`, `OutboxEvent` | inventory risk, sync freshness | conflict diagnostics for negative stock |
| `cash.session.opened` | `pos-shift/repository.prisma.ts` | `sync-event-contract.ts` | `projectCashSessionOpened` | `CashSession`, `OutboxEvent` | cash variance, operational health | overlap conflict diagnostics |
| `cash.movement.recorded` | `pos-shift/repository.prisma.ts` | `sync-event-contract.ts` | `projectCashMovementRecorded` | `CashMovement`, `OutboxEvent` | cash variance, health radar | movement ledger diagnostics |
| `inventory.low_stock_detected` | `event-factory.ts` | `sync-event-contract.ts` | `projectLowStockDetected` | `ReplenishmentSignal`, `OutboxEvent` | inventory risk ranking, alerts | replenishment trace |

## Compatibility Notes

- `topic` remains accepted as a compatibility alias for `eventType`.
- `shift.opened` maps to `cash.session.opened`.
- `shift.closed` maps to `cash.movement.recorded`.
- `acked` is compatibility status and must not be read as governance reconciliation unless the lifecycle evidence says `projected` or `reconciled`.

## Raw SQL Policy

Normal app business flow must use Prisma Client. Raw SQL remains acceptable for migrations, diagnostics, validation tooling, and bridge rescue/backfill paths when documented.

