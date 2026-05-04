# PRISMA_VERTICALS_00C_CORE_DATA_BOUNDARIES

## Proposito

Definir que datos pertenecen al nucleo comun y cuales deben ir a extensiones verticales.

## Core permitido

| Core | Permitido | No permitido |
|---|---|---|
| Product | articulo fisico base, precio, sku, barcode, stock simple | receta, mesa, cita, talla/color fija, tecnico, ruta |
| Sale | ticket, total, turno, terminal, operador, pago | cocina, silla, lote medico, ruta de entrega detallada |
| SaleLine | item cobrado, cantidad, precio, referencia vendible | datos especializados como columnas permanentes |
| Payment | metodo, monto, referencia, estado | conciliacion bancaria avanzada universal |
| StockMovement | entrada/salida, razon, before/after | semantica de cocina, cita o reparacion |
| OutboxEvent | topic, payload versionado, estado | payload sin contrato |

## Decision

El core debe ser aburrido. Aburrido en arquitectura es bueno. Emocionante dejalo para el cliente que compra pan dulce a las 10 pm.

## Prueba rapida

Si el campo solo sirve a farmacia, restaurante, estetica, taller, ropa o ruta, no entra al core. Si el campo afecta dinero o inventario en cualquier giro, puede relacionarse con core mediante una extension gobernada.
