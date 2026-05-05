# Shared API Response Contract

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

Normaliza respuestas para API Tablet POS y futuras rutas PC/sync.


## Success format

```json
{ "ok": true, "data": {}, "meta": {} }
```

## Error format

```json
{ "ok": false, "code": "INSUFFICIENT_STOCK", "message": "Stock insuficiente para este producto.", "details": {} }
```

## Tablet minimum APIs

- `GET  /api/pos/products/search?q=`
- `GET  /api/pos/products/resolve?code=`
- `POST /api/pos/sales/complete`
- `GET  /api/pos/sales/today`

## Traceability/export APIs

- `GET /api/pos/events/recent`
- `GET /api/pos/events/outbox`
- `GET /api/pos/inventory/low-stock`
- `GET /api/pos/inventory/movements/recent`
- `GET /api/pos/reports/operational-today`
- `GET /api/pos/export/sales-today?format=json|csv`
- `GET /api/pos/export/events?format=json|csv`
- `GET /api/pos/export/inventory-movements?format=json|csv`

## Canonical POS errors

- `EMPTY_CART`
- `INVALID_QUANTITY`
- `PRODUCT_NOT_FOUND`
- `PRODUCT_INACTIVE`
- `INSUFFICIENT_STOCK`
- `TERMINAL_NOT_FOUND`
- `NETWORK_UNAVAILABLE`
- `SYNC_PENDING`
