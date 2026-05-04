# PRISMA Verticales 00F - Validation Fixtures

**Paquete:** `PRISMA_VERTICALS_ARCHITECTURE_00F_VERTICAL_VALIDATION_FIXTURES`  
**Version:** `0.0.1`  
**Estado:** arquitectura contractual instalable  
**Raiz objetivo:** `F:\repos\hitech-os\apps\terminal-de-venta-system`  
**Proposito:** cerrar la primera base multi-giro con fixtures, escenarios, smoke checks y criterios de aceptacion

> Regla de barrio: si no se puede probar, no existe. Una arquitectura sin fixtures es como alarma sin pila: presume mucho y cuida nada.


## 1. Que resuelve este bloque

`00F` convierte los contratos de `00A` a `00E` en evidencia revisable. No agrega runtime de negocio todavia. Agrega datos de prueba, escenarios, matrices de aceptacion y un validador para que cualquier siguiente vertical pueda demostrar que cumple el contrato antes de tocar UI, API o base de datos.

Sin este bloque, PRISMA tendria documentos elegantes, que es muy bonito hasta que el primer restaurante pida mesas y la farmacia pida lotes. Con este bloque, cada vertical queda obligado a declarar que pantallas usa, que flujos cubre, que eventos genera, que permisos necesita y como se comporta offline.

## 2. Capas que valida

| Capa | Que valida |
|---|---|
| Core contracts | Que el nucleo comun no se llene de reglas por giro |
| Vertical registry | Que cada giro exista y tenga identidad unica |
| Data models | Que los datos verticales no invadan entidades core |
| Events and permissions | Que dinero, inventario y acciones sensibles generen eventos y permisos |
| UX operations | Que pantallas y flujos tengan estados humanos y no mensajes de programador |

## 3. Principios de fixture

1. Un fixture debe representar una operacion real, no una fantasia de demo.
2. Un escenario debe incluir precondiciones, pasos, resultado esperado, eventos y permisos.
3. Cada vertical debe cubrir venta, cobro, error, offline, devolucion o cierre equivalente.
4. Las pruebas no deben depender de PC para vender cuando el modo Tablet lo permite.
5. Las pruebas deben distinguir Tablet POS de PC Backoffice.
6. Los casos sensibles deben exigir auditoria.
7. El lenguaje esperado debe ser es-MX operativo.

## Vertical `convenience` - Tienda de conveniencia

**Uso operativo:** venta rapida, barcode, ticket, stock local y turno.  
**Flujos cubiertos:** quick_sale, barcode_sale, cash_change, return_ticket, shift_close, offline_sale.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Existencias, Producto no encontrado, Devoluciones.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `restaurant` - Restaurante / cafeteria

**Uso operativo:** mesas, comandas, cocina, cuenta abierta y propina.  
**Flujos cubiertos:** open_table, send_to_kitchen, split_bill, cash_change, table_close, offline_order.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Mesas, Comandas, Cocina, Cuenta.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `pharmacy` - Farmacia

**Uso operativo:** lotes, caducidad, receta, producto sensible y devolucion controlada.  
**Flujos cubiertos:** barcode_sale, lot_expiry_check, prescription_gate, sensitive_return, cash_change, offline_limited_sale.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Producto sensible, Receta, Lotes y caducidad.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `beauty` - Estetica / barberia

**Uso operativo:** agenda, servicios, comisiones, cliente recurrente y cobro de servicio.  
**Flujos cubiertos:** book_appointment, sell_service, assign_staff, commission_capture, cash_change, reschedule.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Agenda, Servicios, Colaborador, Cliente.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `hardware` - Ferreteria

**Uso operativo:** unidades variables, cotizacion, precio por medida y venta asistida.  
**Flujos cubiertos:** quote_create, measure_sale, stock_check, cash_change, partial_return, offline_quote.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Cotizaciones, Unidades de medida, Existencias asistidas.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `apparel` - Ropa / boutique

**Uso operativo:** variantes, tallas, colores, cambios y disponibilidad.  
**Flujos cubiertos:** variant_lookup, size_color_sale, exchange_flow, cash_change, stock_check, return_ticket.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Variantes, Cambios, Disponibilidad por talla.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `repair` - Taller / reparacion

**Uso operativo:** orden de trabajo, refacciones, mano de obra y entrega.  
**Flujos cubiertos:** work_order_create, parts_add, labor_add, deposit_payment, delivery_close, offline_intake.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Orden de trabajo, Refacciones, Entrega.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `field_route` - Venta en ruta / campo

**Uso operativo:** ruta, visita, preventa, entrega y offline fuerte.  
**Flujos cubiertos:** route_start, customer_visit, preorder_capture, delivery_confirm, cash_collection, offline_sync_later.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Ruta, Cliente de ruta, Entrega, Cobranza.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `grocery_scale` - Abarrotes con bascula

**Uso operativo:** pesaje, precio por kilo, etiqueta y merma ligera.  
**Flujos cubiertos:** weighed_item_sale, label_scan, manual_weight_capture, cash_change, stock_adjust_light, offline_scale_sale.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Bascula, Pesaje, Etiqueta.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## Vertical `food_truck` - Food truck / punto movil

**Uso operativo:** menu corto, flujo rapido, propina opcional y offline.  
**Flujos cubiertos:** menu_sale, combo_sale, rush_order, cash_change, close_shift, offline_sale.  
**Pantallas cubiertas:** Vender, Cobro, Ticket actual, Ventas de hoy, Turno, Sincronizacion, Menu, Orden rapida, Cierre movil.  
**Objetivo de prueba:** confirmar que el vertical puede operar sin contaminar el nucleo comun, respetando Tablet como POS y PC como gobierno pesado.

### Criterio minimo

- El cajero puede completar el flujo principal sin lenguaje tecnico.
- Las acciones sensibles piden permiso o confirmacion.
- Los estados `empty`, `error`, `offline`, `sync_pending` y `success` tienen salida visible.
- Todo flujo que afecte dinero, inventario, turno o cliente produce evento auditable.
- El vertical no mete backoffice completo dentro de Tablet.

## 4. Resultado esperado

Despues de instalar este paquete, el repo contiene una base contractual para construir pruebas reales por vertical. La validacion local debe responder algo como:

```text
OK vertical validation fixtures: 10 verticals, 60 scenarios, 490 acceptance checks validated
VERIFY OK
```

La cifra exacta puede crecer en paquetes posteriores, pero el principio no cambia: cada vertical nuevo entra con evidencia, no con puro entusiasmo de junta.
