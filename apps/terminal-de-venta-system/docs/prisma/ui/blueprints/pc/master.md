# PRISMA UI PC Master Blueprint v3

> Documento maestro heredado y promovido a vista de entrada modular.

# PRISMA UI Blueprint PC - Nivel Dios v2.0

**Cliente:** PC / Desktop / Web Admin Console  
**Fecha:** 2026-04-25  
**Estado:** Blueprint maestro vivo  
**Hermano obligatorio:** `prisma_ui_tablet_blueprint_nivel_dios_v2.md`  
**Objetivo:** diseñar la experiencia PC como centro de mando completo para operar, configurar, auditar, extender y escalar PRISMA sin convertirlo en mole de pantallas.

---

## 1. Decisión base

La versión PC de PRISMA no debe ser solamente "la versión grande" de Tablet. PC es el **centro de mando**: administra, configura, analiza, resuelve conflictos y prepara la operación. Tablet es el brazo rápido en piso, mostrador, almacén, ruta o acceso.

En PC se ven más datos, más estados, más filtros, más auditoría y más gobierno. Si Tablet es el machete para abrir camino, PC es el mapa, la radio y el jefe de cuadrilla diciendo por dónde no meterse al pantano.


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


## 7. Modelo de navegación PC

### 7.1 Shell principal

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Topbar: negocio / sucursal / sync / caja / usuario / búsqueda global          │
├───────────────┬──────────────────────────────────────────────────────────────┤
│ Sidebar        │ Header de módulo: título, estado, acciones, filtros rápidos │
│               ├──────────────────────────────────────────────────────────────┤
│ 01 Dashboard   │ Contenido principal: tabla, dashboard, workflow o editor     │
│ 02 Ventas      │                                                              │
│ 03 Pedidos     │ Panel derecho contextual: detalle, auditoría, plugin slots   │
│ 04 Clientes    │                                                              │
│ 05 Inventario  │ Footer discreto: versión, eventos pendientes, health         │
│ 06 Compras     │                                                              │
│ 07 Caja        │                                                              │
│ 08 Reportes    │                                                              │
│ 09 Admin       │                                                              │
│ 10 Plugins     │                                                              │
└───────────────┴──────────────────────────────────────────────────────────────┘
```

### 7.2 Regla de densidad

PC puede mostrar tablas densas, filtros avanzados, edición masiva y paneles laterales. Pero densidad no significa aventar datos como puesto de chácharas. Cada pantalla debe tener:

- una acción primaria;
- un estado visible;
- una tabla o canvas principal;
- un panel de detalle;
- un slot de plugin controlado;
- una ruta de auditoría.

## 8. Pantallas PC clave

## PC-01 Dashboard de mando

**Intent:** `dashboard_view`  
**Usuario principal:** dueño, admin, supervisor  
**Objetivo:** ver salud general del negocio y detectar dónde se está torciendo la operación.

### Módulos
- `MOD-ANALYTICS`
- `MOD-SALES`
- `MOD-CASH`
- `MOD-INVENTORY`
- `MOD-SYNC`
- `MOD-PLUGINS`

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Dashboard | Hoy / Semana / Mes | Sucursal | Comparar                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ KPI Ventas │ KPI Caja │ KPI Inventario │ KPI Sync │ KPI Cartera               │
├───────────────────────────────┬──────────────────────────────────────────────┤
│ Tendencia ventas/categorías   │ Alertas críticas                            │
│                               │ - caja con diferencia                       │
│                               │ - productos bajo mínimo                     │
│                               │ - conflictos sync                           │
├───────────────────────────────┴──────────────────────────────────────────────┤
│ Actividad reciente + acciones recomendadas                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Slots de plugin
- `dashboard.kpi.extra_cards`
- `dashboard.alerts.vertical`
- `dashboard.recommendations.vertical`

### No negociable
El dashboard no debe ser mural de gráficas para impresionar al primo. Debe responder: **qué pasó, qué está mal, qué hago ahora**.

---

## PC-02 Ventas y checkout desktop

**Intent:** `task_view` + `table_view`  
**Usuario principal:** cajero avanzado, supervisor, admin  
**Objetivo:** operar ventas completas con búsqueda poderosa, carrito claro, pagos y control de excepciones.

### Módulos
- `MOD-SALES`
- `MOD-CATALOG`
- `MOD-CUSTOMERS`
- `MOD-PAYMENTS`
- `MOD-CASH`
- `MOD-HARDWARE`

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Venta | Terminal | Lista precio | Cliente | Estado caja                       │
├───────────────────────────────┬──────────────────────────────────────────────┤
│ Buscador productos/servicios  │ Carrito                                      │
│ Tabla resultados              │ líneas, descuentos, impuestos, notas         │
│ filtros rápidos               │                                              │
├───────────────────────────────┼──────────────────────────────────────────────┤
│ Cliente / historial / deuda   │ Totales + pagos + acciones                   │
└───────────────────────────────┴──────────────────────────────────────────────┘
```

### Slots de plugin
- `checkout.product_result.badges`
- `checkout.cart.line_extensions`
- `checkout.payment.methods`
- `checkout.customer.rules`

### Políticas
- **Offline:** completo si catálogo, precios y caja están disponibles localmente.
- **Sync:** emite `sale.created`, `payment.received`, `inventory.reserved_or_deducted`.
- **Auditoría:** descuento manual, cancelación, devolución, cambio de precio, venta a crédito.

---

## PC-03 Pedidos, órdenes y workflow comercial

**Intent:** `workflow_view`  
**Usuario principal:** admin, operaciones, supervisor  
**Objetivo:** manejar cotizaciones, pedidos, órdenes de servicio, producción ligera o entrega por etapas sin crear pantallas distintas por giro.

### Estados base

```text
draft -> quoted -> confirmed -> in_progress -> ready -> delivered -> closed
                         └──────────── cancelled / blocked ───────────────┘
```

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Pedidos | Kanban / Lista / Calendario | filtros por estado                    │
├───────────────┬────────────────────────────────────┬─────────────────────────┤
│ Estados       │ Lista/Kanban de órdenes            │ Detalle orden           │
│ draft         │                                    │ cliente, líneas, pagos  │
│ confirmed     │                                    │ timeline, archivos      │
│ in_progress   │                                    │ plugin slot workflow    │
└───────────────┴────────────────────────────────────┴─────────────────────────┘
```

### Slots de plugin
- `order.workflow.stages`
- `order.detail.vertical_fields`
- `order.timeline.extra_events`
- `order.actions.vertical`

### Ejemplos sin romper core
- Maquila agrega etapas de producción.
- Taller agrega diagnóstico y evidencias.
- Restaurante agrega preparación y comandas.
- Distribución agrega ruta y entrega parcial.

---

## PC-04 Clientes, cartera y contratos

**Intent:** `table_view` + `profile_view`  
**Usuario principal:** ventas, admin, cobranza  
**Objetivo:** centralizar clientes, historial, crédito, contratos, membresías, garantías y relación comercial.

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Clientes | Segmentos | Deuda | Activos | Riesgo                               │
├───────────────────────────────┬──────────────────────────────────────────────┤
│ Tabla clientes                │ Perfil del cliente                           │
│ nombre, teléfono, RFC, deuda  │ datos, historial, cartera, permisos          │
│ tags, segmento, última compra │ plugins: membresía, expediente, contrato     │
└───────────────────────────────┴──────────────────────────────────────────────┘
```

### Slots de plugin
- `customer.profile.summary_cards`
- `customer.profile.contracts`
- `customer.profile.vertical_history`
- `customer.actions.vertical`

### Invariantes
- Cliente es cliente. Miembro, paciente, alumno, socio o mayorista son roles/extensiones, no entidades paralelas.
- Toda deuda debe pertenecer a cuenta, venta, pedido o contrato auditable.

---

## PC-05 Inventario maestro y ledger

**Intent:** `table_view` + `audit_view`  
**Usuario principal:** inventario, admin, compras  
**Objetivo:** controlar existencias reales por historial, no por numerito mágico.

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Inventario | Stock | Movimientos | Conteos | Transferencias | Reservas        │
├───────────────────────────────┬──────────────────────────────────────────────┤
│ Tabla productos/ubicaciones   │ Detalle stock                                 │
│ stock, mínimo, reservado      │ ledger, ajustes, conteos, plugin fields       │
├───────────────────────────────┴──────────────────────────────────────────────┤
│ Timeline de movimientos + explicación de balance                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Slots de plugin
- `inventory.item.badges`
- `inventory.ledger.extra_columns`
- `inventory.count.validation_rules`
- `inventory.alerts.vertical`

### Plugins esperados
- lotes y caducidad;
- tallas y colores;
- equivalencias;
- recetas/insumos;
- seriales;
- ubicación por almacén.

---

## PC-06 Compras, proveedores y recepción

**Intent:** `workflow_view` + `table_view`  
**Usuario principal:** compras, admin, almacén  
**Objetivo:** conectar abasto, recepción, costos e inventario sin capturas dobles.

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Compras | Proveedores | OC | Recepciones | Facturas proveedor                 │
├───────────────────────────────┬──────────────────────────────────────────────┤
│ Lista OC / recepción          │ Detalle                                      │
│ estado, proveedor, fecha      │ líneas, costos, recepción parcial, impacto   │
└───────────────────────────────┴──────────────────────────────────────────────┘
```

### Slots de plugin
- `procurement.receipt.validation`
- `supplier.profile.vertical_fields`
- `purchase_order.line_extensions`

### Estados base
`draft -> sent -> partially_received -> received -> closed -> cancelled`

---

## PC-07 Caja, turnos y auditoría de dinero

**Intent:** `task_view` + `audit_view`  
**Usuario principal:** cajero, supervisor, admin  
**Objetivo:** abrir, operar, cerrar, auditar y explicar diferencias de caja.

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Caja | Sesión actual | Cortes | Diferencias | Gastos                           │
├───────────────────────────────┬──────────────────────────────────────────────┤
│ Resumen efectivo/tarjeta      │ Acciones: retiro, ingreso, gasto, corte      │
│ movimientos recientes         │                                              │
├───────────────────────────────┴──────────────────────────────────────────────┤
│ Auditoría: quién hizo qué, cuándo, desde qué terminal                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Slots de plugin
- `cash.session.extra_totals`
- `cash.close.validation_rules`
- `cash.audit.vertical_context`

### Eventos
- `cash.opened`
- `cash.movement.created`
- `cash.closed`
- `cash.discrepancy.flagged`

---

## PC-08 Reportes, analytics y decisiones

**Intent:** `dashboard_view` + `report_view`  
**Usuario principal:** dueño, dirección, admin  
**Objetivo:** convertir operación en decisión.

### Reportes base
- ventas por periodo, sucursal, usuario, categoría;
- utilidad estimada y margen;
- rotación y merma;
- caja y diferencias;
- compras y proveedores;
- cartera y aging;
- rendimiento por plugin vertical.

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Reportes | Biblioteca | Favoritos | Exportar                                  │
├───────────────┬────────────────────────────────────┬─────────────────────────┤
│ Categorías    │ Vista reporte / gráfica            │ Filtros y explicación   │
│ ventas        │                                    │ qué mide / qué no mide  │
│ inventario    │                                    │                          │
│ cartera       │                                    │                          │
└───────────────┴────────────────────────────────────┴─────────────────────────┘
```

### Slots de plugin
- `analytics.report.registry`
- `analytics.kpi.vertical`
- `analytics.export.format`

---

## PC-09 Administración, seguridad y configuración

**Intent:** `config_view`  
**Usuario principal:** owner, admin técnico  
**Objetivo:** gobernar usuarios, permisos, sucursales, terminales, feature flags, hardware, fiscal y reglas generales.

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Admin | Organización | Usuarios | Permisos | Dispositivos | Fiscal | Flags     │
├───────────────────────────────┬──────────────────────────────────────────────┤
│ Menú configuración            │ Formulario / tabla / editor                  │
│                               │ Validación, preview de impacto, auditoría    │
└───────────────────────────────┴──────────────────────────────────────────────┘
```

### Reglas
- Cambios de permisos requieren auditoría.
- Cambios fiscales requieren versión y prueba.
- Cambios de hardware se registran por adaptador.
- Feature flags deben mostrar impacto en PC y Tablet.

---

## PC-10 Plugin Studio + Target Atlas

**Intent:** `plugin_view`  
**Usuario principal:** owner, admin, producto, integrador  
**Objetivo:** instalar, activar, configurar, auditar y gobernar plugins por giro sin contaminar el core.

Esta es la pantalla que evita que PRISMA se vuelva monstruo. Aquí se decide qué capacidades existen, en qué sucursales aplican, qué pantallas extienden, qué permisos crean, qué datos tocan y cómo se desinstalan si se portan como borracho en boda.

### Layout

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Plugin Studio | Activos | Marketplace interno | Target Atlas | Validación      │
├───────────────┬────────────────────────────────────┬─────────────────────────┤
│ Familias      │ Plugins / targets                  │ Panel de contrato       │
│ retail        │ - retail-basic                     │ dependencies            │
│ memberships   │ - memberships                      │ slots usados            │
│ production    │ - light-production                 │ permisos                │
│ distribution  │ - distribution                     │ offline/sync/fiscal     │
└───────────────┴────────────────────────────────────┴─────────────────────────┘
```

### Subvistas

| Subvista | Para qué sirve | Resultado |
| --- | --- | --- |
| `Installed` | ver plugins activos | saber qué toca cada plugin |
| `Target Atlas` | explorar industrias posibles | elegir vertical sin improvisar |
| `Capability Matrix` | comparar necesidades por giro | decidir si va core o plugin |
| `Slot Inspector` | ver dónde se monta cada plugin | evitar duplicidad |
| `Validation Gate` | revisar manifiesto antes de activar | bloquear pegostes |
| `Rollback Plan` | saber cómo desactivar | no quedar casado con errores |

### Contrato visual del plugin

```text
Plugin Card
├─ identidad: nombre, familia, versión, estado
├─ dependencias: módulos requeridos
├─ impacto UI: pantallas y slots que toca
├─ impacto datos: shapes que extiende
├─ impacto operación: offline, sync, hardware
├─ impacto negocio: reportes y permisos
└─ salud: errores, migraciones, eventos recientes
```

### Estados de plugin

```text
draft -> validated -> installed -> enabled -> configured -> active
                       └──────── disabled -> archived ────────┘
```

### Permisos críticos
- `plugins.view`
- `plugins.install`
- `plugins.configure`
- `plugins.enable_disable`
- `plugins.rollback`
- `plugins.audit`


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


## 13. Matriz PC de pantallas contra módulos

| Pantalla | Core | Catalog | Customers | Sales | Inventory | Cash | Sync | Hardware | Fiscal | Plugins |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PC-01 Dashboard | yes | yes | yes | yes | yes | yes | yes | partial | partial | yes |
| PC-02 Ventas | partial | yes | yes | yes | yes | yes | yes | yes | optional | yes |
| PC-03 Pedidos | partial | yes | yes | yes | yes | partial | yes | optional | optional | yes |
| PC-04 Clientes | partial | optional | yes | yes | optional | optional | yes | optional | optional | yes |
| PC-05 Inventario | partial | yes | optional | optional | yes | no | yes | optional | no | yes |
| PC-06 Compras | partial | yes | optional | no | yes | no | yes | optional | optional | yes |
| PC-07 Caja | yes | no | optional | yes | no | yes | yes | optional | optional | yes |
| PC-08 Reportes | yes | yes | yes | yes | yes | yes | yes | optional | optional | yes |
| PC-09 Admin | yes | partial | partial | partial | partial | partial | yes | yes | yes | yes |
| PC-10 Plugins | yes | partial | partial | partial | partial | partial | yes | yes | yes | yes |

## 14. Reglas de evolución PC

### 14.1 Cuándo agregar pantalla nueva

Agregar pantalla nueva solo si:

1. el usuario principal cambia;
2. la intención cambia;
3. el patrón actual no permite completar el flujo;
4. el plugin no puede vivir en slot sin romper claridad;
5. hay permisos o auditoría que justifican separación.

Si solo cambia un campo, una columna o una validación, se agrega slot o configuración. No pantalla nueva. No vamos a criar pantallas como conejos con WiFi.

### 14.2 Versionado recomendado

| Cambio | Versión doc | Requiere cambio en Tablet | Ejemplo |
| --- | --- | --- | --- |
| corrección textual | patch | no | aclarar copy |
| nuevo slot | minor | yes, si aplica | `customer.profile.contracts` |
| nuevo plugin target | minor | yes | `vertical-rentals` |
| nuevo patrón de pantalla | major | yes | `route_view` |
| cambio de estado core | major | yes | nuevo estado de pedido |

## 15. Validación PC antes de construir

Checklist mínimo:

- [ ] Cada pantalla tiene contrato lleno.
- [ ] Cada acción crítica tiene permiso.
- [ ] Cada flujo con dinero emite auditoría.
- [ ] Inventario usa ledger, no balance mágico.
- [ ] Checkout declara offline policy.
- [ ] Plugin Studio bloquea plugins sin manifiesto.
- [ ] Todo plugin declara impacto en Tablet.
- [ ] Hardware entra por adaptadores.
- [ ] Fiscal no contamina checkout base.
- [ ] Dashboard responde qué pasó, qué está mal y qué sigue.

## 16. Backlog sano para PC

### Now
- PC-01 Dashboard de mando
- PC-02 Ventas desktop
- PC-05 Inventario ledger
- PC-09 Administración base
- PC-10 Plugin Studio mínimo

### Next
- PC-03 Pedidos workflow
- PC-04 Clientes/cartera
- PC-07 Caja/auditoría
- PC-08 Reportes base

### Later
- PC-06 Compras avanzadas
- reportes verticales por plugin
- comparativos multisucursal profundos
- configurador visual de workflows

## 17. Criterio de calidad final

La versión PC está bien diseñada si permite:

1. vender;
2. controlar;
3. configurar;
4. auditar;
5. extender;
6. resolver conflictos;
7. crecer por giro;
8. sincronizar con Tablet sin traducciones raras;
9. apagar un plugin sin romper el core;
10. explicar al usuario qué pasó cuando algo falla.

Si no cumple eso, no es centro de mando: es un Excel con maquillaje y complejo de grandeza.
