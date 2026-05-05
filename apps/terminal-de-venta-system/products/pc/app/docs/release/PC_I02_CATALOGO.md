# Release note - PC I02 Catálogo

## Entrega

`install_pc_i02_catalogo.py` genera localmente `pc_i02_catalogo.zip` e instala los archivos de catálogo avanzado dentro de `products/pc/app/**`.

## Cambio funcional

La ruta `/catalog` deja de ser un overview genérico y pasa a usar una capa real de repositorio/servicio/validador:

```text
/catalog
  -> CatalogDashboard
  -> getCatalogWorkspace
  -> CatalogRepository
  -> Prisma Product + Barcode[] + StockSnapshot
  -> catalog-quality validator
```

## Pruebas mínimas

- Validación de carril PC.
- Manifest y checksums.
- Backup antes de sobrescribir.
- Verify de archivos instalados.
- `node tools/verify_pc_catalog_02.mjs --root products/pc/app` cuando Node está disponible.
- DB smoke con SQLite si existe canonical.db.
- HTTP smoke opcional si PC está levantada en puerto 3130.

## Resultado esperado

`READY` si todo instala, verifica y pasa pruebas funcionales disponibles.

`READY_WITH_CAVEATS` si el código queda instalado/verificado, pero DB o servidor local no están disponibles para smoke completo.

`BLOCKED` si falla carril, manifest, checksums, apply, verify o un test crítico ejecutable.
