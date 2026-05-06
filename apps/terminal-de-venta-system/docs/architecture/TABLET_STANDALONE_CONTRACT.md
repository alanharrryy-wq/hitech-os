# Tablet Standalone Contract

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

Bloquea la autonomia del POS Tablet antes de implementar motores finales.


## Capacidades minimas

Tablet debe vender, buscar productos, leer barcode/SKU, construir ticket, cerrar ticket, cobrar con metodo de pago basico, decrementar stock, registrar movimientos, registrar eventos, consultar resumen del dia, exportar datos, sincronizar despues si aplica y operar offline.

## Capas internas

`UI Touch -> API Routes / Server Actions -> pos-api -> pos-engine -> Prisma Client -> SQLite local tablet-pos.db -> Outbox/Event Log`

## APIs minimas

- `GET  /api/pos/products/search?q=`
- `GET  /api/pos/products/resolve?code=`
- `POST /api/pos/sales/complete`
- `GET  /api/pos/sales/today`

## APIs de trazabilidad/export

- `GET /api/pos/events/recent`
- `GET /api/pos/events/outbox`
- `GET /api/pos/inventory/low-stock`
- `GET /api/pos/inventory/movements/recent`
- `GET /api/pos/reports/operational-today`
- `GET /api/pos/export/sales-today?format=json|csv`
- `GET /api/pos/export/events?format=json|csv`
- `GET /api/pos/export/inventory-movements?format=json|csv`

## Done criteria de la siguiente etapa de codigo

- `tablet-db-init` runs.
- Creates/uses `data/tablet-pos.db`.
- `tablet-dev` runs without PC.
- Products can be searched.
- Sale can be completed by API.
- Ticket is created.
- Stock is decremented.
- Movements are created.
- Events/outbox are created.
- Daily report updates.
- Sales/events/movements export.
- `tsc --noEmit` passes.
