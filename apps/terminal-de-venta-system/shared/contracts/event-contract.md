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

## Golden rule

If it affects money, inventory, customer, cash register, order, membership, fiscal data, or production, it must generate an event.
