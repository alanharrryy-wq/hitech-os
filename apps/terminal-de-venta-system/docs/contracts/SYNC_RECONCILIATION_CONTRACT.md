# Sync Reconciliation Contract

Estado: canon listo para codigo.
Idioma operativo: es-MX.
Alcance: contratos, arquitectura y criterios de implementacion; no implementa motores finales.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## Proposito

Permite que Tablet opere sin PC/red y que PC consolide despues sin bloquear venta local.


## Goal

Allow Tablet to operate without PC/network and let PC consolidate later.

## Basic flow

Tablet executes sale -> writes `Sale`/`SaleLine`/`StockMovement` -> creates semantic `OutboxEvent` -> if sync is available, sends events -> PC ingests events -> PC validates contract -> PC writes event-ledger lifecycle -> PC runs Prisma ORM projectors -> PC reconciles or marks conflict/dead-letter -> Mobile supervises through `/api/mobile/snapshot` -> Control audits.

## Outbox states

- `pending`
- `sent`
- `failed`
- `acked`
- `conflict`

Compatibility note: `acked` is not proof of governed reconciliation unless the event ledger also has `lifecycleStatus = reconciled`.

## Lifecycle states

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

## Possible conflicts

- `product_discontinued`
- `old_local_price`
- `negative_stock`
- `duplicate_event`
- `terminal_not_registered`
- `sale_outside_shift`
- `inconsistent_sequence`
- `invalid_schema`
- `unknown_topic`

## Canonical machine-readable source

The canonical machine-readable source is:

`shared/contracts/sync-event-contract.v1.json`

All outbox states, conflict codes, event topics and required event envelope
fields must match that file.

## Offline rule

Offline does not mean permission for everything.

Allowed offline: sales with active local catalog, local tickets, local shift/day cuts, local export and local data consultation.

Blockable offline: massive price changes, advanced product creation, large inventory adjustments, sensitive refunds, permission changes and multi-branch operations.
