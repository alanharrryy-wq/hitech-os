# Shared Event Contract

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

Define eventos como verdad operacional entre Tablet, PC, outbox, sync y auditoria.


## Minimum POS events

- `sale.created`
- `sale.completed`
- `ticket.closed`
- `stock.decremented`
- `inventory.low_stock_detected`

## Later events

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

## Every sensitive event must include

- `eventId`
- `topic`
- `businessId`
- `terminalId`
- `actorId`
- `source`
- `occurredAt`
- `payload`
- `schemaVersion`

## Canonical machine-readable source

The canonical machine-readable source is:

`shared/contracts/sync-event-contract.v1.json`

All Tablet emitted events, PC accepted events, shared/twin-kernel sync events,
outbox states and conflict codes must match that file.

## Canonical conflict codes

- `product_discontinued`
- `old_local_price`
- `negative_stock`
- `duplicate_event`
- `terminal_not_registered`
- `sale_outside_shift`
- `inconsistent_sequence`
- `invalid_schema`
- `unknown_topic`

## Deprecated aliases

Aliases such as `sync.conflict_detected`, `sync.conflict_resolved`,
`catalog.updated`, `stock.received`, `return.created`, `sync.started`,
`sync.succeeded`, `sync.failed`, `outbox.enqueued` and `outbox.dispatched`
are deprecated compatibility names. They must not be returned as canonical
topics.

## Golden rule

If it affects money, inventory, customer, cash register, order, membership, fiscal data, or production, it must generate an event.
