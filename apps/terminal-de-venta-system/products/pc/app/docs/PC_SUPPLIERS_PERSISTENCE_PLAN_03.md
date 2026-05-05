# PRISMA PC - Plan Persistencia Proveedores Lifecycle 03

## Por que no meter persistencia en este ZIP

Porque mezclar UI, motor, endpoints, schema, migraciones y repositorios reales en una sola entrega es como querer remodelar cocina, baño y drenaje el mismo domingo. Puede salir, pero luego nadie sabe cual fuga mojo la sala.

Este ZIP v02 deja contrato operativo. El siguiente debe conectar persistencia con cambios controlados.

## Entidades a crear o mapear

### Supplier

Campos minimos:

- id
- businessId
- tradeName
- legalName
- category
- status
- notes
- createdAt
- updatedAt

### SupplierContact

- id
- supplierId
- name
- role
- phone
- whatsapp
- email
- isPrimary

### SupplierSchedule

- id
- supplierId
- cadence
- weekdaysJson
- approximateTime
- orderCutoffWeekday
- orderCutoffTime
- leadTimeDays
- nextVisitDate
- nextOrderCutoff

### SupplierTerms

- id
- supplierId
- paymentCondition
- creditDays
- minimumOrderCents
- creditLimitCents
- usualDiscountBps
- shippingCostCents
- returnPolicy

### SupplierProduct

- id
- supplierId
- productId
- isPrimary
- packageSize
- minPurchaseUnits
- recentCostCents
- lastCostUpdateAt

### PurchaseOrder

- id
- businessId
- supplierId
- folio
- source
- status
- createdAt
- expectedReceptionDate
- expectedPaymentDate
- totalCents
- recommendationId nullable

### PurchaseOrderLine

- id
- orderId
- productId
- skuSnapshot
- nameSnapshot
- orderedUnits
- receivedUnits
- unitCostCents
- expectedTotalCents

### ReceivingReceipt

- id
- orderId nullable
- supplierId
- status
- expectedAt
- receivedAt
- createdBy
- reason

### ReceivingDifference

- id
- receiptId
- productId
- expectedUnits
- receivedUnits
- reason
- note

### SupplierPayable

- id
- supplierId
- orderId nullable
- receiptId nullable
- dueDate
- amountCents
- status
- notes

### SupplierAuditEvent

- id
- topic
- actorId
- actorRole
- entityType
- entityId
- beforeJson
- afterJson
- reason
- createdAt
- source
- visibleSummary

## Transacciones necesarias

### Convertir recomendacion a pedido

1. Leer recomendacion vigente.
2. Validar proveedor activo.
3. Validar lineas y caja.
4. Crear PurchaseOrder.
5. Crear PurchaseOrderLine.
6. Crear AuditEvent.
7. Marcar recomendacion como converted_to_order si existe tabla de runs.

Rollback: toda la transaccion revierte pedido, lineas y auditoria.

### Confirmar recepcion

1. Leer pedido.
2. Validar estado.
3. Crear ReceivingReceipt.
4. Crear ReceivingDifference si aplica.
5. Crear StockMovement por linea recibida.
6. Actualizar PurchaseOrderLine.receivedUnits.
7. Cambiar estado de pedido.
8. Crear SupplierPayable si hay credito o saldo.
9. Crear AuditEvent.

Rollback: revierte receipt, differences, stock movements, payable y estado de pedido.

### Registrar pago

1. Leer SupplierPayable.
2. Validar rol.
3. Aplicar pago parcial o completo.
4. Crear AuditEvent.
5. Recalcular presupuesto seguro de Compra Inteligente en siguiente corrida.

## Indices recomendados

- Supplier.businessId + status
- SupplierSchedule.supplierId + nextVisitDate
- SupplierProduct.productId + isPrimary
- PurchaseOrder.businessId + supplierId + status
- PurchaseOrder.source + createdAt
- ReceivingReceipt.orderId + status
- SupplierPayable.supplierId + dueDate + status
- SupplierAuditEvent.entityType + entityId
- SupplierAuditEvent.topic + createdAt

## Gates antes de schema real

- No romper `products/pc/app/src/lib/suppliers/types.ts`.
- Mantener endpoints v02.
- Mantener mensajes es-MX.
- No exponer jerga tecnica en UI.
- No tocar Tablet salvo contrato de señales.
- Instalador debe poder revertir migracion si falla validacion.

## Entrega siguiente sugerida

`PRISMA_PC_PROVEEDORES_PERSISTENCIA_PRISMA_20260503_v03.zip`

Contenido:

- schema patch controlado;
- repositorio Prisma;
- seed minimo;
- API conectada a DB;
- smoke script con lectura/escritura real;
- rollback de schema si aplica o migracion reversible documentada.
