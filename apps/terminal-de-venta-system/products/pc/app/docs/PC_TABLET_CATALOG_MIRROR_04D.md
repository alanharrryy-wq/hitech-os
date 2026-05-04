# PC Tablet Catalog Mirror 04D

## Objetivo

Hacer visible en PC el catálogo masivo agregado a Tablet en `PRISMA_TABLET_MASS_CATALOG_04B`.

## Decisión

Tablet y PC no comparten base local directa:

- Tablet opera `products/tablet/app/data/tablet-pos.db`.
- PC lee la base canónica `tools/_local/data/terminal-de-venta-system/canonical.db`.

Por eso cargar Tablet no actualiza PC automáticamente. Este paquete agrega un seed PC explícito e idempotente.

## Datos

- Productos espejo: 142.
- Barcodes públicos referenciados: 14.
- Códigos internos operativos: 128.
- Business PC: `biz_hitech_default`.
- Ubicación stock PC: `SUCURSAL_CENTRO`.

## Validación

```powershell
cd F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app
pnpm run db:pc:mass-catalog
pnpm run verify:pc:mass-catalog
pnpm run typecheck
```

## Nota de arquitectura

Esto no convierte a PC en requisito de venta. Tablet sigue vendiendo standalone. PC queda como backoffice con copia consolidada para catálogo, stock, barcodes y gobierno.
