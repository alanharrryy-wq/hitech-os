# PRISMA Verticales 00D - Eventos, Permisos, Auditoria y Sincronizacion

**Paquete:** `PRISMA_VERTICALS_ARCHITECTURE_00D_VERTICAL_EVENTS_PERMISSIONS`  
**Estado:** arquitectura instalable  
**Idioma visible:** es-MX operativo  
**Regla madre:** todo giro puede especializar eventos y permisos, pero no puede romper el sobre comun de auditoria, sync y seguridad.

## 0. Proposito

Este documento define como PRISMA controla eventos, permisos, auditoria y sincronizacion por vertical de negocio. El objetivo es que cada giro pueda crecer sin convertir el sistema en una piñata de ifs, banderas secretas y botones con poderes de villano.

La regla central es simple: **si una accion toca dinero, inventario, cliente, turno, permiso, auditoria o sincronizacion, debe tener evento, permiso y rastro.**

## 1. Decision canonica

PRISMA separa cuatro niveles:

1. **Core events:** hechos comunes a cualquier negocio.
2. **Vertical events:** hechos propios del giro.
3. **Core permissions:** permisos que existen en todo POS/backoffice.
4. **Vertical permissions:** permisos que solo existen cuando una capacidad vertical esta activa.

Esto evita que una farmacia herede mesas de restaurante o que una barberia cargue lote sanitario como si vendiera jarabe para la tos. La vida ya es rara sin eso.


## Vertical: Tienda de conveniencia

**ID:** `convenience`  
**Capacidades base:** `pos.sale`, `inventory.stock`, `shift.cash`, `sync.outbox`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Restaurante o cafeteria

**ID:** `restaurant`  
**Capacidades base:** `pos.sale`, `restaurant.table`, `restaurant.kitchen`, `tips.gratuity`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Farmacia

**ID:** `pharmacy`  
**Capacidades base:** `pos.sale`, `pharmacy.lot`, `pharmacy.prescription`, `inventory.expiration`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Estetica, barberia o salon

**ID:** `beauty`  
**Capacidades base:** `services.sale`, `appointments.booking`, `staff.commission`, `customer.profile`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Ferreteria

**ID:** `hardware`  
**Capacidades base:** `pos.sale`, `quote.create`, `inventory.units`, `bulk.pricing`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Ropa o boutique

**ID:** `apparel`  
**Capacidades base:** `pos.sale`, `apparel.variant`, `exchange.flow`, `inventory.stock`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Taller o reparaciones

**ID:** `repair`  
**Capacidades base:** `work_order.create`, `parts.consume`, `labor.charge`, `customer.approval`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Venta en campo o ruta

**ID:** `field_route`  
**Capacidades base:** `route.visit`, `preorder.capture`, `offline.sale`, `cash.collection`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Abarrotes con bascula

**ID:** `grocery_scale`  
**Capacidades base:** `weighted.sale`, `scale.capture`, `inventory.stock`, `price.lookup`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## Vertical: Food truck o punto movil

**ID:** `food_truck`  
**Capacidades base:** `pos.sale`, `menu.item`, `offline.sale`, `daily.close`

### Politica de eventos

- Debe emitir eventos core cuando vende, cobra, devuelve, abre turno, cierra turno o descuenta inventario.
- Debe emitir eventos verticales solo cuando la accion pertenezca al giro.
- Ningun evento visible para cajero debe mostrar nombres internos, payloads, colas tecnicas ni errores de programador.

### Politica de permisos

- Cajero opera venta y consulta local.
- Supervisor autoriza devoluciones sensibles o ajustes.
- PC/backoffice gobierna permisos pesados, auditoria historica y reconciliacion.
- Tablet no administra seguridad avanzada, solo respeta decisiones.

### Politica offline

- Venta local permitida cuando la politica del vertical lo permita.
- Eventos quedan como pendientes por enviar.
- Acciones sensibles pueden bloquearse hasta reconexion o autorizacion.


## 12. Regla anti-caos

Nunca agregar un evento vertical metiendolo directo en componentes UI. Primero entra al catalogo de eventos, luego a la politica del vertical, despues a permisos, despues a auditoria y al final a la UI.

Si no pasa por ese camino, es contrabando arquitectonico. Y el contrabando arquitectonico siempre termina debajo de la alfombra, oliendo feo.
