# PRISMA Tablet POS Standalone Core 01A - Engine

Este directorio contiene el motor local de venta para Tablet. No dibuja pantallas, no expone rutas HTTP y no intenta resolver backoffice. Su trabajo es más sencillo y más serio: cerrar una venta local de forma transaccional, descontar stock, registrar movimientos y dejar eventos en outbox.

## Contrato operativo

Entrada pública inicial:

- `posEngineRepository.completeLocalSale(input)`

Responsabilidades:

- resolver productos por `productId`, `sku` o `barcode`
- validar cantidades
- validar producto activo
- validar stock cuando `allowNegativeStock` sea `false`
- crear `Sale`
- crear `SaleLine`
- descontar `Product.stockOnHand`
- crear `StockMovement`
- crear `OutboxEvent`
- devolver folio, líneas, total y eventos generados

No responsabilidades:

- UI
- rutas API
- impresión de ticket
- métodos de pago complejos
- facturación
- sync remoto
- multi-sucursal administrado

## Eventos locales generados

- `sale.created`
- `sale.completed`
- `ticket.closed`
- `stock.decremented`
- `inventory.low_stock_detected` cuando el stock resultante queda bajo el umbral configurado.

## Motivo del diseño

Tablet debe poder vender sin PC. Este motor es la primera pieza de esa autonomía. PC podrá gobernar después, pero no debe ser requisito para cerrar una venta local.
