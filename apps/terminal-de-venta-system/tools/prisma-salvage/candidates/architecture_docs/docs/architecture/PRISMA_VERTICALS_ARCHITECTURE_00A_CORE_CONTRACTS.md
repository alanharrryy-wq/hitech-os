# PRISMA_VERTICALS_ARCHITECTURE_00A_CORE_CONTRACTS

**Proyecto:** PRISMA POS / Terminal de Venta multi-giro  
**Entregable:** `PRISMA_VERTICALS_ARCHITECTURE_00A_CORE_CONTRACTS`  
**Tipo:** arquitectura fundacional + contratos  
**Estado:** base canonica propuesta  
**Idioma visible:** es-MX  
**Regla madre:** PRISMA Core vende. Los verticales especializan. PC gobierna. Tablet opera. Shared Kernel no se vuelve basurero.

---

## 0. Proposito

Este documento define la primera capa formal para que PRISMA pueda escalar a multiples giros de negocio sin convertir el POS en una sopa de cables con pantalla tactil.

El objetivo de `00A_CORE_CONTRACTS` no es implementar todos los giros. El objetivo es fijar las reglas, contratos y limites para que cada giro futuro pueda entrar como modulo enchufable, verificable y reversible.

Esta capa debe proteger tres cosas:

1. **El nucleo comun POS.** Lo que todos los negocios necesitan para vender.
2. **Las capacidades verticales.** Lo que cada giro activa sin contaminar a los demas.
3. **La frontera Tablet / PC.** Tablet opera. PC administra profundo.

---

## 1. Decision canonica multi-giro

PRISMA se estructura en tres niveles:

```text
PRISMA Core
  -> capacidades comunes de venta, caja, inventario basico, turnos, devoluciones, eventos y sync

Vertical Layer
  -> capacidades especificas por giro: restaurante, farmacia, estetica, ferreteria, taller, ropa, ruta, etc.

Product Surfaces
  -> Tablet POS y PC Backoffice consumen el core y activan capacidades segun perfil de negocio
```

### 1.1 Regla de separacion

Un vertical **no puede** modificar el comportamiento comun del core si ese cambio rompe a otro giro.

Ejemplo correcto:

- Restaurante agrega mesas y comandas.
- Farmacia agrega lotes y caducidad.
- Estetica agrega citas y servicios.

Ejemplo incorrecto:

- Restaurante obliga a que toda venta tenga mesa.
- Farmacia obliga a que todo producto tenga lote.
- Estetica obliga a que todo ticket tenga cita.

El core debe seguir vendiendo productos simples aunque ningun vertical este activo.

---

## 2. PRISMA Core

El core es el conjunto minimo que debe existir en todos los giros.

### 2.1 Capacidades core obligatorias

| Codigo | Nombre visible | Responsabilidad |
|---|---|---|
| `core.sales` | Vender | Crear tickets, agregar lineas y cerrar venta |
| `core.payments` | Cobro | Registrar metodo de pago y total cobrado |
| `core.ticket` | Ticket | Mantener lineas, cantidades, subtotal, total y correcciones |
| `core.catalog` | Catalogo basico | Consultar productos o servicios vendibles |
| `core.inventory.basic` | Existencias basicas | Ver y descontar existencia cuando aplique |
| `core.returns` | Devoluciones | Registrar devoluciones controladas |
| `core.shift` | Turno | Abrir, consultar y cerrar turno operativo |
| `core.reports.today` | Ventas de hoy | Consultar ventas locales del dia |
| `core.events` | Eventos | Registrar hechos operativos auditables |
| `core.sync` | Pendientes por enviar | Mostrar envio, fallos y reintentos |
| `core.export` | Exportar | Exportar datos locales permitidos |
| `core.permissions` | Permisos | Controlar acciones sensibles |

### 2.2 Reglas del core

1. El core no debe conocer detalles de un giro especifico.
2. El core no debe depender de PC para vender.
3. El core no debe depender de internet para cerrar una venta local permitida.
4. El core debe emitir eventos para toda accion sensible.
5. El core debe traducir errores tecnicos a mensajes operativos.
6. El core debe permitir que una capacidad vertical bloquee, extienda o valide una accion solo mediante contrato formal.

---

## 3. Vertical Layer

La capa vertical define perfiles de negocio y capacidades opcionales.

### 3.1 Que es un vertical

Un vertical es un paquete de reglas, pantallas, datos, eventos, permisos y validaciones para un giro.

No es una carpeta de componentes sueltos.
No es un tema visual.
No es un modo bonito.
No es un hack con `if businessType == restaurant` regado como confeti triste.

Un vertical debe declarar:

- `verticalId`
- nombre visible
- capacidades requeridas
- capacidades opcionales
- entidades de datos propias
- eventos propios
- permisos propios
- rutas Tablet permitidas
- rutas PC permitidas
- reglas offline
- reglas de sync
- fixtures minimos
- smoke checks

### 3.2 Verticales iniciales previstos

| Vertical | ID | Prioridad | Razon |
|---|---|---:|---|
| Tienda de conveniencia | `convenience` | 1 | Base actual del POS |
| Restaurante / cafeteria | `restaurant` | 2 | Cambia venta por mesas/comandas |
| Farmacia | `pharmacy` | 3 | Requiere lotes/caducidad/controles |
| Estetica / barberia | `beauty` | 4 | Servicios, citas, comisiones |
| Ferreteria | `hardware` | 5 | Unidades variables y cotizaciones |
| Ropa / boutique | `apparel` | 6 | Variantes, tallas, cambios |
| Taller / reparacion | `repair` | 7 | Ordenes de trabajo y refacciones |
| Ruta / campo | `field_route` | 8 | Offline fuerte, rutas, preventa |

---

## 4. Sistema de capacidades

Las capacidades son interruptores funcionales gobernados por contrato.

### 4.1 Familias de capacidades

```text
sales.*
payments.*
inventory.*
appointments.*
restaurant.*
pharmacy.*
delivery.*
repair.*
customer.*
staff.*
sync.*
reports.*
```

### 4.2 Capacidades comunes extendibles

| Capacidad | Descripcion | Tablet | PC |
|---|---|---|---|
| `sales.products` | Venta de productos | Principal | Consulta/reporting |
| `sales.services` | Venta de servicios | Principal si aplica | Configuracion avanzada |
| `payments.cash` | Efectivo | Principal | Auditoria |
| `payments.card` | Tarjeta | Principal | Auditoria |
| `payments.transfer` | Transferencia | Principal | Auditoria |
| `inventory.stock` | Existencia por producto | Consulta/descuento | Gobierno |
| `inventory.adjustments` | Ajustes | Limitado | Principal |
| `sync.outbox` | Pendientes por enviar | Visible y operativo | Reconciliacion |
| `reports.today` | Resumen del dia | Operativo | Consolidado |

### 4.3 Capacidades verticales

| Capacidad | Vertical tipico | Descripcion |
|---|---|---|
| `restaurant.tables` | Restaurante | Mesas, cuentas abiertas |
| `restaurant.kitchen_orders` | Restaurante | Comandas a cocina |
| `restaurant.tips` | Restaurante | Propina y reparto |
| `pharmacy.lots` | Farmacia | Lotes y caducidad |
| `pharmacy.prescription` | Farmacia | Receta o autorizacion |
| `beauty.appointments` | Estetica | Agenda y citas |
| `beauty.commissions` | Estetica | Comisiones por servicio |
| `hardware.measure_units` | Ferreteria | Venta por metro, kilo, litro o pieza |
| `apparel.variants` | Ropa | Tallas, colores, variantes |
| `repair.work_orders` | Taller | Ordenes de reparacion |
| `field_route.routes` | Campo | Rutas y preventa |
| `customer.credit` | Varios | Credito a cliente |

---

## 5. Contrato de activacion vertical

Cada vertical se activa por manifiesto.

### 5.1 Manifiesto minimo

```json
{
  "schemaVersion": "1.0.0",
  "verticalId": "convenience",
  "displayName": "Tienda de conveniencia",
  "coreRequired": true,
  "capabilities": {
    "required": ["core.sales", "core.payments", "core.ticket"],
    "optional": ["inventory.stock", "sync.outbox"]
  },
  "surfaces": {
    "tablet": { "enabled": true },
    "pc": { "enabled": true }
  },
  "offline": {
    "salesAllowed": true,
    "sensitiveActionsRequireConnection": false
  }
}
```

### 5.2 Reglas de activacion

1. Ningun vertical se activa sin manifiesto valido.
2. Toda capacidad requerida debe existir.
3. Toda ruta visible debe tener nombre de negocio en es-MX.
4. Toda accion sensible debe declarar permiso.
5. Toda entidad vertical debe declarar dueño.
6. Todo evento vertical debe declarar contrato.
7. Todo cambio de vertical debe pasar smoke check.

---

## 6. Frontera Tablet / PC

### 6.1 Tablet puede hacer

- vender;
- cobrar;
- corregir ticket;
- consultar catalogo operativo;
- consultar existencia operativa;
- alta basica cuando el giro lo permita;
- devoluciones guiadas;
- abrir/cerrar turno;
- operar offline si la politica lo permite;
- ver pendientes por enviar;
- exportar datos locales permitidos.

### 6.2 Tablet no debe hacer

- compras avanzadas;
- recepcion formal de mercancia;
- auditoria profunda;
- control multi-sucursal complejo;
- configuracion avanzada de permisos;
- gestion completa de proveedores;
- reconciliacion compleja de conflictos;
- administracion pesada por vertical.

### 6.3 PC puede hacer

- gobierno avanzado de catalogo;
- inventario profundo;
- compras;
- recepcion;
- reabasto;
- auditoria;
- dashboard ejecutivo;
- permisos;
- usuarios;
- terminales;
- consolidacion multi-terminal;
- conflictos de sincronizacion.

---

## 7. Eventos core y eventos verticales

### 7.1 Eventos core

```text
sale.created
sale.completed
ticket.closed
payment.recorded
stock.decremented
return.created
shift.opened
shift.closed
sync.event.sent
sync.event.failed
```

### 7.2 Eventos verticales previstos

```text
restaurant.table.opened
restaurant.table.closed
restaurant.kitchen_order.sent
pharmacy.lot.consumed
pharmacy.prescription.attached
beauty.appointment.created
beauty.service.completed
hardware.measurement.sold
apparel.variant.sold
repair.work_order.opened
repair.work_order.closed
field_route.visit.completed
```

### 7.3 Regla de eventos

Un evento vertical no debe reemplazar un evento core. Debe complementarlo.

Ejemplo restaurante:

```text
sale.completed
restaurant.table.closed
restaurant.kitchen_order.sent
```

Ejemplo farmacia:

```text
sale.completed
stock.decremented
pharmacy.lot.consumed
```

---

## 8. Permisos

### 8.1 Permisos core

```text
pos.sale.create
pos.sale.complete
pos.ticket.edit
pos.return.create
shift.open
shift.close
inventory.local.view
inventory.local.adjust.basic
report.today.view
sync.pending.view
export.local.create
```

### 8.2 Permisos verticales

```text
restaurant.table.manage
restaurant.kitchen_order.send
restaurant.tip.edit
pharmacy.prescription.override
pharmacy.lot.adjust
beauty.appointment.manage
beauty.commission.view
hardware.quote.create
apparel.exchange.create
repair.work_order.manage
field_route.visit.manage
customer.credit.approve
```

### 8.3 Regla

La Tablet puede ejecutar permisos operativos. PC administra permisos estructurales.

---

## 9. Datos y extensibilidad

### 9.1 Regla principal

El modelo base no debe inflarse para satisfacer todos los giros.

Incorrecto:

```text
Product.tableId
Product.prescriptionId
Product.appointmentId
Product.repairOrderId
```

Correcto:

```text
Core Product
Vertical Extension Table
Vertical Event
Vertical Metadata Contract
```

### 9.2 Patron recomendado

```text
core_entity
vertical_extension
vertical_event
vertical_projection
```

Ejemplo:

```text
Product
PharmacyProductExtension
PharmacyLot
PharmacyLotMovement
```

Ejemplo restaurante:

```text
Sale
RestaurantTableSession
KitchenOrder
KitchenOrderLine
```

---

## 10. Navegacion por vertical

La navegacion visible debe ser generada por perfil de negocio.

### 10.1 Core Tablet

```text
Vender
Cobro
Ventas de hoy
Existencias
Devoluciones
Turno
Pendientes por enviar
Exportar
```

### 10.2 Restaurante Tablet

```text
Vender
Mesas
Comandas
Cobro
Ventas de hoy
Turno
Pendientes por enviar
```

### 10.3 Farmacia Tablet

```text
Vender
Catalogo
Existencias
Caducidades
Devoluciones
Turno
Pendientes por enviar
```

### 10.4 Estetica Tablet

```text
Vender
Citas
Servicios
Clientes
Cobro
Turno
Pendientes por enviar
```

### 10.5 Regla

Si una opcion no ayuda a operar el giro en caja, no debe estar en Tablet como navegacion principal.

---

## 11. KPIs

### 11.1 KPIs core

- ventas netas;
- numero de tickets;
- ticket promedio;
- unidades por ticket;
- tiempo promedio de venta;
- tiempo promedio de escaneo;
- devoluciones/cancelaciones;
- uso offline;
- latencia de sincronizacion.

### 11.2 KPIs por vertical

| Vertical | KPIs propios |
|---|---|
| Restaurante | ocupacion de mesas, tiempo de comanda, propina promedio |
| Farmacia | productos por caducar, lotes consumidos, recetas asociadas |
| Estetica | citas atendidas, no-shows, comision por empleado |
| Ferreteria | cotizaciones convertidas, venta por unidad variable |
| Ropa | cambios por variante, rotacion por talla/color |
| Taller | ordenes abiertas, tiempo de reparacion, refacciones usadas |
| Campo | visitas realizadas, ventas por ruta, ventas offline |

---

## 12. Validaciones obligatorias

Todo vertical debe pasar:

1. Manifiesto valido.
2. Capacidades requeridas existentes.
3. Rutas visibles con nombres es-MX.
4. Sin terminos tecnicos visibles.
5. Permisos declarados para acciones sensibles.
6. Eventos declarados para acciones sensibles.
7. Offline declarado.
8. Smoke check Tablet.
9. Smoke check PC si aplica.
10. Prueba de no contaminacion del core.

---

## 13. Reglas anti-caos

Queda prohibido:

- meter `if vertical == ...` regado en pantallas core;
- inflar tablas core con campos de todos los giros;
- hacer que un vertical rompa venta basica;
- meter backoffice completo en Tablet;
- duplicar eventos core con nombres distintos;
- usar ingles visible en UI final;
- crear rutas sin contrato de intencion;
- activar capacidades sin permisos;
- aceptar verticales sin fixtures;
- saltarse instalador, backup, verify y rollback.

---

## 14. Roadmap de verticalizacion

### 00A - Core contracts

Este paquete. Define arquitectura, contratos, capacidades y reglas.

### 00B - Vertical registry

Registro formal de verticales, perfiles, manifest loader y catalogo de capacidades.

### 00C - Vertical data models

Patrones de extension de datos y modelos iniciales por giro.

### 00D - Events permissions

Eventos, permisos y auditoria por vertical.

### 00E - UX operations

Navegacion, flujos y microcopy por vertical.

### 00F - Validation fixtures

Fixtures, pruebas, smoke checks y criterios de aceptacion.

---

## 15. Decision final

PRISMA no debe crecer como una app por giro separada. Debe crecer como una plataforma POS con core comun y verticales enchufables.

La forma correcta es:

```text
Core estable
+ capacidades declaradas
+ vertical manifest
+ extensiones aisladas
+ eventos auditables
+ permisos claros
+ validacion automatica
```

Si se respeta esta arquitectura, PRISMA puede escalar a muchos giros sin volverse monstruo de feria.
