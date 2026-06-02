<!-- Generated from ATLAS_CHAT_SHARED_CORE.zip on 2026-05-08. Do not treat this as source code. -->


# ATLAS_SHARED_CORE_CONTRACTS

Estado: atlas inicial mejorado.
Alcance: contratos compartidos confirmados por `shared/contracts/**`, `docs/contracts/**`, `docs/architecture/**` y contratos verticales.

## Resumen

Los contratos de Shared Core definen cómo hablan las superficies, no cómo se ve una pantalla ni cómo se implementa un flujo local. Son el reglamento del partido: si Tablet mete gol, PC no puede decir que era básquet porque leyó otro papel.

## Índice contractual

| Dominio | Fuente canónica o principal | Fuente machine-readable | Certeza | Notas |
|---|---|---|---|---|
| API response | `docs/contracts/API_RESPONSE_CONTRACT.md`, `shared/contracts/api-response-contract.md` | Pendiente si existe tipo único compilable | Confirmado | Envelope `{ok,data,meta}` y `{ok,code,message,details}`. |
| Errors | `docs/contracts/ERRORS_CONTRACT.md`, `shared/contracts/error-contract.md` | Pendiente | Confirmado | Debe alinearse con errores POS canónicos. |
| Events/sync | `docs/contracts/EVENT_CONTRACT.md`, `shared/contracts/event-contract.md` | `shared/contracts/sync-event-contract.v1.json` | Confirmado | Fuente machine-readable para topics, outbox states, conflict codes y envelope. |
| Sync reconciliation | `docs/contracts/SYNC_RECONCILIATION_CONTRACT.md`, `shared/contracts/sync-contract.md` | `shared/contracts/sync-event-contract.v1.json` | Confirmado | Offline permite venta local, no todo. |
| Permissions/audit | `docs/contracts/PERMISSIONS_AUDIT_CONTRACT.md`, `shared/contracts/permission-contract.md` | `shared/contracts/security-audit-permissions.v1.json` | Confirmado | Distingue Tablet Solo, Tablet Pro y Tablet+PC. |
| UI state | `docs/contracts/UI_STATE_CONTRACT.md`, `shared/contracts/ui-state-contract.md` | Pendiente | Confirmado | Estados visibles: idle, loading, ready, empty, error, offline, sync_pending, sync_failed, success. |
| Schema compatibility | `docs/architecture/PRISMA_SCHEMA_OWNERSHIP.md`, `shared/contracts/schema-compatibility-contract.md` | `prisma/schema.prisma` y vertical data model JSON | Confirmado con divergencia | Hay divergencia `CashSession` vs `Shift`; marcar para normalización. |
| Screen contracts | `shared/contracts/screen-contract.md` | Pendiente | Confirmado | Alinear pantallas sin absorber UI específica. |
| UI governance contracts | `shared/contracts/ui/*.json` | JSONs en `shared/contracts/ui/**` | Confirmado | Gobernanza Visual OS/tri-surface. |
| Vertical contracts | `shared/contracts/verticals/**` | JSON schemas/contracts verticales | Confirmado | Define registry, profiles, events, permissions, UX, validation fixtures. |

## Contrato API

### Canon confirmado

- Success format: `{ "ok": true, "data": {}, "meta": {} }`.
- Error format: `{ "ok": false, "code": "INSUFFICIENT_STOCK", "message": "Stock insuficiente para este producto.", "details": {} }`.
- APIs mínimas POS documentadas: búsqueda de productos, resolve por código, completar venta y ventas del día.
- APIs de trazabilidad/export documentadas: events recent/outbox, low stock, inventory movements, operational today, exports JSON/CSV.
- Errores POS canónicos confirmados: `EMPTY_CART`, `INVALID_QUANTITY`, `PRODUCT_NOT_FOUND`, `PRODUCT_INACTIVE`, `INSUFFICIENT_STOCK`, `TERMINAL_NOT_FOUND`, `NETWORK_UNAVAILABLE`, `SYNC_PENDING`.

### Cambio seguro

1. Actualizar contrato Markdown y, si existe, tipo machine-readable.
2. Revisar consumidores por dependencia cruzada.
3. Mantener compatibilidad de `ok`, `code`, `message`, `details`.
4. Agregar errores nuevos sin renombrar códigos existentes salvo migración explícita.
5. Verificar UI states de error/offline/sync failure.

## Contrato de eventos y sync

### Topics mínimos confirmados

| Grupo | Topics |
|---|---|
| Venta/ticket | `sale.created`, `sale.completed`, `ticket.closed` |
| Stock | `stock.decremented`, `inventory.low_stock_detected`, futuro `stock.adjusted` |
| Sync | `sync.event.sent`, `sync.event.failed`, `sync.conflict.detected`, `sync.conflict.resolved` |
| Catálogo | `catalog.product.created`, `catalog.product.updated` |
| Turno/caja | `shift.opened`, `shift.closed` |

### Envelope sensible obligatorio

Todo evento sensible debe incluir:

```text
eventId, topic, businessId, terminalId, actorId, source, occurredAt, payload, schemaVersion
```

### Outbox states confirmados

```text
pending, sent, failed, acked, conflict
```

### Conflict codes canónicos

```text
product_discontinued, old_local_price, negative_stock, duplicate_event,
terminal_not_registered, sale_outside_shift, inconsistent_sequence,
invalid_schema, unknown_topic
```

### Regla de oro

Si afecta dinero, inventario, cliente, caja, pedido, membresía, fiscal o producción, debe generar evento. Si no genera evento, luego la auditoría queda como policía sin libreta.

## Contrato de sync reconciliation

Flujo básico confirmado:

```text
Tablet executes sale
-> writes Sale/SaleLine/StockMovement
-> creates OutboxEvent
-> sends if sync available
-> PC ingests events
-> PC validates contract
-> PC updates consolidated view
-> PC marks events received
-> PC resolves conflicts if needed
```

### Offline permitido

- Ventas con catálogo local activo.
- Tickets locales.
- Cortes locales de turno/día.
- Export local.
- Consulta local de datos.

### Offline bloqueable

- Cambios masivos de precio.
- Creación avanzada de productos.
- Ajustes grandes de inventario.
- Devoluciones sensibles.
- Cambios de permisos.
- Operaciones multi-sucursal.

## Permisos y auditoría

| Plan/contexto | Permisos/documentación confirmada |
|---|---|
| Tablet Solo | `pos.sale.create`, `pos.sale.complete`, `pos.ticket.view`, `inventory.local.view`, `report.today.view`, `export.local.create` |
| Tablet Pro | `pos.sale.cancel`, `pos.return.create`, `inventory.local.adjust`, `shift.open`, `shift.close`, `event.outbox.view` |
| Tablet + PC | `catalog.write`, `price.write`, `inventory.adjust.approve`, `purchase.write`, `receiving.write`, `audit.view`, `sync.conflict.resolve`, `user.permission.manage` |

Toda acción sensible debe registrar:

```text
actorId, role, terminalId, businessId, action, entityType, entityId, before, after, createdAt
```

Roles mínimos: `tablet_operator`, `tablet_supervisor`, `pc_backoffice`, `pc_admin`.

## Schema compatibility

### Regla confirmada

Prisma ORM ayuda a ordenar datos, pero no reemplaza arquitectura ni contratos.

### Schemas permitidos

1. Root/backoffice canonical schema: PC/backoffice, consolidación, inventory avanzado, compras, receiving, audit y sync.
2. Tablet local schema: POS standalone mínimo.

### Modelos Prisma root detectados

El snapshot contiene 23 modelos Prisma:

```text
Business, Store, Terminal, TaxRate, PriceList, PriceListItem, Product, Barcode, StockSnapshot, StockMovement, Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine, ReplenishmentSignal, CashSession, CashMovement, Sale, SaleLine, SaleReturn, AuditCount, OutboxEvent
```

### Divergencia que debe resolverse

- `PRISMA_SCHEMA_OWNERSHIP.md` dice que el nombre canónico de datos es `CashSession` aunque UI pueda decir turno/shift.
- `shared/contracts/schema-compatibility-contract.md` enumera `Shift` en el mínimo Tablet.
- `prisma/schema.prisma` contiene `CashSession`, no `Shift`.

Conclusión: usar `CashSession` como evidencia de implementación actual y marcar normalización documental `Shift` vs `CashSession` como pendiente.

## Vertical contracts

### Registro confirmado

`shared/verticals/registry/vertical-registry.v0.json` declara 10 verticales:

```text
convenience, restaurant, pharmacy, beauty, hardware, apparel, repair, field_route, grocery_scale, food_truck
```

Reglas confirmadas del registry:

- Un negocio declara vertical principal.
- Navegación visible sale del vertical activo, capacidades y permisos.
- Capacidades bloqueadas no se exponen en Tablet.
- Eventos verticales usan namespace.
- PC gobierna configuración profunda; Tablet opera caja.

### Archivos clave

| Tipo | Rutas |
|---|---|
| Schemas contract | `shared/contracts/verticals/*.json` |
| Registry | `shared/verticals/registry/**` |
| Profiles | `shared/verticals/registry/profiles/*.vertical-profile.json` |
| Data model/extensions | `shared/verticals/data-models/**` |
| Events | `shared/verticals/events/**` |
| Permissions | `shared/verticals/permissions/**` |
| UX operation | `shared/verticals/ux/**` |
| Validation | `shared/verticals/validation/**` |
| Validators | `tools/verticals/validate_vertical_*` |

## Regla twin change

Según `packages/shared-kernel/README.md` y `SHARED_KERNEL_CONTRACT.md`:

- Si cambia identidad compartida, naming compartido, eventos compartidos o sync contract, es twin change.
- Si solo mejora operación local Tablet o PC, es local.

## Zonas sensibles

```text
packages/shared-kernel/**
shared/twin-kernel/**
shared/contracts/**
shared/contracts/sync-event-contract.v1.json
shared/contracts/security-audit-permissions.v1.json
shared/contracts/verticals/**
prisma/schema.prisma
prisma/migrations/**
```

## Verificación contractual recomendada

| Cambio | Verificación mínima |
|---|---|
| Eventos/sync | Validar `sync-event-contract.v1.json`, revisar outbox states/conflict codes, correr validators verticales si toca vertical events. |
| Permisos | Validar `security-audit-permissions.v1.json`, revisar audit metadata y roles mínimos. |
| API/errors | Revisar consumidores y estados UI; mantener envelope estable. |
| Schema | Revisar `PRISMA_SCHEMA_OWNERSHIP.md`, migración, seed, smoke, rollback y docs. |
| Vertical | Correr `tools/verticals/validate_vertical_contracts_00a.py` a `00f.py` según bloque. |
| UI state | Revisar que error, conflict, offline y sync failure nunca sean silenciosos. |

## Rollback contractual

- Nunca renombrar topics o permisos sin alias/migración explícita.
- Restaurar contrato machine-readable previo si falla validación.
- Si un cambio rompe Tablet standalone, revertir antes de intentar ajuste cosmético.
- Para schema, rollback requiere backup/migración inversa; no borrar columnas o datos a mano.

## Pendientes

1. Confirmar fuente machine-readable única para API response/errors/UI state si existe fuera del ZIP.
2. Normalizar `CashSession` vs `Shift` en contratos y vertical catalogs.
3. Confirmar si aliases deprecated de eventos siguen aceptados en ingest o sólo documentados para migración.
4. Confirmar ownership final de cada contrato por chat/equipo.
