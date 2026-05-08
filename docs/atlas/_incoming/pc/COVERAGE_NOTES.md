# COVERAGE NOTES - PC Atlas Ronda 2

Destino único: `docs/atlas/_incoming/pc/`  
Fuente única: `ATLAS_CHAT_PC.zip`

## Cobertura confirmada

El atlas cubre solamente evidencia presente en el ZIP:

- `analysis/routes_and_apis.json`
- `analysis/pc_full_file_inventory.csv`
- `analysis/shared_dependency_hits.json`
- `analysis/pc_public_asset_manifest.json`
- `analysis/package_scripts.json`
- `templates/prisma-atlas.schema.json`
- `source_snapshot/products/pc/app/**`
- `global_context/docs/**` como contexto de contratos/arquitectura global, no como ownership PC

## Conteos confirmados desde el ZIP

| Elemento | Conteo |
|---|---:|
| Rutas visibles | 47 |
| Rutas API | 36 |
| Archivos inventariados de PC | 400 |
| Componentes TSX | 39 |
| Repositorios server | 9 |
| Servicios/motores detectados | 44 |
| Validadores server | 4 |
| Herramientas/verificadores | 34 |
| Markdown docs PC | 78 |
| Assets públicos presentes | 6 |
| Assets listados en manifest | 10 |

## Fronteras de propiedad

PC sí se documenta como propietario funcional de:

- Backoffice PC.
- Páginas y API routes bajo `products/pc/app/app/**`.
- Componentes bajo `products/pc/app/components/**`.
- Servicios, repositorios, validadores y motores bajo `products/pc/app/src/**`.
- Verificadores y fixtures bajo `products/pc/app/tools/**` y `products/pc/app/fixtures/**`.

PC no se documenta como propietario de:

- Prisma canónico.
- Shared Core.
- `shared/twin-kernel`.
- `shared/licensing`.
- `shared/tri-db`.
- `shared-ui/prisma`.
- `styles/prisma-visual-os`.
- Contratos globales en `global_context/docs/contracts/**`.

## Hallazgo de assets

`analysis/pc_public_asset_manifest.json` lista 10 assets, pero el snapshot contiene 6. Los cuatro faltantes quedan pendientes y no fueron creados ni inventados.

## Validación JSON

`atlas.pc.json` se emitió con los campos canónicos requeridos por `templates/prisma-atlas.schema.json`:

- `atlasId`
- `app`
- `root`
- `version`
- `changeIntents`
- `verification`

## Limitaciones

No se confirma desde el ZIP:

- Compilación completa.
- Build Next completo.
- Migraciones Prisma reales.
- Disponibilidad de dependencias compartidas.
- CI de GitHub.
- Estado final de permisos/auth.
- Runtime real con DB.

## Recomendación antes de promover a ruta final

Mantener esta entrega en staging hasta validar en repo completo:

```bash
cd products/pc/app
npm run check:package
npm run typecheck
npm run build
```

Y confirmar dependencias externas antes de mover cualquier contenido a rutas finales.