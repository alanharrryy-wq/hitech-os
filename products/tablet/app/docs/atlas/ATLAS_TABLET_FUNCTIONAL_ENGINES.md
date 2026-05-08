# ATLAS TABLET FUNCTIONAL ENGINES - Ronda 2

## Alcance

Este documento mapea motores funcionales confirmados dentro de `products/tablet/app` según el ZIP. No documenta Shared Core como si perteneciera a Tablet; cuando hay imports compartidos se marcan como dependencia externa.

## Motores confirmados

| Motor | Ubicación | Responsabilidad Tablet confirmada |
| --- | --- | --- |
| Catálogo local | `src/server/local-catalog` | Listar, resolver e importar catálogo local operativo |
| Productos POS | `src/server/pos-api/product-mutations.prisma` y APIs `products/*` | Crear/actualizar/buscar/resolver productos y validar barcodes |
| Venta durable | `src/server/pos-engine` | Persistir venta, líneas, movimiento de stock y outbox |
| Ventas API | `app/api/pos/sales/*` | Completar venta, listar ventas del día y consultar detalle |
| Devoluciones | `app/api/pos/returns/create` + capa server POS | Crear devolución asociada a operación POS |
| Turnos | `app/api/pos/shift/*` | Consultar/abrir/cerrar turno local de Tablet |
| Reportes POS | `src/server/pos-reports` | Reporte operacional, pending outbox, low stock y movimientos recientes |
| Exportación | `src/server/pos-export` | CSV de ventas, eventos y movimientos de inventario |
| Outbox | `src/server/pos-outbox` | Exponer eventos pendientes/recientes de sincronización |
| Sync | `src/server/sync` | Panel y retry de eventos; contratos externos de Shared Kernel |
| Licensing adapter | `src/server/licensing` | Adaptador Tablet hacia `shared/licensing` externo |
| Runtime snapshot | `src/server/tablet-runtime-snapshot` | Snapshot de runtime para diagnóstico/preview |
| Release gate | `src/server/operable-release-gate` | Estado/veredicto operativo de release en Tablet |

## Catálogo local

Endpoints confirmados:

- `/api/pos/catalog/products`
- `/api/pos/catalog/resolve`
- `/api/pos/catalog/import`

Verificador `verify:i02-catalogo` pasa. Confirma archivo local, módulo server, rutas y fixtures con productos activos/inactivos, SKU, barcode, precio y stock.

## Motor POS durable

El verificador T04 confirma marcadores de persistencia en `src/server/pos-engine/repository.prisma.ts`:

- creación de `Sale`
- creación de `SaleLine`
- creación de `StockMovement`
- creación de `OutboxEvent`

Esto permite documentar que el flujo POS no es sólo maqueta visual; hay persistencia durable local. No se asume sincronización PC completa porque eso no se confirma sólo con el ZIP.

## Ventas y ticket detail

Endpoints confirmados:

- `/api/pos/sales/complete`
- `/api/pos/sales/today`
- `/api/pos/sales/detail`

Estado de QA:

- La ruta de detalle existe.
- Usa `getSaleDetail`.
- Soporta `saleId`/`folio`.
- Devuelve `SALE_NOT_FOUND`.
- La pantalla maneja not_found, error, loading y líneas.

Bloqueos vigentes:

- `I03A-010 screen calls direct detail endpoint` falla.
- `I03A-016 list links to encoded saleId` falla.

## Offline, outbox y export

Endpoints confirmados:

- `/api/pos/offline/audit`
- `/api/pos/events/outbox`
- `/api/pos/events/recent`
- `/api/pos/export/contextual`
- `/api/pos/export/sales-today`
- `/api/pos/export/events`
- `/api/pos/export/inventory-movements`

T04 confirma:

- auditoría usa reporte operacional, outbox y movimientos
- auditoría expone CSV exports
- auditoría declara no depender de PC
- pantalla llama endpoint offline audit
- pantalla renderiza exports y movimientos
- exportador construye ventas del día, eventos y movimientos
- `csvResponse` existe
- reporte incluye pending outbox, low stock y recent movements

Bloqueo vigente:

- `T04-008 screen renders outbox` falla.

## Turnos

Endpoints confirmados:

- `/api/pos/shift/current`
- `/api/pos/shift/open`
- `/api/pos/shift/close`

Responsabilidad: operación local de turno en Tablet. Reglas globales de negocio quedan pendientes si dependen de componentes no incluidos.

## Licensing

`src/server/licensing/**` y `components/license/**` importan `shared/licensing`. Tablet sólo consume/adapta. No se declara ownership sobre el motor de licencia.

## Shared Kernel y composición

`src/composition/**`, `src/modules/**` y `src/server/sync/events.ts` importan tipos/registries de `@shared-kernel/*`. En este atlas se registran como dependencia externa. La validación de paquete falla precisamente porque esos archivos no están dentro del ZIP.

## Base de datos local

El ZIP incluye dos SQLite:

- `data/tablet-pos.db`: base con datos demo/operativos.
- `prisma/data/tablet-pos.db`: base estructural vacía.

El atlas no cambia ni migra ninguna DB. Sólo documenta su existencia y rol.

## Release functional readiness

Estado honesto: **BLOCKED**. El motor POS tiene piezas reales, pero no debe promoverse a release final mientras I03A y T04 fallen. La cosa está como taquería con trompo prendido pero sin salsa verde: vende, sí, pero falta lo que el cadenero de QA exige.