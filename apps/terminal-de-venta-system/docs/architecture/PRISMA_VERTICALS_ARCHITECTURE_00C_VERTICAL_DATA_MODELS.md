# PRISMA_VERTICALS_ARCHITECTURE_00C_VERTICAL_DATA_MODELS

**Paquete:** `PRISMA_VERTICALS_ARCHITECTURE_00C_VERTICAL_DATA_MODELS`  
**Version:** `0.3.0`  
**Estado:** arquitectura canonica de modelos de datos multi-giro  
**Fecha:** 2026-04-29  
**Raiz esperada:** `apps/terminal-de-venta-system`  
**Idioma visible:** `es-MX`  

## 0. Decision principal

PRISMA no debe escalar agregando columnas al azar al modelo comun. Ese camino convierte `Product` en tamal de cables: un dia guarda precio, al siguiente mesa, receta, talla, lote, mecanico, propina y nombre del perro del cliente. Bonito no queda. Mantenible menos.

La decision canonica es esta:

> **Core modela la operacion comun. Las verticales modelan diferencias reales. Los contratos definen los limites. Los eventos registran la verdad operacional.**

Este paquete define el mapa de datos para que nuevos giros entren como extensiones gobernadas, no como remiendos pegados al nucleo.

## 1. Objetivos

1. Proteger el nucleo comun POS/backoffice.
2. Permitir que cada giro agregue entidades propias sin contaminar `Product`, `Sale`, `SaleLine`, `Payment` o `StockMovement`.
3. Definir que vive en Tablet, que vive en PC y que debe compartirse.
4. Definir reglas para migraciones futuras sin romper instalaciones existentes.
5. Dejar criterios claros para validar nuevos modelos de datos verticales.

## 2. Reglas madre

- Tablet puede operar datos locales necesarios para vender.
- PC puede gobernar datos profundos, auditoria, compras, recepcion, reabasto y analitica.
- Shared Kernel no es bodega de modelos. Solo acepta contratos comunes estables.
- Una entidad vertical no debe volverse obligatoria para todos los giros.
- Si un dato solo existe para un giro, vive en la extension de ese giro.
- Si un dato afecta dinero, inventario, cliente, caja, permiso o auditoria, genera evento.
- Si un dato afecta venta local, debe tener representacion local segura en Tablet.

## 3. Anti-patron que se prohibe

No crear un `Product` universal con campos como:

```text
lotNumber, prescriptionRequired, tableNumber, serviceDuration, appointmentId,
repairOrderId, technicianId, size, color, routeStopId, kitchenStatus, scaleWeight
```

Eso parece rapidez, pero es deuda con brillantina. Cada vertical debe extender donde corresponde.

## 4. Nucleo comun de entidades

Estas entidades son la columna comun. Pueden tener relaciones con extensiones, pero no absorber sus campos especializados.

| Entidad | Responsabilidad | Regla de frontera |
|---|---|---|
| `Business` | Identidad del negocio, regimen operativo, paquetes activos y politicas base. | Mantener estable y minimo; especializacion fuera del core. |
| `Terminal` | Dispositivo autorizado para operar localmente y generar eventos. | Mantener estable y minimo; especializacion fuera del core. |
| `Operator` | Persona o rol que ejecuta acciones sensibles en Tablet o PC. | Mantener estable y minimo; especializacion fuera del core. |
| `Shift` | Turno de caja local con apertura, cierre, cortes y resumen. | Mantener estable y minimo; especializacion fuera del core. |
| `Product` | Articulo vendible fisico base; no debe absorber servicios, mesas, recetas ni reparaciones. | Solo articulo fisico vendible base; servicios, menus, variantes y lotes se enlazan como extension. |
| `Barcode` | Codigo de lectura asociado a producto, variante o unidad de venta. | Mantener estable y minimo; especializacion fuera del core. |
| `PriceRule` | Regla basica de precio vigente, con alcance por negocio, terminal o vertical. | Mantener estable y minimo; especializacion fuera del core. |
| `Sale` | Ticket o venta cerrable localmente por Tablet. | Mantener estable y minimo; especializacion fuera del core. |
| `SaleLine` | Linea de venta con producto, servicio o item verticalizado normalizado. | Puede referenciar un item vendible normalizado; los detalles verticales viven en metadata gobernada o extension. |
| `Payment` | Registro de metodo, monto, referencia y estado de pago. | No guarda reglas fiscales profundas ni proveedor de pago como dependencia dura. |
| `StockSnapshot` | Foto operativa de existencia disponible. | Mantener estable y minimo; especializacion fuera del core. |
| `StockMovement` | Movimiento de inventario trazable. | No interpreta cocina, cita o reparacion; solo registra movimiento de inventario cuando existe inventario. |
| `Return` | Operacion de devolucion total o parcial. | Mantener estable y minimo; especializacion fuera del core. |
| `OutboxEvent` | Evento local pendiente, enviado, fallido o reconocido. | No guarda payload sin contrato; cada topic debe estar versionado. |
| `AuditEntry` | Rastro de accion sensible con actor, antes/despues y razon. | Mantener estable y minimo; especializacion fuera del core. |
| `ExportBatch` | Paquete de datos exportado localmente. | Mantener estable y minimo; especializacion fuera del core. |

## 5. Tipos de extension vertical

Las extensiones se clasifican por impacto operativo.

| Tipo | Uso | Puede vivir en Tablet | Debe vivir en PC | Ejemplo |
|---|---|---:|---:|---|
| `sale_extension` | Agrega datos a una venta o linea | Si, si afecta cobro | Si | propina, comanda, peso |
| `catalog_extension` | Especializa producto/servicio | Parcial | Si | lote, variante, menu item |
| `workflow_extension` | Agrega flujo propio | Si, si opera mostrador | Si | cita, mesa, orden de trabajo |
| `inventory_extension` | Cambia control de existencia | Parcial | Si | lotes, tallas, unidades variables |
| `compliance_extension` | Control legal/sensible | Solo lectura o captura minima | Si | receta, controlado, auditoria |
| `analytics_extension` | KPI o reporte especifico | No obligatorio | Si | venta por mesa, comision, merma por lote |

## 6. Politica de almacenamiento

1. **Core first:** si el dato aplica a todos los giros, puede entrar a core.
2. **Extension first:** si aplica a uno o pocos giros, entra como extension.
3. **Tablet minimal:** Tablet solo guarda lo necesario para operar y recuperarse offline.
4. **PC authoritative:** PC mantiene configuracion profunda, historicos grandes y resolucion de conflictos.
5. **Event sourced enough:** no se requiere event sourcing puro, pero toda accion sensible deja evento.

## 7. Patron de relacion recomendado

```text
Sale
  -> SaleLine
    -> SellableRef
       -> Product | Service | MenuItem | RepairLabor | WeightedItem
    -> VerticalLineExtension opcional

Product
  -> Barcode
  -> StockSnapshot
  -> VerticalCatalogExtension opcional
```

El nucleo no necesita saber todos los detalles. Necesita saber cobrar, registrar, auditar y sincronizar.

## 8. Matriz de verticales y entidades especializadas

| Vertical | Principio de datos | Extensiones principales | Prohibido meter al core |
|---|---|---|---|
| `convenience` | Productos rapidos, codigos de barra, stock simple, cortes y ventas de alto ritmo. | `ShelfLocation`, `QuickPriceOverride`, `SimplePromotion`, `LowStockSignal` | `tableNumber`, `appointmentTime`, `prescriptionId`, `repairOrderId` |
| `restaurant` | Venta puede ser consumo abierto; mesas, comandas y cocina son extension, no core POS. | `Table`, `DiningSession`, `KitchenTicket`, `MenuModifier`, `TipAllocation` | `prescriptionId`, `sizeColorMatrix`, `serialNumber`, `routeStopId` |
| `pharmacy` | Control sensible por lote, caducidad, receta y restriccion; no convertir cada producto en expediente medico. | `Lot`, `ExpirationPolicy`, `PrescriptionReference`, `ControlledProductFlag`, `SubstitutionRule` | `tableNumber`, `appointmentTime`, `repairLaborHours`, `colorSizeGrid` |
| `beauty` | Vende servicios, citas y comisiones; inventario de producto existe pero no manda todo el negocio. | `Service`, `Appointment`, `StaffCommission`, `ClientProfile`, `ServicePackage` | `lotExpiration`, `tableNumber`, `repairVin`, `scaleWeight` |
| `hardware` | Necesita unidades variables, medidas, cotizaciones y ventas parciales sin romper Product. | `MeasureUnit`, `CutLengthLine`, `Quote`, `BulkUnitPricing`, `SerialToolRentalFlag` | `appointmentTime`, `kitchenStation`, `prescriptionId`, `colorSizeGrid` |
| `apparel` | Variantes de talla/color y cambios; no meter talla y color como columnas eternas en Product. | `VariantMatrix`, `Size`, `Color`, `ExchangePolicy`, `SeasonTag` | `lotExpiration`, `tableNumber`, `repairOrderId`, `routeStopId` |
| `repair` | Orden de trabajo combina mano de obra, refacciones, diagnostico y entregas; no es ticket instantaneo puro. | `WorkOrder`, `RepairAsset`, `LaborLine`, `PartReservation`, `DiagnosticNote` | `tableNumber`, `prescriptionId`, `appointmentChair`, `scaleWeight` |
| `field_route` | Offline fuerte, preventa, entrega, cliente en ruta y consolidacion posterior. | `Route`, `RouteStop`, `DeliveryAttempt`, `CustomerCredit`, `MobileSettlement` | `tableNumber`, `appointmentChair`, `prescriptionId`, `kitchenStation` |
| `grocery_scale` | Pesaje, precio por unidad variable y tolerancias; el peso es dato de linea, no nuevo producto por cada kilo. | `ScaleReading`, `WeightedSaleLine`, `TarePolicy`, `UnitPriceByWeight`, `ScaleDevice` | `appointmentTime`, `tableNumber`, `prescriptionId`, `repairOrderId` |
| `food_truck` | Punto movil de comida con menu simple, combos, propina opcional y offline tolerante. | `MenuCombo`, `ServiceWindow`, `PrepStatus`, `MobileLocation`, `TipAllocation` | `prescriptionId`, `sizeColorMatrix`, `repairOrderId`, `routeCreditLimit` |

## 9. Reglas por entidad core

### 9.1 Product

`Product` representa articulo fisico base. Debe permanecer pequeño.

Campos permitidos de core:

```text
id, businessId, sku, name, barcode, priceCents, stockOnHand,
lowStockThreshold, isActive, createdAt, updatedAt
```

Campos que NO deben entrar directo a `Product`:

- mesa
- comanda
- receta
- lote avanzado
- talla/color como columnas fijas
- tecnico asignado
- cita
- ruta
- peso capturado
- propina
- orden de reparacion

### 9.2 Sale

`Sale` representa el ticket o venta. No debe convertirse en expediente vertical.

Permitido:

- total
- subtotal
- descuentos
- metodo de pago
- turno
- terminal
- operador
- estado
- timestamps

Especializaciones fuera:

- `DiningSession` para restaurante
- `Appointment` para estetica
- `RouteStop` para campo
- `WorkOrder` para taller
- `PrescriptionReference` para farmacia

### 9.3 SaleLine

`SaleLine` es la unidad cobrada. Debe permitir vender productos, servicios o items verticales mediante referencia normalizada.

Regla:

> Si una linea necesita datos propios del giro, se agrega `verticalLineExtension`, no columnas sueltas.

### 9.4 StockMovement

Solo se genera cuando hay inventario real afectado. Un servicio de corte de cabello no descuenta stock, salvo productos usados si se modelan como consumo interno.

### 9.5 OutboxEvent

Todo modelo vertical que afecte operacion offline debe producir eventos versionados.

Formato recomendado:

```json
{
  "topic": "vertical.restaurant.kitchen_ticket.created",
  "schemaVersion": "0.1.0",
  "businessId": "...",
  "terminalId": "...",
  "actorId": "...",
  "payload": {}
}
```

## 10. Reglas de migracion

1. Ninguna vertical puede requerir migracion destructiva del core.
2. Toda nueva entidad vertical debe tener propietario declarado.
3. Toda entidad vertical debe declarar si vive en Tablet, PC o ambos.
4. Toda relacion hacia core debe ser opcional salvo que el vertical la active.
5. Toda migracion debe tener rollback o estrategia de compatibilidad.
6. Toda extension debe tener fixture minimo.
7. Toda extension debe tener prueba de validacion.

## 11. Compatibilidad con paquetes previos

Este paquete depende conceptualmente de:

- `00A_CORE_CONTRACTS`
- `00B_VERTICAL_REGISTRY`

No requiere modificar runtime de Tablet ni PC. Instala contratos, docs, matrices y validadores. No toca schema Prisma real todavia. Eso es intencional: primero se pone la varilla, luego el concreto.

## 12. Criterio de aceptacion del 00C

- Existen contratos de datos verticales.
- Existen extensiones por los 10 verticales registrados.
- Existe matriz de entidad/propiedad.
- Existe validador local.
- Ningun perfil vertical mete campos especializados al core.
- La verificacion pasa sin depender de servicios externos.
- Los archivos quedan instalados bajo `docs`, `shared` y `tools`.

## Vertical `convenience` - Conveniencia / minisuper

### Principio

Productos rapidos, codigos de barra, stock simple, cortes y ventas de alto ritmo.

### Entidades Tablet

`Product`, `Barcode`, `Sale`, `SaleLine`, `Payment`, `Shift`, `StockMovement`, `LowStockSignal`

### Entidades PC

`Product`, `Barcode`, `StockSnapshot`, `PriceRule`, `SimplePromotion`, `AuditEntry`

### Extensiones declaradas

`ShelfLocation`, `QuickPriceOverride`, `SimplePromotion`, `LowStockSignal`

### Campos prohibidos en core

`tableNumber`, `appointmentTime`, `prescriptionId`, `repairOrderId`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `restaurant` - Restaurante / cafeteria

### Principio

Venta puede ser consumo abierto; mesas, comandas y cocina son extension, no core POS.

### Entidades Tablet

`DiningSession`, `Table`, `Sale`, `SaleLine`, `Payment`, `KitchenTicket`, `TipAllocation`

### Entidades PC

`MenuItem`, `RecipeCost`, `KitchenStation`, `TipPolicy`, `AuditEntry`

### Extensiones declaradas

`Table`, `DiningSession`, `KitchenTicket`, `MenuModifier`, `TipAllocation`

### Campos prohibidos en core

`prescriptionId`, `sizeColorMatrix`, `serialNumber`, `routeStopId`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `pharmacy` - Farmacia

### Principio

Control sensible por lote, caducidad, receta y restriccion; no convertir cada producto en expediente medico.

### Entidades Tablet

`Product`, `Lot`, `Sale`, `SaleLine`, `Payment`, `PrescriptionReference`, `Return`

### Entidades PC

`Lot`, `ExpirationPolicy`, `ControlledProductFlag`, `SupplierBatch`, `AuditEntry`

### Extensiones declaradas

`Lot`, `ExpirationPolicy`, `PrescriptionReference`, `ControlledProductFlag`, `SubstitutionRule`

### Campos prohibidos en core

`tableNumber`, `appointmentTime`, `repairLaborHours`, `colorSizeGrid`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `beauty` - Estetica / barberia / salon

### Principio

Vende servicios, citas y comisiones; inventario de producto existe pero no manda todo el negocio.

### Entidades Tablet

`Service`, `Appointment`, `Sale`, `SaleLine`, `Payment`, `StaffCommission`

### Entidades PC

`ServiceCatalog`, `StaffCommissionPolicy`, `ClientProfile`, `AppointmentBook`, `AuditEntry`

### Extensiones declaradas

`Service`, `Appointment`, `StaffCommission`, `ClientProfile`, `ServicePackage`

### Campos prohibidos en core

`lotExpiration`, `tableNumber`, `repairVin`, `scaleWeight`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `hardware` - Ferreteria

### Principio

Necesita unidades variables, medidas, cotizaciones y ventas parciales sin romper Product.

### Entidades Tablet

`Product`, `MeasureUnit`, `Quote`, `Sale`, `SaleLine`, `Payment`, `StockMovement`

### Entidades PC

`BulkUnitPricing`, `SupplierCatalog`, `MeasurePolicy`, `QuoteApproval`, `AuditEntry`

### Extensiones declaradas

`MeasureUnit`, `CutLengthLine`, `Quote`, `BulkUnitPricing`, `SerialToolRentalFlag`

### Campos prohibidos en core

`appointmentTime`, `kitchenStation`, `prescriptionId`, `colorSizeGrid`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `apparel` - Ropa / boutique

### Principio

Variantes de talla/color y cambios; no meter talla y color como columnas eternas en Product.

### Entidades Tablet

`VariantMatrix`, `Sale`, `SaleLine`, `Payment`, `Return`, `ExchangePolicy`

### Entidades PC

`VariantMatrix`, `SeasonTag`, `InventoryByVariant`, `ExchangePolicy`, `AuditEntry`

### Extensiones declaradas

`VariantMatrix`, `Size`, `Color`, `ExchangePolicy`, `SeasonTag`

### Campos prohibidos en core

`lotExpiration`, `tableNumber`, `repairOrderId`, `routeStopId`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `repair` - Taller / reparaciones

### Principio

Orden de trabajo combina mano de obra, refacciones, diagnostico y entregas; no es ticket instantaneo puro.

### Entidades Tablet

`WorkOrder`, `LaborLine`, `PartReservation`, `Sale`, `Payment`, `DiagnosticNote`

### Entidades PC

`WorkOrder`, `TechnicianQueue`, `PartsInventory`, `WarrantyPolicy`, `AuditEntry`

### Extensiones declaradas

`WorkOrder`, `RepairAsset`, `LaborLine`, `PartReservation`, `DiagnosticNote`

### Campos prohibidos en core

`tableNumber`, `prescriptionId`, `appointmentChair`, `scaleWeight`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `field_route` - Campo / ruta

### Principio

Offline fuerte, preventa, entrega, cliente en ruta y consolidacion posterior.

### Entidades Tablet

`Route`, `RouteStop`, `Sale`, `Payment`, `DeliveryAttempt`, `OutboxEvent`

### Entidades PC

`RoutePlanner`, `CustomerCredit`, `MobileSettlement`, `RouteReconciliation`, `AuditEntry`

### Extensiones declaradas

`Route`, `RouteStop`, `DeliveryAttempt`, `CustomerCredit`, `MobileSettlement`

### Campos prohibidos en core

`tableNumber`, `appointmentChair`, `prescriptionId`, `kitchenStation`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `grocery_scale` - Abarrotes con bascula

### Principio

Pesaje, precio por unidad variable y tolerancias; el peso es dato de linea, no nuevo producto por cada kilo.

### Entidades Tablet

`ScaleReading`, `WeightedSaleLine`, `Sale`, `Payment`, `Product`

### Entidades PC

`ScaleDevice`, `TarePolicy`, `UnitPriceByWeight`, `AuditEntry`

### Extensiones declaradas

`ScaleReading`, `WeightedSaleLine`, `TarePolicy`, `UnitPriceByWeight`, `ScaleDevice`

### Campos prohibidos en core

`appointmentTime`, `tableNumber`, `prescriptionId`, `repairOrderId`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## Vertical `food_truck` - Food truck / comida movil

### Principio

Punto movil de comida con menu simple, combos, propina opcional y offline tolerante.

### Entidades Tablet

`MenuCombo`, `Sale`, `SaleLine`, `Payment`, `PrepStatus`, `MobileLocation`

### Entidades PC

`MenuCatalog`, `MobileLocation`, `SalesByStop`, `PrepPolicy`, `AuditEntry`

### Extensiones declaradas

`MenuCombo`, `ServiceWindow`, `PrepStatus`, `MobileLocation`, `TipAllocation`

### Campos prohibidos en core

`prescriptionId`, `sizeColorMatrix`, `repairOrderId`, `routeCreditLimit`

### Regla practica

Si este giro requiere un dato que no existe en conveniencia, probablemente no pertenece al core. Debe declararse como extension versionada, con propietario y prueba de compatibilidad. Si el cajero lo necesita para cobrar, Tablet puede tener una version local minima. Si solo sirve para administracion profunda, PC lo gobierna.

## 13. Checklist extendido por extension

Este checklist debe aplicarse a toda extension futura. No es relleno documental: es la cerca electrificada para que el modelo no se vuelva rancho sin escrituras.

- `convenience.ShelfLocation` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `convenience.QuickPriceOverride` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `convenience.SimplePromotion` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `convenience.LowStockSignal` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `restaurant.Table` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `restaurant.DiningSession` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `restaurant.KitchenTicket` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `restaurant.MenuModifier` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `restaurant.TipAllocation` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `pharmacy.Lot` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `pharmacy.ExpirationPolicy` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `pharmacy.PrescriptionReference` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `pharmacy.ControlledProductFlag` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `pharmacy.SubstitutionRule` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `beauty.Service` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `beauty.Appointment` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `beauty.StaffCommission` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `beauty.ClientProfile` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `beauty.ServicePackage` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `hardware.MeasureUnit` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `hardware.CutLengthLine` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `hardware.Quote` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `hardware.BulkUnitPricing` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `hardware.SerialToolRentalFlag` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `apparel.VariantMatrix` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `apparel.Size` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `apparel.Color` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `apparel.ExchangePolicy` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `apparel.SeasonTag` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `repair.WorkOrder` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `repair.RepairAsset` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `repair.LaborLine` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `repair.PartReservation` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `repair.DiagnosticNote` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `field_route.Route` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `field_route.RouteStop` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `field_route.DeliveryAttempt` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `field_route.CustomerCredit` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `field_route.MobileSettlement` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `grocery_scale.ScaleReading` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `grocery_scale.WeightedSaleLine` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `grocery_scale.TarePolicy` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `grocery_scale.UnitPriceByWeight` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `grocery_scale.ScaleDevice` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `food_truck.MenuCombo` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `food_truck.ServiceWindow` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `food_truck.PrepStatus` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `food_truck.MobileLocation` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.
- `food_truck.TipAllocation` debe declarar owner, storage, syncPolicy, tabletAccess, pcAuthority, auditImpact, offlineImpact y rollbackStrategy.

## 14. Reglas de gobierno detalladas

1. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
2. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
3. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
4. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
5. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
6. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
7. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
8. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
9. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
10. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
11. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
12. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
13. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
14. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
15. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
16. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
17. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
18. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
19. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
20. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
21. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
22. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
23. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
24. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
25. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
26. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
27. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
28. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
29. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
30. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
31. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
32. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
33. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
34. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
35. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
36. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
37. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
38. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
39. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
40. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
41. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
42. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
43. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
44. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
45. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
46. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
47. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
48. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
49. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
50. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
51. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
52. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
53. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
54. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
55. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
56. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
57. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
58. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
59. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
60. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
61. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
62. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
63. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
64. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
65. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
66. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
67. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
68. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
69. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
70. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
71. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
72. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
73. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
74. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
75. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
76. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
77. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
78. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
79. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
80. Una extension vertical nueva debe demostrar por que no cabe en core sin contaminar otros giros; si la respuesta es 'por si acaso', se rechaza. Debe incluir fixture, evento si afecta operacion, owner y criterio de rollback.
