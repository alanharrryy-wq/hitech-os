# PC to Tablet Catalog Delta Closure 01

Status: implemented, pending command evidence in final operator report.

## Ownership Model

PC owns canonical catalog/master-data distribution for:

- Product
- Brand
- Supplier
- ProductSupplier
- PriceList
- PriceListItem
- TaxRate
- DropdownCatalog
- DropdownOption

Tablet owns local selling continuity. Tablet maps the PC source business scope into its local POS business scope so existing offline sales remain local. Catalog pulls do not reset local Product.stockOnHand on updates; stock is set only when a product is first created locally.

## Contract

Contract file:

`shared/contracts/pc-tablet-catalog-delta.v1.json`

Shared TypeScript validator/types:

`shared/twin-kernel/src/sync/catalog-delta.ts`

Contract id:

`PRISMA_PC_TO_TABLET_CATALOG_DELTA_V1`

Stream:

`pc.catalog.delta.v1`

Cursor:

`updatedAt_entityRank_id`

## PC Export

Endpoint:

`POST /api/sync/export/catalog-delta`

Read-only GET is also available:

`GET /api/sync/export/catalog-delta`

Modes:

- `delta`
- `bootstrap`
- `resync`

The PC exporter reads canonical Prisma tables, orders changes deterministically, validates the envelope against the shared contract, and records POST-generated exports in `AuditEvent` with topic `pc.catalog.delta.exported`.

## Tablet Pull

Endpoint:

`POST /api/pos/sync/pull`

Status endpoint:

`GET /api/pos/sync/pull`

Tablet pulls from PC `/api/sync/export/catalog-delta`, validates the shared envelope, applies records in dependency order, and stores local checkpoint state in `SyncCheckpoint`.

Checkpoint fields include:

- stream
- source
- scopeKey
- deviceId
- terminalId
- cursorValue
- lastEventId
- lastAttemptId
- status
- lifecycleStatus
- checkpointAt
- lastAttemptedAt
- lastSuccessfulAt
- metadataJson

Checkpoint advancement rule:

- success or empty result advances/preserves the cursor as successful
- invalid payload, rejected item, or conflict records attempt metadata but does not advance the successful cursor

## Failure Modes

- duplicate change id: counted as duplicate, not double-applied
- retry/stale cursor: item cursor at or before current checkpoint is counted as duplicate
- unknown entity: rejected by shared validator
- invalid payload: rejected before apply
- missing dependency: conflict, checkpoint success is not advanced
- PC unavailable: Tablet reports warning and continues local POS operation
- PC sync disabled: Tablet reports disabled state and continues local POS operation

## Operator UI

PC:

- `/sync`
- `/tablet-communication`

PC buttons:

- `Generar delta catalogo` -> `POST /api/sync/export/catalog-delta` with `{ "mode": "delta" }`
- `Bootstrap catalogo` -> `POST /api/sync/export/catalog-delta` with `{ "mode": "bootstrap" }`
- `Resync catalogo` -> `POST /api/sync/export/catalog-delta` with `{ "mode": "resync" }`
- `Registrar refresh runtime` -> `POST /api/backoffice/tablet-communication/governance-command`

Tablet:

- `/sync`

Tablet buttons:

- `Pedir delta` -> `POST /api/pos/sync/pull` with `{ "mode": "delta" }`
- `Bootstrap inicial` -> `POST /api/pos/sync/pull` with `{ "mode": "bootstrap", "resetCheckpoint": true }`
- `Resync controlado` -> `POST /api/pos/sync/pull` with `{ "mode": "resync", "resetCheckpoint": true }`
- `Actualizar` -> `GET /api/pos/sync/pull`

The Tablet screen separates outbound Tablet to PC queue state from inbound PC to Tablet catalog pull state.

## Chart Lab Boundary

Chart Lab was not used as production runtime, not imported into PC/Tablet, and not used as evidence for catalog sync closure.

## Verification Commands

- `pnpm -C apps/terminal-de-venta-system/products/pc/app prisma:generate`
- `pnpm -C apps/terminal-de-venta-system/products/tablet/app prisma:generate`
- `pnpm -C apps/terminal-de-venta-system/products/pc/app typecheck`
- `pnpm -C apps/terminal-de-venta-system/products/tablet/app typecheck`
- `pnpm -C apps/terminal-de-venta-system verify:pc-to-tablet-catalog-sync`
- `pnpm -C apps/terminal-de-venta-system verify:supplier-product-supplier-sync`
- `pnpm -C apps/terminal-de-venta-system verify:tablet-sync-dispatcher`
- `pnpm -C apps/terminal-de-venta-system verify:sync-closure-truth`

## Evidence Matrix

| Entity | Tablet schema | PC schema | Contract | PC export | Tablet pull/import | Checkpoint | Validator | Applicator | Duplicate/retry/conflict | Fixtures | Verifier | PC UI | Tablet UI | Final |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Product | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
| Brand | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
| Supplier | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
| ProductSupplier | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
| PriceList | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
| PriceListItem | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
| TaxRate | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
| DropdownCatalog | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
| DropdownOption | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | yes | CLOSED |
