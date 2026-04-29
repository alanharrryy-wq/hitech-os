# Data Model Tablet Local

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

Define el modelo minimo de DB local que permite autonomia POS Tablet.


SQLite local DB is Tablet autonomy.

## Entidades minimas

- `Business`
- `Terminal`
- `Product`
- `Barcode`
- `Sale`
- `SaleLine`
- `StockMovement`
- `OutboxEvent`
- `CashSession` (operator-facing shift/turno)

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
