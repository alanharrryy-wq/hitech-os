# PRISMA Verticales 00B - Registro canonico de giros

**Paquete:** `PRISMA_VERTICALS_ARCHITECTURE_00B_VERTICAL_REGISTRY`  
**Estado:** base fundacional multi-giro  
**Idioma visible:** es-MX  
**Regla madre:** el nucleo PRISMA vende; los verticales especializan; PC gobierna; Tablet opera.

## 0. Decision principal

PRISMA no debe crecer como una sola app con cien condiciones embarradas en ventas, catalogo y checkout. Debe crecer como un nucleo comun con capacidades activables por giro. El registro de verticales es la lista oficial de giros, capacidades, navegacion, eventos, permisos y limites Tablet/PC.

Sin este registro, cada giro se vuelve excepcion. Restaurante mete mesas en venta comun, farmacia mete lotes en producto base, estetica mete citas en ticket, taller mete ordenes de trabajo en catalogo y al rato el sistema parece mochila escolar: trae todo, pero nada sale rapido.

## 1. Modelo de capas

```text
PRISMA Core
  venta, cobro, ticket, turno, devoluciones, stock basico, eventos, sync y exportacion

Vertical Registry
  declara giros y capacidades activas

Vertical Profiles
  definen navegacion, permisos, eventos y limites por giro

Tablet Surface
  operacion rapida, local, touch-first y clara para cajero

PC Surface
  gobierno, administracion, auditoria, compras, reportes y consolidacion

Shared Contracts
  ids, schema, permisos, eventos y compatibilidad minima
```

## 2. Reglas de frontera

Tablet puede vender, cobrar, consultar, corregir, abrir/cerrar turno, registrar devolucion controlada y mostrar pendientes por enviar. Tablet no debe administrar proveedores completos, compras, recepcion avanzada, auditoria profunda, reglas globales ni permisos pesados.

PC puede configurar catalogo avanzado, administrar inventario profundo, compras, recepcion, auditoria, dashboard, permisos, consolidacion y conflictos.

## 3. Estados de vertical

| Estado | Significado |
|---|---|
| `draft` | disenado pero no liberado |
| `available` | listo para activarse en entorno controlado |
| `enabled` | activo en una cuenta |
| `disabled` | apagado para una cuenta |
| `deprecated` | no usar en cuentas nuevas |

## 4. Regla de activacion

```text
navegacion visible = vertical activo + capacidades activas + permisos + superficie correcta
```

Nada de menu universal. El cajero de estetica no debe ver Lotes de farmacia, y el de farmacia no necesita Mesas como si fuera botica con restaurante clandestino.

## 5. Verticales iniciales


## Tienda de conveniencia (`convenience`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.products`, `barcode.scan`, `inventory.stock`, `shift.cash_control`, `returns.basic`, `offline.sales`, `sync.outbox`, `reports.today`, `export.local`.

**Tablet muestra:** Vender, Ventas de hoy, Existencias, Devoluciones, Turno, Pendientes por enviar.

**PC muestra:** Catalogo, Existencias, Movimientos, Compras, Recepcion, Auditoria, Dashboard, Sincronizacion.

**Bloqueado en Tablet:** `supplier.management`, `purchasing.full`, `receiving.full`, `audit.deep`.

**Eventos minimos:** `sale.completed`, `ticket.closed`, `stock.decremented`, `return.created`, `shift.opened`, `shift.closed`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Restaurante / cafeteria (`restaurant`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.products`, `sales.services`, `restaurant.tables`, `restaurant.open_tabs`, `restaurant.kitchen_tickets`, `payments.tips`, `shift.cash_control`, `offline.sales`, `sync.outbox`.

**Tablet muestra:** Vender, Mesas, Cuentas abiertas, Cobro, Ventas de hoy, Turno, Pendientes por enviar.

**PC muestra:** Menu, Inventario, Recetas, Cocina, Caja, Auditoria, Dashboard, Sincronizacion.

**Bloqueado en Tablet:** `recipe.costing.deep`, `supplier.management`, `purchase_order.approval`, `payroll.full`.

**Eventos minimos:** `restaurant.table.opened`, `restaurant.kitchen_ticket.sent`, `sale.completed`, `tip.recorded`, `restaurant.table.closed`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Farmacia (`pharmacy`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.products`, `barcode.scan`, `inventory.stock`, `inventory.lots`, `inventory.expiration`, `pharmacy.prescription_flag`, `returns.controlled`, `offline.sales.restricted`, `sync.outbox`, `audit.sensitive`.

**Tablet muestra:** Vender, Buscar producto, Existencias, Devoluciones, Turno, Pendientes por enviar.

**PC muestra:** Catalogo, Lotes, Caducidades, Compras, Recepcion, Auditoria, Dashboard, Sincronizacion.

**Bloqueado en Tablet:** `controlled_catalog.full_admin`, `supplier.management`, `bulk_price_change`, `audit.deep`.

**Eventos minimos:** `sale.completed`, `pharmacy.lot.decremented`, `pharmacy.expiration.warning_shown`, `pharmacy.controlled_item.blocked`, `return.created`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Estetica / barberia / salon (`beauty`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.services`, `sales.products`, `appointments.booking`, `staff.commissions.basic`, `customers.basic`, `payments.tips`, `shift.cash_control`, `offline.sales`, `sync.outbox`.

**Tablet muestra:** Cobrar servicio, Agenda de hoy, Productos, Ventas de hoy, Turno, Pendientes por enviar.

**PC muestra:** Agenda, Clientes, Servicios, Empleados, Comisiones, Inventario, Dashboard, Sincronizacion.

**Bloqueado en Tablet:** `payroll.full`, `commission_rules.deep`, `customer_marketing.full`, `supplier.management`.

**Eventos minimos:** `beauty.appointment.checked_in`, `beauty.service.completed`, `staff.commission.accrued`, `sale.completed`, `tip.recorded`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Ferreteria (`hardware`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.products`, `barcode.scan`, `inventory.stock`, `inventory.units_variable`, `quotes.basic`, `customer.credit.basic`, `returns.basic`, `offline.sales`, `sync.outbox`.

**Tablet muestra:** Vender, Cotizar, Existencias, Ventas de hoy, Devoluciones, Turno, Pendientes por enviar.

**PC muestra:** Catalogo, Unidades, Existencias, Compras, Recepcion, Clientes, Auditoria, Dashboard.

**Bloqueado en Tablet:** `unit_conversion_admin.deep`, `supplier.management`, `purchase_order.full`, `credit_policy.full`.

**Eventos minimos:** `quote.created`, `sale.completed`, `stock.decremented`, `unit_quantity.sold`, `return.created`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Ropa / boutique (`apparel`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.products`, `inventory.stock`, `inventory.variants`, `returns.exchange`, `customers.basic`, `discounts.basic`, `offline.sales`, `sync.outbox`.

**Tablet muestra:** Vender, Cambios, Existencias, Ventas de hoy, Turno, Pendientes por enviar.

**PC muestra:** Catalogo, Variantes, Existencias, Temporadas, Compras, Auditoria, Dashboard.

**Bloqueado en Tablet:** `variant_matrix_admin.deep`, `supplier.management`, `season_planning.full`, `price_rules.deep`.

**Eventos minimos:** `apparel.variant.sold`, `apparel.exchange.created`, `sale.completed`, `stock.decremented`, `discount.applied`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Taller / reparaciones (`repair`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.services`, `sales.products`, `repairs.work_orders`, `repairs.deposits`, `customers.basic`, `inventory.stock`, `offline.sales.restricted`, `sync.outbox`.

**Tablet muestra:** Cobrar, Ordenes, Refacciones, Ventas de hoy, Turno, Pendientes por enviar.

**PC muestra:** Ordenes, Clientes, Refacciones, Garantias, Inventario, Auditoria, Dashboard.

**Bloqueado en Tablet:** `diagnostic_templates.full`, `warranty_policy.deep`, `supplier.management`, `technician_payroll.full`.

**Eventos minimos:** `repair.work_order.opened`, `repair.deposit.received`, `repair.completed`, `sale.completed`, `repair.part.used`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Venta en campo / ruta (`field_route`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.products`, `delivery.routes`, `customers.basic`, `customer.credit.basic`, `inventory.mobile_stock`, `offline.sales`, `offline.strong`, `sync.outbox`, `payments.cash`, `export.local`.

**Tablet muestra:** Ruta, Vender, Clientes, Cobros, Ventas de hoy, Pendientes por enviar.

**PC muestra:** Rutas, Clientes, Credito, Inventario movil, Auditoria, Dashboard, Sincronizacion.

**Bloqueado en Tablet:** `credit_policy.full`, `route_planning.deep`, `multi_branch.reconciliation`, `supplier.management`.

**Eventos minimos:** `field_route.route.started`, `field_route.customer.visited`, `sale.completed`, `payment.collected`, `mobile_stock.decremented`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Abarrotes con bascula (`grocery_scale`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.products`, `barcode.scan`, `inventory.stock`, `inventory.units_weight`, `scale.integration.basic`, `offline.sales`, `sync.outbox`.

**Tablet muestra:** Vender, Pesables, Existencias, Ventas de hoy, Turno, Pendientes por enviar.

**PC muestra:** Catalogo, Unidades, Bascula, Existencias, Compras, Dashboard.

**Bloqueado en Tablet:** `scale_device_admin.deep`, `supplier.management`, `purchase_order.full`, `margin_rules.deep`.

**Eventos minimos:** `weighted_item.sold`, `sale.completed`, `stock.decremented`, `scale.reading.captured`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## Food truck / punto movil de comida (`food_truck`)

**Rol Tablet:** Operacion rapida del giro desde Tablet sin convertirla en backoffice.

**Rol PC:** Gobierno profundo del giro, auditoria, configuracion, compras, reportes y consolidacion.

**Capacidades:** `sales.products`, `sales.services`, `menu.combos`, `payments.tips`, `offline.sales`, `shift.cash_control`, `sync.outbox`, `export.local`.

**Tablet muestra:** Vender, Menu, Ventas de hoy, Turno, Pendientes por enviar.

**PC muestra:** Menu, Costos, Inventario, Eventos, Dashboard, Sincronizacion.

**Bloqueado en Tablet:** `recipe.costing.deep`, `supplier.management`, `event_planning.full`, `payroll.full`.

**Eventos minimos:** `menu.combo.sold`, `sale.completed`, `tip.recorded`, `shift.closed`, `sync.event.pending`.

**Regla operativa:** este vertical extiende PRISMA Core sin romper el flujo comun de venta. Si la Tablet empieza a mostrar configuracion profunda, proveedores completos o auditoria pesada, el vertical esta invadiendo PC como vecino que se estaciona en tu entrada.


## 6. Antipatrones prohibidos

- Agregar campos verticales al core sin contrato.
- Mostrar pantallas de todos los giros a todos los negocios.
- Crear eventos sin namespace.
- Usar terminos tecnicos visibles en Tablet.
- Meter proveedores completos en Tablet.
- Hacer que una venta basica dependa de PC.
- Convertir cada vertical en fork.
- Crear vertical sin fixtures, QA y criterios de aceptacion.

## 7. Definition of Done

Un vertical queda aceptable cuando tiene manifiesto valido, navegacion Tablet/PC, capacidades, permisos, eventos, politica offline, bloqueos de Tablet, KPIs y criterios de aceptacion. Tambien debe pasar validador y no contaminar el nucleo comun.

## 8. Siguiente paquete

Despues de este registro, toca `PRISMA_VERTICALS_ARCHITECTURE_00C_VERTICAL_DATA_MODELS`, para definir extensiones de datos por giro sin meter campos mutantes al core.
