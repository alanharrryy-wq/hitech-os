# Tablet POS Permissions

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

Roles PC de gobierno externo, no requeridos para venta local Tablet:

- `pc_backoffice`
- `pc_admin`

## Implementation guardrails

- `POST /api/pos/sales/complete` returns audit-shaped metadata for `pos.sale.complete`.
- Local export routes return JSON audit metadata and CSV audit headers for `export.local.create`.
- Offline local sale/export is allowed; actorId remains required in the event envelope or audit metadata.
