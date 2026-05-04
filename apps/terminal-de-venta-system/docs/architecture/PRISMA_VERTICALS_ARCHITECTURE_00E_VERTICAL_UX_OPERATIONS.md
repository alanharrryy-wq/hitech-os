# PRISMA Verticales 00E - UX Operations

**Paquete:** `PRISMA_VERTICALS_ARCHITECTURE_00E_VERTICAL_UX_OPERATIONS`  
**Propósito:** definir cómo se opera PRISMA por giro en Tablet y PC sin rediseñar la interfaz visual y sin convertir Tablet en backoffice.  
**Decisión:** las verticales no solo activan datos; activan rutas, flujos, microcopy, estados, permisos visibles y límites de operación.

## Regla madre

Tablet opera. PC gobierna. Core vende. Vertical especializa.

Si una pantalla de Tablet obliga al cajero a pensar como administrador, esa pantalla está en el producto equivocado. Si PC intenta cobrar como caja principal, también está en el producto equivocado. Esta división permite que un giro nuevo no se pegue con cinta canela al POS base.

## Principios operativos

1. La primera acción visible de Tablet debe ser la acción de trabajo del giro.
2. Cada vertical debe declarar su pantalla primaria, sus pantallas secundarias y sus pantallas prohibidas en Tablet.
3. Toda acción deshabilitada debe explicar la razón en lenguaje de negocio.
4. Todo estado vacío debe decir qué pasó y cuál es el siguiente movimiento.
5. Los términos técnicos nunca son texto de usuario final.
6. La navegación de Tablet debe estar limitada a operación diaria.
7. PC puede tener módulos pesados, pero cada módulo debe tener propósito claro y salida operativa.
8. Offline debe sentirse como continuidad controlada, no como desastre.
9. Las devoluciones, cambios, autorizaciones y operaciones sensibles deben ser guiadas.
10. Cada vertical debe poder probarse con una ruta feliz y tres rutas de error.

## Matriz de operación por vertical

| Vertical | Nombre | Tablet principal | PC principal | Flujo dominante |
| --- | --- | --- | --- | --- |
| convenience | Tienda de conveniencia | Vender, Cobro, Ventas de hoy, Existencias | Catálogo avanzado, Inventario, Compras, Recepción | venta de productos por código de barras, ticket rápido, efectivo, tarjeta, devolución simple y corte de turno |
| restaurant | Restaurante / cafetería | Vender, Mesa o pedido, Cobro, Cocina | Menú avanzado, Recetas/costos, Mesas, Cocina | pedido abierto, mesa o para llevar, envío a cocina, cierre de cuenta, propina opcional y corte |
| pharmacy | Farmacia | Vender, Cobro, Consulta producto, Ventas de hoy | Catálogo regulado, Lotes, Caducidades, Compras | venta de producto sensible, revisión de lote/caducidad, bloqueo por permiso, ticket y auditoría |
| beauty | Estética / barbería / salón | Agenda, Cobro, Servicios, Clientes | Catálogo de servicios, Personal, Comisiones, Agenda avanzada | cita o servicio sin cita, selección de servicio, asignación de personal, cobro y comisión |
| hardware | Ferretería | Vender, Cotización rápida, Cobro, Existencias | Catálogo técnico, Unidades, Cotizaciones, Inventario | venta por pieza, metro, kilo o paquete, cotización rápida, conversión de unidades y cobro |
| apparel | Ropa / boutique | Vender, Cambios, Cobro, Variantes | Catálogo variantes, Temporadas, Inventario, Promociones | venta por talla/color, cambio de producto, ticket y consulta de variantes disponibles |
| repair | Taller / reparaciones | Órdenes, Cobro, Refacciones, Anticipos | Órdenes avanzadas, Diagnóstico, Garantías, Inventario | orden de trabajo, diagnóstico simple, refacción, mano de obra, anticipo y cierre |
| field_route | Venta en campo / ruta | Ruta, Vender, Cobro, Clientes | Rutas, Clientes, Crédito, Inventario móvil | visita a cliente, venta offline, cobro, crédito permitido, pendiente de envío y cierre de ruta |
| grocery_scale | Abarrotes con báscula | Vender, Pesaje, Cobro, Existencias | Catálogo pesable, Unidades, Básculas, Inventario | producto pesable, lectura de peso o captura manual, precio por unidad, ticket y cobro |
| food_truck | Food truck / punto móvil de comida | Vender, Pedido, Cobro, Menú disponible | Menú, Recetas, Inventario, Ubicaciones | pedido rápido, menú limitado, cobro, estado offline, corte por ubicación o evento |

## Vertical: Tienda de conveniencia (`convenience`)

### Propósito operativo
Venta de productos por código de barras, ticket rápido, efectivo, tarjeta, devolución simple y corte de turno. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Vender, Cobro, Ventas de hoy, Existencias, Devoluciones, Turno, Pendientes por enviar.

### Navegación PC recomendada
Catálogo avanzado, Inventario, Compras, Recepción, Auditoría, Dashboard, Sincronización.

### No debe vivir en Tablet
proveedores completos en Tablet; compras formales en Tablet; conteo físico profundo en caja.

### Estados de error especiales
producto no encontrado; producto sin stock; precio faltante; código duplicado.

### KPIs UX asociados
tiempo promedio de venta; tiempo promedio de escaneo; número de tickets; quiebres de stock; devoluciones.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `venta de productos por código de barras, ticket rápido, efectivo, tarjeta, devolución simple y corte de turno` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Restaurante / cafetería (`restaurant`)

### Propósito operativo
Pedido abierto, mesa o para llevar, envío a cocina, cierre de cuenta, propina opcional y corte. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Vender, Mesa o pedido, Cobro, Cocina, Ventas de hoy, Turno, Pendientes por enviar.

### Navegación PC recomendada
Menú avanzado, Recetas/costos, Mesas, Cocina, Compras, Inventario, Dashboard.

### No debe vivir en Tablet
compras completas en Tablet; recetas complejas en caja; costeo profundo frente al cliente.

### Estados de error especiales
pedido sin mesa; producto agotado; cocina no disponible; cuenta dividida.

### KPIs UX asociados
tiempo de toma de pedido; tiempo a cocina; ticket promedio; ventas por mesa; cancelaciones.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `pedido abierto, mesa o para llevar, envío a cocina, cierre de cuenta, propina opcional y corte` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Farmacia (`pharmacy`)

### Propósito operativo
Venta de producto sensible, revisión de lote/caducidad, bloqueo por permiso, ticket y auditoría. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Vender, Cobro, Consulta producto, Ventas de hoy, Lotes próximos a vencer, Turno, Pendientes por enviar.

### Navegación PC recomendada
Catálogo regulado, Lotes, Caducidades, Compras, Auditoría, Permisos, Dashboard.

### No debe vivir en Tablet
cambios masivos de precio en Tablet; alta avanzada de controlados en caja; ajustes grandes offline.

### Estados de error especiales
receta requerida; lote vencido; producto restringido; autorización requerida.

### KPIs UX asociados
ventas por producto sensible; caducidades próximas; devoluciones; errores de captura; lotes bloqueados.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `venta de producto sensible, revisión de lote/caducidad, bloqueo por permiso, ticket y auditoría` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Estética / barbería / salón (`beauty`)

### Propósito operativo
Cita o servicio sin cita, selección de servicio, asignación de personal, cobro y comisión. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Agenda, Cobro, Servicios, Clientes, Ventas de hoy, Turno, Pendientes por enviar.

### Navegación PC recomendada
Catálogo de servicios, Personal, Comisiones, Agenda avanzada, Inventario, Dashboard.

### No debe vivir en Tablet
nómina completa en Tablet; configuración avanzada de comisiones en caja; inventario profundo.

### Estados de error especiales
cita empalmada; servicio sin precio; personal no asignado; cliente no llega.

### KPIs UX asociados
servicios por día; ticket promedio; productividad por persona; comisiones; no-show.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `cita o servicio sin cita, selección de servicio, asignación de personal, cobro y comisión` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Ferretería (`hardware`)

### Propósito operativo
Venta por pieza, metro, kilo o paquete, cotización rápida, conversión de unidades y cobro. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Vender, Cotización rápida, Cobro, Existencias, Ventas de hoy, Turno, Pendientes por enviar.

### Navegación PC recomendada
Catálogo técnico, Unidades, Cotizaciones, Inventario, Compras, Recepción, Dashboard.

### No debe vivir en Tablet
catálogo técnico completo en Tablet; recepción de compra desde caja; ajuste masivo de inventario.

### Estados de error especiales
unidad inválida; cantidad decimal inválida; cotización vencida; existencia insuficiente.

### KPIs UX asociados
ventas por unidad; cotizaciones convertidas; errores de unidad; stock crítico; margen por familia.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `venta por pieza, metro, kilo o paquete, cotización rápida, conversión de unidades y cobro` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Ropa / boutique (`apparel`)

### Propósito operativo
Venta por talla/color, cambio de producto, ticket y consulta de variantes disponibles. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Vender, Cambios, Cobro, Variantes, Ventas de hoy, Turno, Pendientes por enviar.

### Navegación PC recomendada
Catálogo variantes, Temporadas, Inventario, Promociones, Compras, Dashboard.

### No debe vivir en Tablet
compras completas en Tablet; temporadas avanzadas frente al cliente; gestión profunda de variantes.

### Estados de error especiales
talla agotada; color agotado; cambio fuera de política; variante no encontrada.

### KPIs UX asociados
ventas por talla; cambios; rotación por variante; stock por color; ticket promedio.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `venta por talla/color, cambio de producto, ticket y consulta de variantes disponibles` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Taller / reparaciones (`repair`)

### Propósito operativo
Orden de trabajo, diagnóstico simple, refacción, mano de obra, anticipo y cierre. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Órdenes, Cobro, Refacciones, Anticipos, Ventas de hoy, Turno, Pendientes por enviar.

### Navegación PC recomendada
Órdenes avanzadas, Diagnóstico, Garantías, Inventario, Compras, Auditoría, Dashboard.

### No debe vivir en Tablet
diagnóstico técnico profundo en caja; garantías complejas sin PC; compras desde Tablet.

### Estados de error especiales
orden incompleta; anticipo insuficiente; refacción sin stock; garantía requerida.

### KPIs UX asociados
órdenes abiertas; tiempo de reparación; anticipos; refacciones usadas; garantías.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `orden de trabajo, diagnóstico simple, refacción, mano de obra, anticipo y cierre` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Venta en campo / ruta (`field_route`)

### Propósito operativo
Visita a cliente, venta offline, cobro, crédito permitido, pendiente de envío y cierre de ruta. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Ruta, Vender, Cobro, Clientes, Pendientes por enviar, Ventas de hoy, Cierre de ruta.

### Navegación PC recomendada
Rutas, Clientes, Crédito, Inventario móvil, Cobranza, Dashboard, Sincronización.

### No debe vivir en Tablet
reconciliación pesada en Tablet; cambio de rutas sin control; permisos de crédito sin política.

### Estados de error especiales
cliente sin ruta; crédito no permitido; sin conexión; venta pendiente por enviar.

### KPIs UX asociados
visitas realizadas; ventas por ruta; uso offline; latencia de envío; cobranza.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `visita a cliente, venta offline, cobro, crédito permitido, pendiente de envío y cierre de ruta` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Abarrotes con báscula (`grocery_scale`)

### Propósito operativo
Producto pesable, lectura de peso o captura manual, precio por unidad, ticket y cobro. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Vender, Pesaje, Cobro, Existencias, Ventas de hoy, Turno, Pendientes por enviar.

### Navegación PC recomendada
Catálogo pesable, Unidades, Básculas, Inventario, Compras, Dashboard.

### No debe vivir en Tablet
calibración avanzada en Tablet; compras profundas; ajustes masivos de peso.

### Estados de error especiales
peso inválido; báscula no disponible; producto no pesable; precio por kilo faltante.

### KPIs UX asociados
ventas pesables; errores de peso; merma; ticket promedio; quiebres.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `producto pesable, lectura de peso o captura manual, precio por unidad, ticket y cobro` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Vertical: Food truck / punto móvil de comida (`food_truck`)

### Propósito operativo
Pedido rápido, menú limitado, cobro, estado offline, corte por ubicación o evento. La Tablet debe priorizar este flujo antes que cualquier módulo de administración. PC conserva configuración, auditoría y administración profunda.

### Navegación Tablet permitida
Vender, Pedido, Cobro, Menú disponible, Ventas de hoy, Turno, Pendientes por enviar.

### Navegación PC recomendada
Menú, Recetas, Inventario, Ubicaciones, Compras, Dashboard.

### No debe vivir en Tablet
recetas completas en Tablet; compras formales; cambios complejos de ubicación.

### Estados de error especiales
menú agotado; sin conexión; ubicación sin abrir; pedido cancelado.

### KPIs UX asociados
ventas por evento; productos agotados; tiempo de pedido; uso offline; ticket promedio.

### Criterio humano de aceptación
Un operador nuevo debe completar el flujo `pedido rápido, menú limitado, cobro, estado offline, corte por ubicación o evento` sin pedir explicación externa, entendiendo cada bloqueo en lenguaje simple y pudiendo regresar a la acción principal en un toque.


## Decisiones anti-caos

- No se permite que una vertical modifique la intención de una pantalla core.
- No se permite que una vertical renombre una acción primaria core sin mapearla a negocio.
- No se permite exponer campos técnicos al usuario final.
- No se permite mezclar configuración global con venta diaria.
- No se permite crear navegación por vertical sin estado vacío, error, deshabilitado, offline y pendiente por enviar.
- No se permite que una vertical agregue operación sensible sin permiso visible y evento auditable.
