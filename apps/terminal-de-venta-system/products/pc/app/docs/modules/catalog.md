# PC I02 - Catálogo avanzado, SKUs y barcodes

## Objetivo

Convertir `/catalog` de una vista tipo overview a una pantalla operativa de backoffice para gobernar productos, SKUs, Barcode[], precios, estados y excepciones.

## Alcance instalado

- Ruta `/catalog` conectada a `getCatalogWorkspace`.
- Repositorio `CatalogRepository` con lectura de `Product`, `Barcode[]` y `StockSnapshot` desde Prisma canónico.
- Servicio `catalog.service.ts` que normaliza filtros, calcula resumen y clasifica excepciones.
- Validador `catalog-quality.ts` para:
  - productos activos sin barcode;
  - barcodes duplicados en la muestra;
  - producto inactivo;
  - precio viejo por política de 45 días.
- UI con:
  - cards de resumen;
  - filtros por búsqueda, estado, categoría e incidencia;
  - tabla de SKUs;
  - ficha de producto;
  - panel de incidencias.

## Límites explícitos

- No modifica Tablet.
- No toca `packages/shared-kernel/**` ni `shared/contracts/**`.
- No hace migración de base de datos.
- No crea edición masiva ni escritura de productos; eso requiere auditoría y permisos posteriores.

## Evidencia esperada

- `tools/verify_pc_catalog_02.mjs` debe pasar.
- El instalador debe generar `evidence/db-smoke/catalog-summary.json` cuando exista `canonical.db`.
- El instalador debe intentar smoke HTTP de `/catalog` si PC ya está levantada en `http://127.0.0.1:3130`.

## Estado honesto

Si Prisma/canonical.db no existe en la máquina local, la pantalla no inventa datos: queda en estado vacío con warning visible. Eso es preferible a vender humo con números bonitos, que para eso ya existe la política.
