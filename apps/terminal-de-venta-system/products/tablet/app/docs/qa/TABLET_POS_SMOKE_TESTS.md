# Tablet POS Smoke Tests

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

Smoke tests esperados para la siguiente etapa de codigo POS standalone.


- `tablet-db-init` crea/usa `data/tablet-pos.db`.
- `tablet-dev` abre Tablet sin PC.
- `GET /api/pos/products/search?q=` responde con contrato `ok`.
- `GET /api/pos/products/resolve?code=` resuelve SKU/codigo.
- `POST /api/pos/sales/complete` completa venta valida.
- Stock decrementa y `StockMovement` se crea.
- `OutboxEvent` queda en `pending` si no hay sync.
- Export JSON/CSV entrega ventas, eventos y movimientos.
- Error visible aparece para carrito vacio, producto inactivo y stock insuficiente.

Typecheck: `pnpm -C F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app run typecheck`.
