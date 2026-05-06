# PRISMA_TABLET_STOCK_SCREEN_01A_REAL_VIEW

## Propósito

Convertir `/stock` en una pantalla operativa real de Tablet, conectada al servicio local `getStockConsole()` y renderizada con `PrismaOperationalScreen`.

## Alcance

- Reemplaza la ruta `products/tablet/app/app/stock/page.tsx`.
- Usa el estándar `PRISMA_TABLET_SCREEN_STANDARD_01A`.
- Lee datos desde `src/lib/services/stock.ts`.
- Presenta KPIs, vigilancia de existencias, reabasto sugerido, pulso por categoría y alertas de barcode.
- Incluye estado de error elegante si el servicio local no responde.

## Fuera de alcance

- No crea bases de datos nuevas.
- No modifica `schema.prisma`.
- No toca `shared-kernel`.
- No convierte Tablet en backoffice pesado.
- No introduce acciones destructivas de inventario.

## Contrato visual

La pantalla debe seguir este orden:

1. Shell unificado de Tablet.
2. Masthead con señal operativa.
3. KPIs principales.
4. Tabla primaria de existencias.
5. Secciones secundarias de reabasto, categorías y barcode.
6. Estados vacíos o de error sin copy de maqueta.

## Fuente de datos

`getStockConsole()` usa `ProductRepositoryPrisma`, que lee productos activos con `barcodes` y `stockSnapshots` desde Prisma Client.

## Decisión de arquitectura

Esta inyección conecta pantalla y servicio existente. La evolución de inventario profundo, ajustes masivos, compras o auditoría queda para PC Backoffice o futuras pantallas gobernadas.
