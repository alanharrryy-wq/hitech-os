# Shared Sync Contract

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

Tablet executes sale -> writes `Sale`/`SaleLine`/`StockMovement` -> creates `OutboxEvent` -> if sync is available, sends events -> PC ingests events -> PC validates contract -> PC updates consolidated view -> PC marks events received -> if conflict exists, PC resolves.

## Outbox states

- `pending`
- `sent`
- `failed`
- `acked`
- `conflict`

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
