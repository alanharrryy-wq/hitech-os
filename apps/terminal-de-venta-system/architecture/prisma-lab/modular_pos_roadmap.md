
# Roadmap modular para un POS más cabrón que SICAR

## Tesis
No conviene copiar SICAR tal cual. Conviene **tomar lo que sí resuelve bien** y rediseñar lo que públicamente se ve más frágil:
- operación local para no quedarse sin cobrar cuando se cae internet
- multicaja / multisucursal
- inventario, compras, ventas, caja, clientes, proveedores
- verticales por giro

Pero en vez de meter todo en un solo mole, la base debe quedar como **core + módulos + plugins de giro**.

---

## Qué debe ganarle a SICAR
1. **Modularidad real**  
   No “versiones especiales” pegadas con chicle. Un mismo núcleo con paquetes por giro.

2. **Modelo de datos canónico**  
   Un solo lenguaje para catálogo, inventario, ventas, caja y sync.

3. **Sync limpio**  
   Nada de sincronización opaca. Debe existir ledger, outbox, colas, versionado y resolución de conflictos.

4. **Offline-first bien hecho**  
   Seguir vendiendo sin internet, pero con reconciliación confiable.

5. **Hardware desacoplado**  
   Báscula, impresora, lector, biometría, torniquete, kitchen display y demás por adaptadores.

6. **Fiscal separado del core**  
   CFDI, SAT, timbrado y compliance como módulo enchufable.

7. **Plugins de giro**  
   Restaurante, gym, farmacia, ferretería, refaccionaria, boutique, taller, etc.

---

## Arquitectura recomendada

### Capa 1. Core Platform
Responsable de identidad, organización y permisos.

**Modelos base**
- Business
- Store
- Terminal
- User
- Role
- Permission
- UserRole
- UserStoreAccess
- Device
- AuditEvent

### Capa 2. Commercial Core
Lo que todo giro necesita para sobrevivir.

**Dominios**
- catálogo
- clientes
- proveedores
- compras
- inventario
- ventas
- pagos
- caja
- devoluciones
- gastos
- pricing
- impuestos base

### Capa 3. Operational Infrastructure
La parte que evita que el sistema se convierta en tamal de bugs.

**Servicios**
- outbox / event log
- importador masivo
- exportación
- attachments / images
- numbering / folios
- auditoría
- jobs programados
- configuración por sucursal
- observabilidad
- backups
- feature flags

### Capa 4. Vertical Plugins
Cada giro entra como módulo aparte, sin ensuciar el core.

**Ejemplos**
- retail-abarrotes
- retail-ferreteria
- retail-refaccionaria
- retail-farmacia
- hospitality-restaurante
- fitness-gym
- service-workshop

---

## Regla de oro de modularización
Cada módulo debe poder vivir como un zip separado con:

- `schema.patch.prisma` o extensión controlada
- migraciones propias
- seeds propias
- permisos propios
- endpoints/servicios propios
- pruebas propias
- documentación de impacto
- banderas de activación

Si un módulo no puede quitarse sin romper media base, entonces no es módulo, es pegoste.

---

## Núcleo canónico sugerido

### 1. Core Platform
**Objetivo:** identidad operativa y control de acceso.

**Submódulos**
- business-structure
- identity-access
- terminals-devices
- audit-trace

### 2. Catalog & Pricing
**Objetivo:** catálogo limpio y reutilizable entre giros.

**Entidades**
- Product
- Category
- Brand
- Barcode
- Uom
- ProductPresentation
- TaxRate
- PriceList
- ProductPrice
- Tag

**Notas**
- soportar unidad base y unidad de venta
- soportar venta fraccionada
- soportar presentaciones
- soportar equivalencias y compatibles

### 3. Inventory
**Objetivo:** ledger serio, no numeritos mágicos.

**Entidades**
- InventoryBalance
- InventoryMovement
- InventoryReservation
- InventoryCount
- InventoryCountLine
- StockTransfer
- StockTransferLine
- WarehouseLocation

**Notas**
- separar balance derivado del historial
- permitir conteos parciales/cíclicos
- reservar stock para pedidos
- soportar traspasos entre sucursales

### 4. Procurement
**Objetivo:** compras y recepción trazables.

**Entidades**
- Supplier
- PurchaseOrder
- PurchaseOrderLine
- GoodsReceipt
- GoodsReceiptLine
- SupplierInvoice

### 5. Sales & Checkout
**Objetivo:** vender rápido sin romper consistencia.

**Entidades**
- Customer
- Quote
- SalesOrder
- Sale
- SaleLine
- Payment
- PaymentAllocation
- Return
- ReturnLine

**Notas**
- venta en espera
- apartados / anticipos
- crédito cliente
- split payments
- descuentos por línea y ticket

### 6. Cash Management
**Objetivo:** que la caja cuadre y si no, que el sistema cante dónde valió madre.

**Entidades**
- CashSession
- CashMovement
- CashCount
- Shift
- Expense

### 7. Sync & Integration
**Objetivo:** multisucursal real.

**Entidades**
- OutboxEvent
- SyncJob
- SyncCheckpoint
- ConflictLog
- IntegrationEndpoint

**Notas**
- event sourcing completo no es obligatorio
- pero sí ledger + outbox + versionado por registro
- toda sincronización debe ser observable

### 8. Fiscal Layer
**Objetivo:** no contaminar el core con SAT desde día uno.

**Entidades**
- FiscalProfile
- Invoice
- CreditNote
- TaxDocument
- StampAttempt
- FiscalCatalogRef

---

## Plugins por giro

### A. Abarrotes / Retail general
**Necesita**
- báscula
- venta a granel
- promociones simples
- recargas / servicios
- mayoreo/menudeo
- etiquetas

### B. Ferretería / Refaccionaria
**Necesita**
- compatibles / equivalencias
- búsqueda por aplicación, medida o vehículo/equipo
- kits
- variantes fuertes
- unidades de compra y venta

### C. Farmacia
**Necesita**
- lotes
- caducidades
- sustitutos
- control por clasificación
- alertas sanitarias
- recetas y restricciones como módulo aparte si aplica

### D. Restaurante
**Necesita**
- mapa de mesas
- comandas
- kitchen display
- recetas
- modifiers
- tiempos
- dividir cuenta
- consumo de insumos por receta

### E. Gym
**Necesita**
- membresías
- vigencias
- control de acceso
- biometría
- asistencias
- renovaciones

### F. Taller / Servicio
**Necesita**
- órdenes de servicio
- diagnóstico
- seguimiento de estatus
- piezas y mano de obra
- evidencias/fotos

---

## Roadmap re-hecho

## Fase 0. Discovery serio por giros
Antes de tocar Prisma, arma una matriz con:
- proceso de venta
- proceso de inventario
- excepciones
- hardware
- fiscal
- sync
- permisos
- reportes críticos

**Salida**
- matriz por giro
- mapa de entidades comunes vs exclusivas
- backlog por dominio

---

## Fase 1. Prisma Core Foundation
**Entregable principal:** `prisma-core-platform.zip`

**Incluye**
- Business, Store, Terminal, User, Role, Permission
- auditoría base
- configuración por sucursal
- seeds base
- migración inicial
- tests de integridad

**No incluye aún**
- ventas
- inventario complejo
- SAT

---

## Fase 2. Catalog & Pricing Foundation
**Entregable:** `prisma-catalog-pricing.zip`

**Incluye**
- productos
- categorías
- barcodes
- listas de precios
- impuestos base
- unidades/presentaciones
- venta fraccionada

**Clave**
Esta fase debe dejar resuelto desde el inicio el maldito tema de “compro por caja y vendo por pieza / kilo / gramo”.

---

## Fase 3. Inventory Ledger
**Entregable:** `prisma-inventory.zip`

**Incluye**
- balances
- movimientos
- reservas
- conteos
- ajustes
- transferencias internas

**Meta**
Poder reconstruir cualquier existencia a partir del historial.

---

## Fase 4. Procurement
**Entregable:** `prisma-procurement.zip`

**Incluye**
- proveedores
- órdenes de compra
- recepción
- impacto en costos y stock

---

## Fase 5. Sales POS
**Entregable:** `prisma-sales-pos.zip`

**Incluye**
- clientes
- cotizaciones/pedidos si aplican
- ventas
- líneas
- pagos
- devoluciones
- apartados/anticipos
- crédito

**Meta**
Ya poder operar una tienda completa.

---

## Fase 6. Cash Management
**Entregable:** `prisma-cash-management.zip`

**Incluye**
- apertura/cierre
- movimientos de caja
- arqueos
- diferencias
- gastos
- cortes

---

## Fase 7. Sync & Local-first
**Entregable:** `prisma-sync-outbox.zip`

**Incluye**
- outbox
- colas
- checkpoints
- conflictos
- replicación entre sucursales

**Meta**
Superar el dolor clásico de muchos POS: sync opaco, lento o caprichoso.

---

## Fase 8. Hardware Integration Layer
**Entregable:** `prisma-hardware-adapters.zip`

**Incluye contratos para**
- impresoras
- básculas
- lectores
- cajones
- biometría
- torniquetes
- pantallas de cocina

**Nota**
El hardware no debe vivir en el schema. Debe vivir en adaptadores y contratos.

---

## Fase 9. Vertical Packs
A partir de aquí salen packs por giro:

1. `vertical-retail-abarrotes.zip`
2. `vertical-retail-ferreteria.zip`
3. `vertical-retail-refaccionaria.zip`
4. `vertical-retail-farmacia.zip`
5. `vertical-hospitality-restaurante.zip`
6. `vertical-fitness-gym.zip`
7. `vertical-service-workshop.zip`

---

## Fase 10. Fiscal & Compliance
**Entregable:** `prisma-fiscal-invoicing.zip`

**Incluye**
- CFDI
- notas de crédito
- intentos de timbrado
- catálogos fiscales
- auditoría fiscal

**Regla**
Esto entra cuando el core comercial ya esté sólido. Meter SAT demasiado temprano es como querer pintar la casa cuando todavía estás colando la losa.

---

## Fase 11. Analytics & Admin
**Entregable:** `prisma-analytics-reporting.zip`

**Incluye**
- dashboards
- KPIs por sucursal
- rentabilidad
- rotación
- merma
- vendedor
- caja
- compras
- aging de cartera

---

## Cómo sí le ganas a SICAR
No se le gana nomás por meter más botones. Se le gana si el sistema sale con estas propiedades:

- modelo canónico limpio
- verticalización real
- local-first con sync observable
- migraciones seguras
- pruebas por módulo
- hardware desacoplado
- fiscal desacoplado
- permisos granulares
- mejor trazabilidad
- APIs y contratos claros
- posibilidad de headless / web / desktop / tablet sin reventar la base

---

## Orden recomendado de construcción inmediata
1. cerrar **matriz de giros**
2. pulir **schema canónico**
3. sacar `prisma-core-platform.zip`
4. sacar `prisma-catalog-pricing.zip`
5. sacar `prisma-inventory.zip`
6. sacar `prisma-sales-pos.zip`
7. sacar `prisma-sync-outbox.zip`
8. luego verticales

---

## Siguiente paso recomendado
El siguiente paso correcto no es aventarse a escribir todo el schema final de una.  
El siguiente paso correcto es hacer dos cosas:

1. **Matriz de capacidades por giro**  
2. **Primer zip ejecutable: `prisma-core-platform.zip`**

Porque si no, acabas construyendo un monstruo con 400 campos que nadie entiende. Un software así queda como cableado de vecindad: medio funciona, pero nadie lo quiere tocar.
