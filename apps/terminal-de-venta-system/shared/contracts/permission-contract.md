# Shared Permission Contract

Estado: canon listo para codigo.
Fuente machine-readable: `shared/contracts/security-audit-permissions.v1.json`.
Idioma operativo: es-MX.
Alcance: contratos, arquitectura y criterios de implementacion; no implementa motores finales.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## Proposito

Separa permisos locales Tablet, permisos pro y permisos de gobierno PC.


## Tablet Solo

- `pos.sale.create`
- `pos.sale.complete`
- `pos.ticket.view`
- `inventory.local.view`
- `report.today.view`
- `export.local.create`

## Tablet Pro

- `pos.sale.cancel`
- `pos.return.create`
- `inventory.local.adjust`
- `shift.open`
- `shift.close`
- `event.outbox.view`

## Tablet + PC

- `catalog.write`
- `price.write`
- `inventory.adjust.approve`
- `purchase.write`
- `receiving.write`
- `audit.view`
- `sync.conflict.resolve`
- `user.permission.manage`

## Every sensitive action must record

- `actorId`
- `role`
- `terminalId`
- `businessId`
- `action`
- `entityType`
- `entityId`
- `before`
- `after`
- `createdAt`

## Minimal roles

- `tablet_operator`
- `tablet_supervisor`
- `pc_backoffice`
- `pc_admin`

## Implementation guardrails

- Tablet sale complete and local export must include audit-shaped metadata.
- Tablet offline local sale/export remains allowed and must not depend on PC.
- PC sync ingest must include `sync.ingest.write` audit metadata.
- PC conflict resolution must use `sync.conflict.resolve`; current conflict route exposes read-only catalog state until a write action exists.
