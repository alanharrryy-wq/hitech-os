# PRISMA 00D - Catalogo de eventos por vertical

Este catalogo define nombres, significado operativo, emisor, consumidor, sensibilidad, modo offline y microcopy sugerida para eventos.

## Eventos core
### `sale.created`

- Descripcion: Se crea una venta local o administrada.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `sale.created`.

### `sale.completed`

- Descripcion: Se completa una venta y queda lista para ticket.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `sale.completed`.

### `ticket.closed`

- Descripcion: Se cierra el ticket visible del cliente.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `ticket.closed`.

### `payment.received`

- Descripcion: Se registra pago recibido.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `payment.received`.

### `payment.failed`

- Descripcion: Fallo un intento de pago.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `payment.failed`.

### `return.created`

- Descripcion: Se inicia una devolucion.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `return.created`.

### `return.completed`

- Descripcion: Se completa una devolucion.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `return.completed`.

### `shift.opened`

- Descripcion: Se abre turno de caja.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `shift.opened`.

### `shift.closed`

- Descripcion: Se cierra turno de caja.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `shift.closed`.

### `stock.decremented`

- Descripcion: Se descuenta existencia por venta.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `stock.decremented`.

### `stock.adjusted`

- Descripcion: Se ajusta inventario local o administrado.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `stock.adjusted`.

### `sync.event.pending`

- Descripcion: Un evento queda pendiente por enviar.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `sync.event.pending`.

### `sync.event.sent`

- Descripcion: Un evento fue enviado.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `sync.event.sent`.

### `sync.event.failed`

- Descripcion: Fallo el envio de un evento.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `sync.event.failed`.

### `sync.conflict.detected`

- Descripcion: Se detecto conflicto de sincronizacion.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `sync.conflict.detected`.

### `catalog.product.created`

- Descripcion: Se crea producto basico.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `catalog.product.created`.

### `catalog.product.updated`

- Descripcion: Se actualiza producto.
- Emisor: Tablet o PC, segun flujo.
- Consumidor: auditoria, sync, reportes y reconciliacion.
- Offline: permitido si la operacion local esta permitida.
- Mensaje visible recomendado: texto de negocio, nunca `catalog.product.updated`.

## Eventos verticales
## Tienda de conveniencia (`convenience`)
### `convenience.barcode.scanned`

- Caso: evento 1 del giro Tienda de conveniencia.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `convenience.cash.drawer.counted`

- Caso: evento 2 del giro Tienda de conveniencia.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `convenience.low_stock.flagged`

- Caso: evento 3 del giro Tienda de conveniencia.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `convenience.age_restricted.item.blocked`

- Caso: evento 4 del giro Tienda de conveniencia.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Restaurante o cafeteria (`restaurant`)
### `restaurant.table.opened`

- Caso: evento 1 del giro Restaurante o cafeteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `restaurant.table.moved`

- Caso: evento 2 del giro Restaurante o cafeteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `restaurant.kitchen.order.sent`

- Caso: evento 3 del giro Restaurante o cafeteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `restaurant.kitchen.item.voided`

- Caso: evento 4 del giro Restaurante o cafeteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `restaurant.tip.added`

- Caso: evento 5 del giro Restaurante o cafeteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Farmacia (`pharmacy`)
### `pharmacy.lot.selected`

- Caso: evento 1 del giro Farmacia.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `pharmacy.expiration.alerted`

- Caso: evento 2 del giro Farmacia.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `pharmacy.prescription.checked`

- Caso: evento 3 del giro Farmacia.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `pharmacy.restricted.item.blocked`

- Caso: evento 4 del giro Farmacia.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Estetica, barberia o salon (`beauty`)
### `beauty.appointment.created`

- Caso: evento 1 del giro Estetica, barberia o salon.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `beauty.appointment.checked_in`

- Caso: evento 2 del giro Estetica, barberia o salon.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `beauty.service.completed`

- Caso: evento 3 del giro Estetica, barberia o salon.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `beauty.commission.accrued`

- Caso: evento 4 del giro Estetica, barberia o salon.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Ferreteria (`hardware`)
### `hardware.quote.created`

- Caso: evento 1 del giro Ferreteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `hardware.quote.converted`

- Caso: evento 2 del giro Ferreteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `hardware.unit.measure.changed`

- Caso: evento 3 del giro Ferreteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `hardware.bulk.price.applied`

- Caso: evento 4 del giro Ferreteria.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Ropa o boutique (`apparel`)
### `apparel.variant.selected`

- Caso: evento 1 del giro Ropa o boutique.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `apparel.exchange.created`

- Caso: evento 2 del giro Ropa o boutique.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `apparel.size.unavailable`

- Caso: evento 3 del giro Ropa o boutique.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `apparel.color.changed`

- Caso: evento 4 del giro Ropa o boutique.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Taller o reparaciones (`repair`)
### `repair.work_order.opened`

- Caso: evento 1 del giro Taller o reparaciones.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `repair.part.consumed`

- Caso: evento 2 del giro Taller o reparaciones.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `repair.labor.added`

- Caso: evento 3 del giro Taller o reparaciones.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `repair.customer.approved`

- Caso: evento 4 del giro Taller o reparaciones.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Venta en campo o ruta (`field_route`)
### `field_route.route.started`

- Caso: evento 1 del giro Venta en campo o ruta.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `field_route.visit.completed`

- Caso: evento 2 del giro Venta en campo o ruta.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `field_route.preorder.created`

- Caso: evento 3 del giro Venta en campo o ruta.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `field_route.cash.collected`

- Caso: evento 4 del giro Venta en campo o ruta.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Abarrotes con bascula (`grocery_scale`)
### `grocery_scale.scale.weight.captured`

- Caso: evento 1 del giro Abarrotes con bascula.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `grocery_scale.weighted.item.added`

- Caso: evento 2 del giro Abarrotes con bascula.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `grocery_scale.tare.applied`

- Caso: evento 3 del giro Abarrotes con bascula.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `grocery_scale.price.lookup.used`

- Caso: evento 4 del giro Abarrotes con bascula.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

## Food truck o punto movil (`food_truck`)
### `food_truck.menu.item.sold`

- Caso: evento 1 del giro Food truck o punto movil.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `food_truck.combo.created`

- Caso: evento 2 del giro Food truck o punto movil.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `food_truck.daily.menu.updated`

- Caso: evento 3 del giro Food truck o punto movil.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.

### `food_truck.mobile.close.created`

- Caso: evento 4 del giro Food truck o punto movil.
- Razon: registrar una accion especifica del giro sin contaminar el core.
- Requiere permiso: si afecta dinero, inventario, cliente o turno.
- Auditoria minima: actor, terminal, negocio, entidad, antes, despues, fecha.
- Offline: depende de `vertical-sync-policy.v0.json`.
