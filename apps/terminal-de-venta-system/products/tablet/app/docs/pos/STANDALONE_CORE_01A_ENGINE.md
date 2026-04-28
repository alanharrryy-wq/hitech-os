# PRISMA Tablet POS Standalone Core 01A - Engine

**Paquete:** `PRISMA_TABLET_POS_STANDALONE_CORE_01A_ENGINE`
**Capa:** Motor de venta local
**Producto:** Tablet POS Standalone
**Estado:** Base instalable para construir código
**Regla madre:** Tablet puede vender sin PC; PC gobierna cuando exista, pero no desbloquea la venta.

## 1. Decisión

Este paquete instala el primer motor real de venta local para Tablet. La Tablet ya tiene base SQLite propia (`data/tablet-pos.db`), schema Prisma local y arranque independiente. Esta inyección agrega la lógica que cierra una venta de forma transaccional.

La decisión es deliberada: **01A no toca UI ni API**. Primero se crea un núcleo confiable, luego una superficie de operación. Hacer pantalla antes del motor es como poner mostrador de mármol en una tienda sin caja: se ve fino, pero el dinero se va por la puerta.

## 2. Alcance

Incluye:

- contrato de entrada para completar venta local
- normalización de líneas de carrito
- resolución de producto por `productId`, `sku` o `barcode`
- validación de cantidad
- validación de producto activo
- validación de stock disponible
- creación de `Sale`
- creación de `SaleLine`
- decremento de `Product.stockOnHand`
- creación de `StockMovement`
- creación de `OutboxEvent`
- eventos locales mínimos
- verificador estático `tools/verify_pos_engine_01a.mjs`
- documentación QA y fixture de catálogo para pruebas posteriores

No incluye:

- pantalla de checkout
- rutas API o server actions
- impresión de tickets
- métodos de pago avanzados
- devoluciones
- corte de caja robusto
- sync remoto con PC
- facturación

## 3. Entrada pública

```ts
posEngineRepository.completeLocalSale(input)
```

### Entrada mínima

```ts
{
  lines: [
    { sku: "COCA-600", qty: 2 }
  ]
}
```

### Entrada completa

```ts
{
  businessId: "biz_tablet_standalone",
  terminalId: "terminal_tablet_001",
  cashSessionId: null,
  cashier: "caja-1",
  location: "tablet-floor",
  allowNegativeStock: false,
  lowStockThreshold: 5,
  lines: [
    { productId: "prod_001", qty: 2 },
    { sku: "SABRITAS-45", qty: 1 },
    { barcode: "750000000001", qty: 1 }
  ]
}
```

## 4. Salida esperada

```ts
{
  saleId: "sale_...",
  folio: "T-20260426-082000-ABC12345",
  businessId: "biz_tablet_standalone",
  terminalId: "terminal_tablet_001",
  cashSessionId: null,
  cashier: "caja-1",
  totalCents: 6900,
  status: "COMPLETED",
  createdAt: Date,
  lines: [...],
  events: [...]
}
```

## 5. Invariantes

1. No se cierra venta vacía.
2. No se acepta cantidad menor o igual a cero.
3. No se vende producto inexistente.
4. No se vende producto inactivo.
5. No se descuenta stock si `allowNegativeStock` es `false` y no alcanza.
6. La venta, líneas, movimientos y outbox deben persistirse dentro de una transacción.
7. Cada cierre genera al menos `sale.created`, `sale.completed` y `ticket.closed`.
8. Cada producto vendido genera `stock.decremented`.
9. Si el stock final queda por debajo del umbral, se genera `inventory.low_stock_detected`.
10. El motor no depende de PC ni de base canónica externa.

## 6. Eventos

### `sale.created`

Marca que se abrió el registro de venta local.

### `sale.completed`

Marca cierre transaccional exitoso.

### `ticket.closed`

Permite a UI, impresión o reporte consumir el resumen del ticket.

### `stock.decremented`

Permite a inventario y sync saber qué producto bajó.

### `inventory.low_stock_detected`

Permite a reportes o alertas mostrar que el producto ya quedó corto.

## 7. Modelo de error

Los errores se encapsulan en `PosEngineError` con `code` y `details`.

Códigos iniciales:

- `EMPTY_CART`
- `INVALID_QUANTITY`
- `PRODUCT_NOT_FOUND`
- `PRODUCT_INACTIVE`
- `INSUFFICIENT_STOCK`
- `TERMINAL_NOT_FOUND`
- `BUSINESS_NOT_FOUND`
- `ENGINE_INVARIANT_FAILED`

## 8. Acceptance criteria

### POS-01A-AC-001

Dado un catálogo local con producto activo y stock suficiente, cuando se llama `completeLocalSale`, entonces se crea una venta con folio local.

### POS-01A-AC-002

Dado un carrito con múltiples líneas, cuando se cierra la venta, entonces se crean líneas de venta con totales por línea correctos.

### POS-01A-AC-003

Dado un producto vendido, cuando se cierra la venta, entonces `Product.stockOnHand` baja por la cantidad vendida.

### POS-01A-AC-004

Dado un producto vendido, cuando se cierra la venta, entonces se crea `StockMovement` con `movement = SALE`, cantidad negativa y razón `sale.completed`.

### POS-01A-AC-005

Dado un cierre exitoso, cuando termina la transacción, entonces se crean outbox events pendientes.

### POS-01A-AC-006

Dado un stock insuficiente y `allowNegativeStock = false`, cuando se intenta cerrar la venta, entonces se rechaza con `INSUFFICIENT_STOCK` y no debe quedar venta parcial.

### POS-01A-AC-007

Dado un producto inactivo, cuando se intenta vender, entonces se rechaza con `PRODUCT_INACTIVE`.

### POS-01A-AC-008

Dado un carrito vacío, cuando se intenta cerrar, entonces se rechaza con `EMPTY_CART`.

### POS-01A-AC-009

Dado un producto que queda bajo el umbral, cuando se cierra la venta, entonces se genera evento `inventory.low_stock_detected`.

### POS-01A-AC-010

Dado que PC no existe, cuando corre el motor contra la DB local de Tablet, entonces no debe requerir rutas de PC ni DB canónica externa.

## 9. Validación instalada

El paquete instala:

```text
products/tablet/app/tools/verify_pos_engine_01a.mjs
```

Uso desde la app Tablet:

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app
node tools/verify_pos_engine_01a.mjs
```

## 10. Próxima inyección

La siguiente pieza debe ser `01B_API`: rutas API o server actions para exponer este motor a la UI.
