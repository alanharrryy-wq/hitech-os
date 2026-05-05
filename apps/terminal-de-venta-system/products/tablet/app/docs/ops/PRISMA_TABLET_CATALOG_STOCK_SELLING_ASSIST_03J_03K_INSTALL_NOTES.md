# Install Notes - PRISMA Tablet Catalog Stock Selling Assist 03J 03K

## Precondiciones

- Repo en `F:\repos\hitech-os\apps\terminal-de-venta-system`.
- ZIP e instalador en `F:\descargasf`.
- Python disponible.
- Node recomendado para verificadores `.mjs`.

## Orden recomendado

1. Ejecutar `--dry-run`.
2. Revisar targets.
3. Ejecutar `--apply`.
4. Ejecutar `--verify`.
5. Levantar Tablet en puerto 3120.
6. Probar `/catalog`, `/stock`, `/existencias` y `/pos`.

## Comando apply

```powershell
python F:\descargasf\install_prisma_tablet_catalog_stock_selling_assist_03j_03k.py --zip-path F:\descargasf\PRISMA_TABLET_CATALOG_STOCK_SELLING_ASSIST_03J_03K.zip --target-root F:\repos\hitech-os\apps\terminal-de-venta-system --apply
```

## Rollback

```powershell
python F:\descargasf\install_prisma_tablet_catalog_stock_selling_assist_03j_03k.py --target-root F:\repos\hitech-os\apps\terminal-de-venta-system --rollback
```

## Archivos con riesgo de reemplazo

- `app/catalog/page.tsx`
- `app/stock/page.tsx`
- `app/existencias/page.tsx`

El resto son archivos nuevos del bloque. El instalador hace backup antes de tocar esos tres archivos, porque hasta los robots saben que sobrescribir sin backup es de villano barato.
