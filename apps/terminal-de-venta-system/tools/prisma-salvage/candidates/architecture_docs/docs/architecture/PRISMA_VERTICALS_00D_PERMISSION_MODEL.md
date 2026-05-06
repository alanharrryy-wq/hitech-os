# PRISMA 00D - Modelo de permisos

Los permisos definen quien puede hacer que. No definen como se ve la pantalla ni reemplazan validaciones de negocio.

## Principios

1. Todo permiso debe tener namespace.
2. Todo permiso sensible debe generar auditoria cuando se usa.
3. Tablet no inventa permisos; solo los lee y bloquea acciones.
4. PC administra permisos pesados cuando el negocio es complejo.
5. Un permiso vertical solo existe si la capacidad vertical existe.

## Permisos core
- `pos.sale.create`
- `pos.sale.complete`
- `pos.ticket.view`
- `pos.ticket.cancel`
- `payment.cash.receive`
- `payment.card.confirm`
- `payment.transfer.confirm`
- `return.create`
- `return.approve`
- `shift.open`
- `shift.close`
- `shift.view`
- `inventory.local.view`
- `inventory.local.adjust`
- `catalog.product.view`
- `catalog.product.create_basic`
- `catalog.product.update_basic`
- `sync.pending.view`
- `sync.retry`
- `export.local.create`
- `audit.local.view`
- `settings.vertical.view`

## Permisos por vertical

### Tienda de conveniencia (`convenience`)
- `barcode.resolve`
- `age_restricted.override`
- `cash.drawer.recount`

### Restaurante o cafeteria (`restaurant`)
- `restaurant.table.open`
- `restaurant.table.close`
- `kitchen.order.send`
- `tip.edit`

### Farmacia (`pharmacy`)
- `pharmacy.lot.select`
- `pharmacy.prescription.confirm`
- `pharmacy.restricted.override`

### Estetica, barberia o salon (`beauty`)
- `appointment.create`
- `appointment.reschedule`
- `service.complete`
- `commission.view`

### Ferreteria (`hardware`)
- `quote.create`
- `quote.convert`
- `bulk.price.override`
- `unit.measure.sell`

### Ropa o boutique (`apparel`)
- `variant.sell`
- `exchange.create`
- `exchange.approve`
- `size.stock.view`

### Taller o reparaciones (`repair`)
- `work_order.create`
- `work_order.close`
- `repair.part.consume`
- `labor.charge`

### Venta en campo o ruta (`field_route`)
- `route.start`
- `route.close`
- `preorder.create`
- `cash.collection.confirm`

### Abarrotes con bascula (`grocery_scale`)
- `scale.weight.capture`
- `tare.apply`
- `weighted.item.sell`

### Food truck o punto movil (`food_truck`)
- `menu.item.sell`
- `combo.sell`
- `mobile.daily.close`

## Matriz base de roles

| Rol | Uso recomendado | Riesgo si se infla |
|---|---|---|
| `cashier` | vende, cobra, consulta ticket y stock operativo | si se vuelve todopoderoso, la auditoria pierde sentido |
| `supervisor` | autoriza devoluciones, ajustes pequenos y cierres | si se vuelve todopoderoso, la auditoria pierde sentido |
| `manager` | revisa operacion, permisos medios y reportes | si se vuelve todopoderoso, la auditoria pierde sentido |
| `owner` | administra politica comercial y excepciones fuertes | si se vuelve todopoderoso, la auditoria pierde sentido |
| `backoffice_admin` | configura PC, catalogo, sync y auditoria | si se vuelve todopoderoso, la auditoria pierde sentido |
| `field_operator` | vende o cobra en ruta con reglas offline | si se vuelve todopoderoso, la auditoria pierde sentido |