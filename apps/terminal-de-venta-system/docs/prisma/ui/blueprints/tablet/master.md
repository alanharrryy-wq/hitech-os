# PRISMA UI Tablet Master Blueprint v3

> Documento maestro heredado y promovido a vista de entrada modular.

# PRISMA UI Blueprint Tablet - Nivel Dios v2.0

**Cliente:** Tablet / Touch / Floor Operations  
**Fecha:** 2026-04-25  
**Estado:** Blueprint maestro vivo  
**Hermano obligatorio:** `prisma_ui_pc_blueprint_nivel_dios_v2.md`  
**Objetivo:** diseñar la experiencia Tablet como consola operativa rápida, táctil, modular y pluginable para mostrador, piso, almacén, ruta, acceso, recepción, producción ligera o servicio.

---

## 1. Decisión base

La versión Tablet de PRISMA no es "PC chiquito". Eso sería meter una sala completa en un vocho y luego preguntar por qué nadie respira. Tablet debe ser **operación concentrada**: menos columnas, más acciones, más tarjetas, más escaneo, más flujo guiado, más resiliencia offline.

PC gobierna y configura. Tablet ejecuta, captura, cobra, atiende, recibe, cuenta, entrega, valida acceso y mueve trabajo.


## 2. Contrato de documentos gemelos

Estos dos archivos deben crecer como pareja técnica:

- `prisma_ui_pc_blueprint_nivel_dios_v2.md`
- `prisma_ui_tablet_blueprint_nivel_dios_v2.md`

### 2.1 Regla de espejo

Cada cambio importante debe declarar si afecta:

| Tipo de cambio | PC | Tablet | Regla |
| --- | --- | --- | --- |
| nuevo módulo core | obligatorio | obligatorio | ambos lo mencionan aunque lo muestren distinto |
| nueva capacidad plugin | obligatorio | obligatorio | PC configura y gobierna; Tablet ejecuta si aplica |
| nueva pantalla | opcional | opcional | solo si el patrón no cabe en pantallas existentes |
| nuevo estado operativo | obligatorio | obligatorio | no puede existir estado que un cliente no entienda |
| nuevo permiso | obligatorio | obligatorio | se documenta quién lo ve, quién lo ejecuta y quién audita |
| nuevo hardware | obligatorio | obligatorio si toca operación | por adaptador, nunca por pantalla hardcodeada |

### 2.2 Niveles de paridad

No todo debe verse igual. Eso sería diseño flojo disfrazado de consistencia.

| Nivel | Qué significa | Ejemplo |
| --- | --- | --- |
| Paridad de dominio | ambos usan el mismo concepto | `Sale`, `Customer`, `InventoryMovement` |
| Paridad de permiso | ambos respetan la misma autoridad | cajero no puede cerrar caja ajena |
| Paridad de estado | ambos entienden el mismo ciclo | pedido `draft -> confirmed -> fulfilled -> paid` |
| Paridad de evento | ambos emiten eventos compatibles | `sale.created`, `cash.closed` |
| Divergencia de experiencia | cada cliente optimiza su forma | PC tabla densa; Tablet flujo táctil |

### 2.3 Regla anti-muerte

Ningún documento puede crecer con secciones exclusivas sin registrar su impacto en el otro. Si Tablet agrega `check-in biométrico`, PC debe tener por lo menos configuración, permisos, reporte o auditoría de esa capacidad. Si PC agrega `lista de precios B2B`, Tablet debe saber cómo vender con esa lista o mostrar que no aplica.

## 3. Principios de arquitectura UI

1. **Core primero, vertical después.** La pantalla base no sabe si está en tienda, gym o maquila. Solo sabe que hay clientes, órdenes, pagos, inventario, eventos y permisos.
2. **Slots antes que forks.** Un plugin se monta en zonas permitidas. No clona pantallas como gremlin mojado.
3. **Estado visible siempre.** Caja, sync, sucursal, usuario, permisos y modo offline deben estar a la vista.
4. **Una fuente de verdad por forma.** Si `Customer` existe, ningún plugin crea `MemberCustomer`, `PatientCustomer` o `ClientitoVIP` como entidad paralela.
5. **Acción cerca del dato.** Si el usuario ve una deuda, debe poder cobrar o prometer pago según permiso. Si ve stock crítico, debe poder comprar, transferir o apartar.
6. **Offline-first sin teatro.** Todo flujo operativo debe declarar qué hace sin internet y cómo se reconcilia.
7. **Auditoría sin estorbar.** La trazabilidad vive detrás, pero aparece cuando hay conflicto, corte, diferencia, devolución, cancelación o sincronización.

## 4. Sistema de módulos compartidos

| ID | Módulo | Dueño lógico | Qué gobierna | Pantallas típicas |
| --- | --- | --- | --- | --- |
| `MOD-CORE` | Core Platform | plataforma | negocio, sucursales, usuarios, roles, terminales, auditoría | configuración, usuarios, permisos |
| `MOD-CATALOG` | Catalog & Pricing | comercial | productos, servicios, precios, unidades, listas, impuestos base | catálogo, checkout, compras |
| `MOD-CUSTOMERS` | Customers & Accounts | comercial | clientes, perfiles, cartera, historial, contratos | clientes, cobranza, pedidos |
| `MOD-SALES` | Sales & Checkout | operación | ventas, cotizaciones, pedidos, devoluciones, apartados | venta, pedidos, devoluciones |
| `MOD-INVENTORY` | Inventory Ledger | operación | stock, movimientos, conteos, reservas, transferencias | inventario, recepción, pedidos |
| `MOD-PROCUREMENT` | Procurement | operación | proveedores, órdenes de compra, recepción, costos | compras, recepción |
| `MOD-CASH` | Cash Management | operación | turnos, caja, arqueos, gastos, diferencias | caja, cortes |
| `MOD-PAYMENTS` | Payments & Credit | financiero | pagos, deuda, crédito, asignación, cobranza | cobranza, checkout, clientes |
| `MOD-SYNC` | Sync & Local-first | infraestructura | outbox, jobs, conflictos, checkpoints | estado sync, conflictos |
| `MOD-HARDWARE` | Hardware Adapters | infraestructura | lectores, impresoras, básculas, biometría, KDS, torniquetes | configuración, operación contextual |
| `MOD-FISCAL` | Fiscal Layer | compliance | CFDI, notas, timbrado, catálogos fiscales | facturación, fiscal |
| `MOD-ANALYTICS` | Analytics | dirección | KPIs, reportes, alertas, comparativos | dashboard, reportes |
| `MOD-PLUGINS` | Plugin Platform | plataforma | instalación, activación, permisos, slots, capacidades | plugin hub, target atlas |

## 5. Contrato de pantalla

Cada pantalla nueva debe usar esta ficha. Si no la llena, no entra. Así de simple, porque después vienen los fantasmas del scope creep a cobrar renta.

```yaml
screen_contract:
  id: PC-XX or TAB-XX
  name: string
  client: pc | tablet
  intent: task_view | table_view | workflow_view | dashboard_view | config_view | plugin_view
  primary_user: owner | admin | supervisor | cashier | operator | field_agent
  modules:
    - MOD-...
  plugin_slots:
    - slot.id
  required_permissions:
    - permission.key
  offline_policy: full | partial | read_only | online_required
  sync_events:
    emits:
      - event.name
    consumes:
      - event.name
  audit_events:
    - audit.name
  empty_state: what the user sees when no data exists
  error_state: what happens when something fails
  validation_notes: acceptance criteria
```

## 6. Contrato de plugin

Todo plugin debe declarar su existencia antes de tocar la UI.

```yaml
plugin_manifest:
  id: vertical-example
  name: string
  target_family: string
  version: semver
  depends_on:
    - MOD-CUSTOMERS
    - MOD-SALES
  extends:
    screens:
      - PC-10
      - TAB-10
    slots:
      - customer.profile.side_panel
      - order.workflow.extra_stage
  permissions:
    - plugin.example.use
  data_shapes:
    creates: []
    extends: []
  hardware_adapters: []
  fiscal_impact: none | optional | required
  offline_policy: full | partial | online_required
  analytics_cards: []
  migration_notes: string
  rollback_notes: string
```

### 6.1 Lo que un plugin tiene prohibido

- crear otra entidad equivalente a una core sin justificación;
- meter estados libres sin transición documentada;
- escribir directo en caja, inventario o pagos sin evento auditable;
- cambiar navegación base sin registrar impacto en PC y Tablet;
- depender de hardware específico sin adaptador;
- romper offline-first sin decirlo de frente.


## 7. Modelo de navegación Tablet

### 7.1 Shell táctil

```text
┌──────────────────────────────────────────────┐
│ Status bar: sucursal | caja | sync | usuario │
├──────────────────────────────────────────────┤
│ Context header: módulo + acción primaria     │
├──────────────────────────────────────────────┤
│                                              │
│  Canvas táctil: cards, flujo, escaneo, pasos │
│                                              │
├──────────────────────────────────────────────┤
│ Bottom nav: Inicio Venta Pedidos Caja Más    │
└──────────────────────────────────────────────┘
```

### 7.2 Regla de interacción

Tablet trabaja con pulgar, dedo, lector, cámara, NFC, biometría o hardware cercano. Todo debe poder hacerse con pocos pasos, botones grandes y confirmaciones claras.

- mínimo 44px visuales por área táctil;
- acciones críticas con confirmación;
- estados offline visibles;
- escaneo como primera clase;
- formularios cortos por pasos;
- tablas convertidas en cards;
- detalle como bottom sheet o side sheet.

## 8. Pantallas Tablet clave

## TAB-01 Inicio operativo

**Intent:** `dashboard_view` + `task_view`  
**Usuario principal:** cajero, operador, encargado  
**Objetivo:** arrancar turno y saber qué requiere atención inmediata.

### Módulos
- `MOD-CORE`
- `MOD-CASH`
- `MOD-SYNC`
- `MOD-SALES`
- `MOD-INVENTORY`
- `MOD-PLUGINS`

### Layout

```text
┌──────────────────────────────────────────────┐
│ PRISMA | Sucursal | Sync | Caja              │
├──────────────────────────────────────────────┤
│ Acción grande: Iniciar venta / Abrir caja    │
├──────────────────────────────────────────────┤
│ Cards rápidas                                │
│ - caja abierta/cerrada                       │
│ - pedidos pendientes                         │
│ - stock crítico                              │
│ - conflictos sync                            │
├──────────────────────────────────────────────┤
│ Accesos: Venta | Pedido | Cliente | Conteo   │
└──────────────────────────────────────────────┘
```

### Slots de plugin
- `home.quick_actions.vertical`
- `home.alerts.vertical`
- `home.status_cards.vertical`

### Offline
Debe funcionar con estado local. Si no hay internet, muestra acciones disponibles y cola pendiente.

---

## TAB-02 Venta rápida / Checkout táctil

**Intent:** `task_view`  
**Usuario principal:** cajero, vendedor, staff  
**Objetivo:** vender rápido con escaneo, búsqueda táctil, carrito visible y cobro simple.

### Layout

```text
┌──────────────────────────────────────────────┐
│ Venta | Cliente opcional | Lista precio      │
├──────────────────────────────────────────────┤
│ [Escanear / buscar producto]                 │
├──────────────────────────┬───────────────────┤
│ Catálogo cards           │ Carrito compacto  │
│ categorías / favoritos   │ total + pagar     │
└──────────────────────────┴───────────────────┘
```

### Slots de plugin
- `tablet.checkout.scan_handler`
- `tablet.checkout.product_card_badges`
- `tablet.checkout.payment_buttons`
- `tablet.checkout.vertical_prompts`

### Comportamientos
- Escaneo agrega al carrito.
- Long press abre detalle.
- Swipe opcional para quitar línea.
- Pago debe poder entrar en flujo de 3 pasos: total -> método -> confirmación.

---

## TAB-03 Pedidos / órdenes en piso

**Intent:** `workflow_view`  
**Usuario principal:** operador, vendedor, técnico, producción  
**Objetivo:** crear, avanzar y cerrar órdenes sin obligar al usuario a entender toda la administración.

### Layout

```text
┌──────────────────────────────────────────────┐
│ Pedidos | Hoy | Mis pendientes | Crear       │
├──────────────────────────────────────────────┤
│ Chips de estado: Nuevo / En proceso / Listo  │
├──────────────────────────────────────────────┤
│ Cards de orden                               │
│ #1023 Cliente | estado | próxima acción      │
│ #1024 Cliente | estado | alerta              │
├──────────────────────────────────────────────┤
│ Bottom sheet: detalle + avanzar estado       │
└──────────────────────────────────────────────┘
```

### Slots de plugin
- `tablet.order.card_vertical_badges`
- `tablet.order.next_action`
- `tablet.order.workflow_extra_steps`
- `tablet.order.capture_fields`

### Ejemplos
- Maquila: avanzar etapa, capturar lote, marcar merma.
- Taller: tomar foto, registrar diagnóstico, entregar equipo.
- Restaurante: mandar comanda, marcar listo.
- Distribución: entregar, cobrar, obtener firma.

---

## TAB-04 Cliente rápido / perfil operativo

**Intent:** `profile_view` + `task_view`  
**Usuario principal:** vendedor, recepción, acceso, cobranza  
**Objetivo:** buscar cliente, ver lo relevante y actuar rápido.

### Layout

```text
┌──────────────────────────────────────────────┐
│ Cliente | Buscar por nombre/teléfono/QR      │
├──────────────────────────────────────────────┤
│ Card cliente: nombre, tags, deuda, estado    │
├──────────────────────────────────────────────┤
│ Acciones: vender, cobrar, renovar, pedido    │
├──────────────────────────────────────────────┤
│ Historial compacto + plugin cards            │
└──────────────────────────────────────────────┘
```

### Slots de plugin
- `tablet.customer.status_card`
- `tablet.customer.primary_action`
- `tablet.customer.vertical_history`
- `tablet.customer.identity_scan`

### Regla
Tablet muestra lo necesario para actuar. PC muestra lo necesario para administrar. No metas formulario de 48 campos aquí, por favor, que el usuario está de pie y la vida ya lo golpeó suficiente.

---

## TAB-05 Inventario rápido / conteo / stock check

**Intent:** `task_view`  
**Usuario principal:** almacén, encargado, vendedor  
**Objetivo:** consultar stock, hacer conteos, ajustes controlados y movimientos rápidos.

### Layout

```text
┌──────────────────────────────────────────────┐
│ Inventario | Escanear | Conteo | Ajuste      │
├──────────────────────────────────────────────┤
│ Producto encontrado                          │
│ stock aquí / otras sucursales / reservado    │
├──────────────────────────────────────────────┤
│ Acciones: contar, apartar, transferir, alerta│
├──────────────────────────────────────────────┤
│ Movimiento reciente                          │
└──────────────────────────────────────────────┘
```

### Slots de plugin
- `tablet.inventory.scan_result_extensions`
- `tablet.inventory.count_rules`
- `tablet.inventory.item_vertical_fields`
- `tablet.inventory.hardware_scale_input`

### Offline
Conteos y movimientos permitidos offline solo si tienen folio local, usuario, terminal y cola sync.

---

## TAB-06 Recepción / compras operativas

**Intent:** `task_view` + `workflow_view`  
**Usuario principal:** almacén, encargado  
**Objetivo:** recibir mercancía, validar contra orden y mandar impacto al inventario.

### Layout

```text
┌──────────────────────────────────────────────┐
│ Recepción | OC abiertas | Escanear           │
├──────────────────────────────────────────────┤
│ Card proveedor / OC                         │
├──────────────────────────────────────────────┤
│ Líneas por recibir                           │
│ producto | esperado | recibido | diferencia  │
├──────────────────────────────────────────────┤
│ Confirmar recepción parcial / completa       │
└──────────────────────────────────────────────┘
```

### Slots de plugin
- `tablet.receiving.line_validation`
- `tablet.receiving.photo_evidence`
- `tablet.receiving.batch_expiry_capture`

---

## TAB-07 Caja táctil / corte simple

**Intent:** `task_view`  
**Usuario principal:** cajero, encargado  
**Objetivo:** abrir caja, registrar movimientos, hacer corte y explicar diferencias sin convertirlo en juicio penal, aunque a veces se lo ganen.

### Layout

```text
┌──────────────────────────────────────────────┐
│ Caja | Abierta por Alan | Desde 09:02        │
├──────────────────────────────────────────────┤
│ Resumen: efectivo | tarjeta | transferencias │
├──────────────────────────────────────────────┤
│ Acciones grandes: ingreso, retiro, gasto     │
├──────────────────────────────────────────────┤
│ Cerrar caja: conteo guiado por denominación  │
└──────────────────────────────────────────────┘
```

### Slots de plugin
- `tablet.cash.extra_tender_types`
- `tablet.cash.close_rules`
- `tablet.cash.shift_notes`

### Auditoría
Todo cierre registra usuario, terminal, hora, diferencia, explicación y evidencia opcional.

---

## TAB-08 Cobranza / pagos en campo

**Intent:** `task_view`  
**Usuario principal:** vendedor, repartidor, cobrador, encargado  
**Objetivo:** cobrar deuda, abonos, anticipos, membresías, pedidos o contratos desde Tablet.

### Layout

```text
┌──────────────────────────────────────────────┐
│ Cobranza | Buscar cliente / escanear pedido  │
├──────────────────────────────────────────────┤
│ Saldo pendiente / documentos / promesas      │
├──────────────────────────────────────────────┤
│ Registrar pago: método, monto, referencia    │
├──────────────────────────────────────────────┤
│ Recibo / comprobante / firma                 │
└──────────────────────────────────────────────┘
```

### Slots de plugin
- `tablet.collections.contract_balance`
- `tablet.collections.route_context`
- `tablet.collections.membership_due`
- `tablet.collections.signature_capture`

---

## TAB-09 Sync, actividad y soporte rápido

**Intent:** `state_view`  
**Usuario principal:** encargado, soporte, admin ligero  
**Objetivo:** mostrar qué está pendiente, qué falló y qué puede hacer el usuario sin meterse al motor.

### Layout

```text
┌──────────────────────────────────────────────┐
│ Estado del sistema | Online / Offline        │
├──────────────────────────────────────────────┤
│ Cola pendiente: ventas, pagos, inventario    │
├──────────────────────────────────────────────┤
│ Conflictos simples: resolver / escalar       │
├──────────────────────────────────────────────┤
│ Diagnóstico: terminal, impresora, lector     │
└──────────────────────────────────────────────┘
```

### Slots de plugin
- `tablet.sync.vertical_conflict_labels`
- `tablet.support.hardware_checks`
- `tablet.activity.plugin_events`

### Regla
No mostrar errores crípticos. Mostrar: qué pasó, qué se guardó, qué falta sincronizar y qué acción existe.

---

## TAB-10 Plugin Workspace / Target Runtime

**Intent:** `plugin_view` + `task_view`  
**Usuario principal:** operador del giro activo  
**Objetivo:** ejecutar capacidades verticales activas sin crear una app distinta por industria.

En Tablet, el módulo 10 no es una biblioteca técnica. Es el **workspace vivo del plugin activo**. Si el negocio es gym, aquí puede vivir check-in, renovaciones y acceso. Si es maquila, etapas de producción. Si es restaurante, mesas y comandas. Si es distribución, ruta y entrega. Pero todo usando slots y contratos, no aventando pantallas huérfanas.

### Layout base

```text
┌──────────────────────────────────────────────┐
│ Workspace | Plugin activo | Estado sync      │
├──────────────────────────────────────────────┤
│ Selector de modo: operar / revisar / cerrar  │
├──────────────────────────────────────────────┤
│ Cards del plugin                             │
│ - próxima acción                             │
│ - pendientes                                 │
│ - alertas                                    │
├──────────────────────────────────────────────┤
│ Acción primaria grande                       │
└──────────────────────────────────────────────┘
```

### Variantes runtime sin romper core

| Plugin | Qué muestra Tablet | Qué configura PC |
| --- | --- | --- |
| `vertical-memberships` | check-in, renovar, congelar, registrar asistencia | planes, vigencias, reglas de acceso |
| `vertical-light-production` | etapas, piezas, avance, merma, evidencia | workflow, estaciones, permisos |
| `vertical-hospitality` | mesas, comandas, estado cocina, dividir cuenta | menú, modifiers, KDS, áreas |
| `vertical-distribution` | ruta, entrega, cobro, firma, evidencia | rutas, cartera, zonas, políticas |
| `vertical-service-workshop` | diagnóstico, fotos, piezas, entrega | estados, garantías, técnicos |
| `vertical-perishables` | lote, caducidad, alerta, merma | reglas lote/caducidad, reportes |
| `vertical-rentals` | entrega, devolución, garantía, daño | calendarios, tarifas, depósitos |
| `vertical-events` | validar acceso, consumo, pulsera | boletaje, zonas, permisos |

### Slots de plugin
- `tablet.plugin.home_cards`
- `tablet.plugin.primary_action`
- `tablet.plugin.workflow_steps`
- `tablet.plugin.capture_widgets`
- `tablet.plugin.hardware_actions`
- `tablet.plugin.offline_queue`

### Estados de workspace

```text
inactive -> available -> configured -> active -> degraded -> blocked
```

### Degraded vs blocked

| Estado | Significa | Acción |
| --- | --- | --- |
| `degraded` | el plugin funciona parcialmente | permitir tareas seguras, avisar restricciones |
| `blocked` | el plugin no puede operar sin riesgo | bloquear acción, escalar a PC/admin |


## 12. Target Atlas nivel dios

Este atlas no es una lista de ocurrencias. Es la forma de evitar que PRISMA nazca como POS de tienda y luego lo quieran disfrazar de gym, maquila o clínica con cinta canela. Cada target se interpreta como paquete vertical encima del core, no como fork del producto.

### 12.1 Familias de target

| Familia | Subtargets posibles | Dominio dominante | Señal de compra | Plugin pack sugerido |
| --- | --- | --- | --- | --- |
| Retail básico | abarrotes, miscelánea, minisúper, papelería, boutique | ventas + inventario | necesita cobrar rápido y controlar stock | `vertical-retail-basic` |
| Retail por variantes | ropa, calzado, accesorios, cosméticos | catálogo + variantes | sufre con tallas, colores, combos | `vertical-retail-variants` |
| Retail pesado | ferretería, refaccionaria, materiales, autopartes | catálogo técnico + compatibilidades | búsqueda compleja y unidades raras | `vertical-retail-technical` |
| Perecederos | farmacia, alimentos, carnicería, cremería, panadería | lotes + caducidad | merma, regulación, fechas | `vertical-perishables` |
| Hospitality | restaurante, cafetería, bar sin alcohol, food court, dark kitchen | comandas + producción | mesas, cocina, tiempos | `vertical-hospitality` |
| Servicios con agenda | estética, barbería, clínica estética, consultorio, spa | citas + clientes | agenda, historial, pagos | `vertical-appointments` |
| Membresías | gym, club, cowork, escuela, academia | contratos recurrentes + acceso | renovaciones, asistencia, acceso | `vertical-memberships` |
| Talleres y reparación | mecánico, celulares, electrónica, bicicletas, motos | órdenes de servicio | seguimiento y evidencias | `vertical-service-workshop` |
| Maquila / producción ligera | maquila textil, empaque, ensamble, impresión, sublimación | órdenes + etapas + entregas | pedidos por etapa y producción | `vertical-light-production` |
| Distribución | rutas, preventa, reparto, almacén, mayoreo | pedidos + rutas + cartera | entrega, cobranza, clientes recurrentes | `vertical-distribution` |
| B2B comercial | mayoristas, distribuidores, proveedores locales | cotizaciones + crédito | cartera, listas de precio, límites | `vertical-b2b-sales` |
| Educación operativa | cursos, talleres, academias, capacitaciones | alumnos + pagos + asistencia | mensualidades y grupos | `vertical-education` |
| Salud administrativa | consultorios, ópticas, dental administrativo | expediente ligero + pagos | citas, clientes, historial | `vertical-health-admin` |
| Renta y reservas | renta de equipo, canchas, salones, mobiliario | reservas + garantías | disponibilidad y depósitos | `vertical-rentals` |
| Campo / agro ligero | insumos agrícolas, veterinaria, alimento animal | lotes + clientes + crédito | venta técnica y cartera | `vertical-agro-vet` |
| Construcción ligera | materiales, contratistas, obra chica | pedidos + entregas parciales | cotización, anticipo, entregas | `vertical-construction-supply` |
| Ecommerce híbrido | tienda física + online, catálogo social | inventario + fulfillment | sincronizar pedidos de canales | `vertical-omnichannel` |
| Eventos | boletaje, accesos, consumo, staff | acceso + caja + control | entradas, pulseras, consumo | `vertical-events` |
| Franquicias pequeñas | sucursales replicables | configuración + auditoría | estándar por sucursal | `vertical-franchise-lite` |
| Gobierno / institucional chico | cooperativas, cajas internas, comedores, almacenes | permisos + trazabilidad | control y auditoría | `vertical-institutional-lite` |

### 12.2 Capacidades pluginables por target

| Capacidad | Quién la usa | Debe vivir como | No debe hacer |
| --- | --- | --- | --- |
| venta rápida | retail, restaurante, eventos | extensión de `sales.checkout` | crear otro checkout paralelo |
| lotes/caducidad | farmacia, perecederos, agro | extensión de `inventory.ledger` | meter fechas en producto base sin política |
| membresías | gym, cowork, educación | extensión de `customers + contracts + payments` | volver cliente = miembro para todo el core |
| agenda/citas | servicios, salud admin, belleza | extensión de `orders + calendar` | meter calendario dentro de ventas |
| producción por etapas | maquila, impresión, taller | extensión de `orders + workflow` | crear estados libres sin máquina de estados |
| rutas y reparto | distribución, ecommerce híbrido | extensión de `orders + fulfillment` | ensuciar venta con logística permanente |
| compatibilidades | refaccionaria, ferretería técnica | extensión de `catalog.search` | duplicar productos por aplicación |
| recetas/insumos | restaurante, panadería | extensión de `inventory.consumption` | descontar stock mágico sin ledger |
| cartera/crédito | B2B, distribución, talleres | extensión de `payments + customer_account` | permitir deuda sin límite ni auditoría |
| acceso físico | gym, eventos, cowork | extensión de `hardware.adapters + identity` | acoplar torniquete al core |
| fiscal avanzado | cualquier negocio formal | extensión de `fiscal.layer` | contaminar checkout base con SAT |
| reportes verticales | todos | extensión de `analytics.registry` | modificar dashboards base por giro |

### 12.3 Regla brutal de sanidad

Si un target exige una pantalla nueva, primero se debe demostrar que no cabe en estas cuatro formas:

1. `task_view`: hacer una acción rápida.
2. `table_view`: consultar, filtrar y editar registros.
3. `workflow_view`: mover una orden por estados.
4. `dashboard_view`: entender salud, alertas y desempeño.

Si no cabe, se crea un nuevo patrón. Pero se documenta como patrón, no como capricho de giro. La diferencia entre arquitectura y tianguis es exactamente esa.


## 13. Matriz Tablet de pantallas contra módulos

| Pantalla | Core | Catalog | Customers | Sales | Inventory | Cash | Sync | Hardware | Fiscal | Plugins |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TAB-01 Inicio | yes | optional | optional | yes | yes | yes | yes | optional | no | yes |
| TAB-02 Venta | partial | yes | yes | yes | yes | yes | yes | yes | optional | yes |
| TAB-03 Pedidos | partial | yes | yes | yes | yes | partial | yes | optional | optional | yes |
| TAB-04 Cliente | partial | optional | yes | yes | optional | optional | yes | optional | optional | yes |
| TAB-05 Inventario | partial | yes | optional | optional | yes | no | yes | yes | no | yes |
| TAB-06 Recepción | partial | yes | optional | no | yes | no | yes | optional | optional | yes |
| TAB-07 Caja | yes | no | optional | yes | no | yes | yes | optional | optional | yes |
| TAB-08 Cobranza | partial | optional | yes | yes | optional | yes | yes | optional | optional | yes |
| TAB-09 Sync | yes | optional | optional | optional | optional | optional | yes | yes | no | yes |
| TAB-10 Workspace | yes | optional | optional | optional | optional | optional | yes | optional | optional | yes |

## 14. Reglas de evolución Tablet

### 14.1 Cuándo agregar pantalla nueva

Agregar pantalla nueva solo si el flujo requiere un modo mental diferente. Ejemplos aceptables:

- modo ruta con mapa y entregas secuenciales;
- modo producción con estación fija;
- modo cocina con comandas vivas;
- modo acceso con validación constante;
- modo inventario ciego para conteos auditados.

Si solo se requiere capturar un campo más, se agrega widget al slot existente. Nada de parir pantallas cada que aparece una ocurrencia.

### 14.2 Relación con PC

Todo plugin que aparezca como acción en Tablet debe tener en PC:

- configuración;
- permisos;
- auditoría;
- reportes mínimos;
- rollback o desactivación;
- impacto de sync.

## 15. Validación Tablet antes de construir

Checklist mínimo:

- [ ] Cada acción crítica cabe en flujo táctil corto.
- [ ] Cada pantalla declara offline policy.
- [ ] Cada captura importante emite evento auditable.
- [ ] Los botones principales son claros y grandes.
- [ ] No hay tablas densas disfrazadas de mobile.
- [ ] El usuario entiende qué está sincronizado y qué no.
- [ ] El plugin activo no reemplaza el core.
- [ ] Todo hardware pasa por adaptador.
- [ ] Toda deuda, pago, caja o inventario queda trazable.
- [ ] PC puede configurar y auditar lo que Tablet ejecuta.

## 16. Backlog sano para Tablet

### Now
- TAB-01 Inicio operativo
- TAB-02 Venta rápida
- TAB-05 Inventario rápido
- TAB-07 Caja táctil
- TAB-09 Sync/actividad
- TAB-10 Plugin Workspace mínimo

### Next
- TAB-03 Pedidos/órdenes
- TAB-04 Cliente rápido
- TAB-08 Cobranza
- TAB-06 Recepción

### Later
- modos especializados por plugin: ruta, cocina, producción, acceso, conteo ciego, agenda.

## 17. Criterio de calidad final

La versión Tablet está bien diseñada si permite:

1. operar rápido;
2. cobrar sin fricción;
3. capturar datos en campo;
4. funcionar offline con honestidad;
5. mostrar estado de sync;
6. trabajar con hardware sin casarse con marcas;
7. ejecutar plugins verticales;
8. mantener permisos y auditoría;
9. sincronizar con PC sin traducciones raras;
10. ser usable de pie, con prisa y con gente esperando.

Si requiere escritorio, mouse y paciencia de monje para vender un producto, fracasó. Tablet no es escritorio miniatura: es herramienta de batalla.
