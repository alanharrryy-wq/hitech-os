# PRISMA Arquitectura Final PC + Tablet

Este documento prevalece sobre documentos anteriores que describan Tablet como consola subordinada, complemento, lujo, pantalla secundaria o app dependiente de PC para vender.

Este documento reemplaza cualquier descripcion anterior donde Tablet dependa de PC para vender.

Regla madre:

Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.

## 1. Decision de producto

PRISMA queda definido como tres capas vendibles y combinables:

- Tablet POS standalone para venta local.
- PC Backoffice para gobierno, auditoria y consolidacion avanzada.
- PC + Tablet para operaciones managed con sincronizacion y reconciliacion.

La Tablet no es lujo, espejo, pantalla secundaria ni terminal subordinada. Es el POS operativo que debe poder vender por si solo con DB local, catalogo local, tickets, decremento de stock, eventos, outbox, exportaciones, reportes y continuidad offline.

## 2. Tablet POS standalone

Tablet debe vender, buscar productos, resolver codigo de barras/SKU, construir ticket, cerrar ticket, cobrar con metodo basico, decrementar stock, registrar movimientos, registrar eventos, consultar resumen del dia, exportar datos y sincronizar despues si aplica.

Ruta canonica local de DB Tablet: `products/tablet/app/data/tablet-pos.db`.
Fallback Prisma: `file:./data/tablet-pos.db`.

Variables de runtime Tablet:

- `TABLET_DATABASE_URL`
- `TABLET_RUNTIME_MODE`

## 3. PC Backoffice/gobierno

PC es panel administrativo y de gobierno. PC puede definir politicas, publicar catalogos, recibir eventos, reconciliar conflictos, auditar ventas y consolidar informacion. PC no es permiso para vender localmente en Tablet.

PC no debe ser requerido para venta basica local, ticket local, decremento local de stock, reporte local del dia ni export local.

## 4. Runtime modes

### `standalone`

Tablet operates with local DB and exports data.
PC required: no.
Internet required: no.

### `managed`

Tablet syncs with PC/backoffice.
PC required: yes for governance/sync.
Internet/network: intermittent or stable.

### `degraded_managed`

Tablet belongs to a managed operation, but keeps selling if PC/network goes down.
PC required: yes for governance, no for basic sales.
Internet required: no for basic sales.

Reglas obligatorias:

- Tablet must never block basic sale because PC is absent.
- If sync fails, allowed local sale continues.
- Sensitive operations are marked.
- Events go to outbox.
- PC resolves conflicts later.
- Tablet commands must not validate PC existence for Tablet tasks.
- Do not depend on tools/_local/data/terminal-de-venta-system/canonical.db for selling.
- Do not use cwd as trusted root.
- Do not invent magic DB paths.

## 5. Local Tablet DB

SQLite local es autonomia Tablet. No es cache secundaria ni espejo fragil. La DB local cubre minimo: `Business`, `Terminal`, `Product`, `Barcode`, `Sale`, `SaleLine`, `StockMovement`, `OutboxEvent`, `CashSession`.

En UI y operacion puede llamarse turno/shift, pero en schema y tooling el nombre canonico es `CashSession`.

## 6. Tablet APIs

APIs minimas:

- `GET  /api/pos/products/search?q=`
- `GET  /api/pos/products/resolve?code=`
- `POST /api/pos/sales/complete`
- `GET  /api/pos/sales/today`

APIs de trazabilidad/export:

- `GET /api/pos/events/recent`
- `GET /api/pos/events/outbox`
- `GET /api/pos/inventory/low-stock`
- `GET /api/pos/inventory/movements/recent`
- `GET /api/pos/reports/operational-today`
- `GET /api/pos/export/sales-today?format=json|csv`
- `GET /api/pos/export/events?format=json|csv`
- `GET /api/pos/export/inventory-movements?format=json|csv`

Todas deben responder con contrato `ok/data/meta` o `ok/code/message/details`.

## 7. Responsabilidades PC

Modulos objetivo PC: `catalog`, `stock`, `counts`, `purchasing`, `receiving`, `replenishment`, `audit`, `sync`, `dashboard`, `settings`.

PC sirve catalogo completo, control SKU/codigo, stock por ubicacion, movimientos, conteos fisicos, compras, recepcion, reabasto, auditoria, dashboard ejecutivo, sync/reconciliacion y control multi-sucursal/multi-terminal.

## 8. Shared Kernel boundaries

Shared Kernel no es carpeta de utilerias. Shared Kernel es contrato.

Puede contener tipos compartidos reales, event names, sync contracts, screen contracts, plugin contracts, glosario compartido y reglas de compatibilidad.

No debe contener helpers locales de Tablet, helpers locales de PC, UI especifica, queries especificas, logica backoffice, logica touch POS ni parches temporales.

Sensitive zones:

- `packages/shared-kernel/*`
- `shared/TWIN_CHAT_SHARED_CONTEXT_6.1.json`
- `shared/contracts/*`
- visible equivalent labels
- shared event names
- sync contracts

Regla twin: si cambia identidad compartida, naming compartido, eventos compartidos o contrato sync, es twin change. Si solo mejora operacion local Tablet o PC, es local.

## 9. Local Tablet data model

## Entidades minimas

- `Business`
- `Terminal`
- `Product`
- `Barcode`
- `Sale`
- `SaleLine`
- `StockMovement`
- `OutboxEvent`
- `CashSession`

## `Product`

- `id`
- `businessId`
- `sku`
- `name`
- `barcode`
- `priceCents`
- `stockOnHand`
- `lowStockThreshold`
- `isActive`
- `createdAt`
- `updatedAt`

## `Sale`

- `id`
- `businessId`
- `terminalId`
- `operatorId`
- `cashSessionId`
- `ticketNumber`
- `status`
- `subtotalCents`
- `discountCents`
- `totalCents`
- `paymentMethod`
- `createdAt`
- `completedAt`

## `SaleLine`

- `id`
- `saleId`
- `productId`
- `sku`
- `name`
- `qty`
- `unitPriceCents`
- `totalCents`

## `StockMovement`

- `id`
- `businessId`
- `productId`
- `reason`
- `quantityDelta`
- `beforeQty`
- `afterQty`
- `sourceType`
- `sourceId`
- `createdAt`

## `OutboxEvent`

- `id`
- `businessId`
- `terminalId`
- `topic`
- `payloadJson`
- `status`
- `attempts`
- `createdAt`
- `syncedAt`

## 10. Event model

Eventos POS minimos:

- `sale.created`
- `sale.completed`
- `ticket.closed`
- `stock.decremented`
- `inventory.low_stock_detected`

Eventos posteriores:

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

Todo evento sensible debe incluir `eventId`, `topic`, `businessId`, `terminalId`, `actorId`, `source`, `occurredAt`, `payload`, `schemaVersion`.

Regla de oro: si afecta dinero, inventario, cliente, caja, pedido, membresia, datos fiscales o produccion, debe generar evento.

## 11. Sync and reconciliation

Objetivo: permitir que Tablet opere sin PC/red y que PC consolide despues.

Flujo basico:

1. Tablet ejecuta venta.
2. Escribe `Sale`, `SaleLine`, `StockMovement`.
3. Crea `OutboxEvent`.
4. Si sync esta disponible, envia eventos.
5. PC ingesta eventos.
6. PC valida contrato.
7. PC actualiza vista consolidada.
8. PC marca eventos recibidos.
9. Si hay conflicto, PC resuelve.

Estados outbox: `pending`, `sent`, `failed`, `acked`, `conflict`.

Conflictos posibles: producto discontinuado, precio local viejo, stock local negativo, evento duplicado, terminal no registrada, venta fuera de turno, secuencia inconsistente.

Offline no significa permiso para todo. Ventas con catalogo local activo, tickets locales, cortes locales, export local y consulta local son permitidos. Cambios masivos de precio, alta avanzada de productos, ajustes grandes, devoluciones sensibles, cambios de permisos y operaciones multi-sucursal pueden bloquearse offline.

## 12. Permission/audit model

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

Toda accion sensible debe registrar `actorId`, `role`, `terminalId`, `businessId`, `action`, `entityType`, `entityId`, `before`, `after`, `createdAt`.

## 13. API response format

Success:

```json
{
  "ok": true,
  "data": {},
  "meta": {}
}
```

Error:

```json
{
  "ok": false,
  "code": "INSUFFICIENT_STOCK",
  "message": "Stock insuficiente para este producto.",
  "details": {}
}
```

Errores canonicos POS:

- `EMPTY_CART`
- `INVALID_QUANTITY`
- `PRODUCT_NOT_FOUND`
- `PRODUCT_INACTIVE`
- `INSUFFICIENT_STOCK`
- `TERMINAL_NOT_FOUND`
- `NETWORK_UNAVAILABLE`
- `SYNC_PENDING`

## 14. UI states

Estados canonicos:

- `idle`
- `loading`
- `ready`
- `empty`
- `error`
- `offline`
- `sync_pending`
- `sync_failed`
- `success`

Ningun flujo operativo puede quedar silencioso ante error, conflicto, offline state o sync failure.

Tablet debe definir estados visuales para busqueda de producto, codigo de barras/SKU, ticket, cierre de venta, metodo de pago, decremento de stock, outbox, reporte diario, export, runtime offline/degradado, sync pending y sync failed.

PC debe definir estados visuales para dashboard, catalogo, stock, movimientos, conteos, compras, recepcion, reabasto, auditoria, sync ingest y conflictos.

## 15. QA acceptance

Tablet acceptance: init DB local, correr sin PC, buscar producto, resolver SKU/codigo, armar ticket, completar venta, decrementar stock, crear movimiento, crear evento/outbox, mostrar resumen diario, exportar ventas/eventos/movimientos, mostrar errores visibles, operar offline y pasar typecheck.

PC acceptance: mostrar catalogo, stock, movimientos, conteos, compras, recepcion, reabasto, auditoria, dashboard, ingestar evento Tablet, marcar conflicto, consolidar venta y no bloquear venta local Tablet.

Integration acceptance: Tablet vende standalone, crea outbox, PC ingesta evento, PC consolida venta, PC detecta conflicto, Tablet sigue vendiendo si PC cae y sync no rompe ventas locales.

## 16. Roadmap

1. `PRISMA_TABLET_POS_STANDALONE_FULL_ENGINE_01`
2. `PRISMA_TABLET_POS_TOUCH_UI_FULL_02`
3. `PRISMA_PC_BACKOFFICE_SYNC_DASHBOARD_03`

Este documento no implementa esas etapas. Solo deja el repo listo para codificarlas.

## 17. Anti-chaos rules

- No subordinar Tablet a PC.
- No hacer que PC autorice ventas basicas locales.
- No convertir Shared Kernel en basurero de helpers.
- No usar `tools/_local/data/terminal-de-venta-system/canonical.db` como requisito para venta Tablet.
- No confiar en cwd para resolver raices.
- No inventar rutas magicas de DB.
- No prometer implementacion que no exista.
- Todo cambio relevante debe ser reversible, verificable y documentado.
