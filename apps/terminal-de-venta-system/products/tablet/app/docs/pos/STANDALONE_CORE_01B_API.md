# PRISMA Tablet Standalone Core 01B - API

## Version

`PRISMA_TABLET_POS_STANDALONE_CORE_01B_API`

## Decision

Despues de `01A_ENGINE`, Tablet ya tiene motor POS local. Este paquete agrega las rutas internas para que la aplicacion pueda operar ventas, busqueda de catalogo y resumen del dia sin depender de PC.

## Scope

Incluye:

- busqueda de productos activos
- resolucion rapida por SKU, barcode o id
- cierre de venta local mediante `posEngineRepository.completeLocalSale`
- resumen de ventas del dia
- manejo consistente de respuestas `{ ok: true }` / `{ ok: false }`
- traduccion de errores del motor a errores HTTP utiles

No incluye:

- UI de checkout
- scanner visual
- devoluciones
- cancelacion avanzada
- sync con PC

## Endpoints

### GET `/api/pos/products/search?q=coca`

Busca productos por nombre, SKU, categoria o barcode parcial.

### GET `/api/pos/products/resolve?code=750000000001`

Resuelve un producto exacto para flujo de scanner o busqueda rapida.

### POST `/api/pos/sales/complete`

Cierra una venta local.

Ejemplo minimo:

```json
{
  "items": [
    { "sku": "COCA-600", "quantity": 2 }
  ],
  "cashier": "tablet-cashier"
}
```

### GET `/api/pos/sales/today`

Devuelve ventas cerradas, total vendido, ticket promedio, unidades vendidas y top productos del dia.

## Acceptance criteria

- La API compila con TypeScript.
- `verify_pos_api_01b.mjs` pasa.
- La ruta de venta llama a `posEngineRepository.completeLocalSale`.
- Las busquedas leen desde la DB local de Tablet.
- Los errores del motor no exponen stacktrace.
- La UI futura puede usar estos endpoints sin importar codigo de Prisma directamente.

## Runtime contract

Todos los endpoints son `runtime = "nodejs"` porque Prisma no debe intentar correr en Edge. Edge esta muy bonito para demos; para SQLite local es como querer freir carnitas en sartencito de juguete.
