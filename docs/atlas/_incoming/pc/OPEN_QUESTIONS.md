# OPEN QUESTIONS - PC Atlas Ronda 2

Destino único: `docs/atlas/_incoming/pc/`  
Fuente única: `ATLAS_CHAT_PC.zip`

Estas preguntas quedan abiertas porque no se pueden confirmar únicamente desde el ZIP. No deben resolverse inventando archivos, rutas ni ownership.

## Prisma y base de datos

1. ¿Dónde vive exactamente el schema Prisma canónico del monorepo?
2. ¿Cuál es el flujo oficial para `db:canonical:generate` y `db:canonical:migrate` en PC?
3. ¿El `products/pc/app/prisma/schema.prisma` transicional debe mantenerse, eliminarse o solo usarse como stub local?
4. ¿El fallback DB local detectado en runtime es aceptado para desarrollo, CI o solo compatibilidad temporal?
5. ¿Qué modelos Prisma son fuente de verdad para catálogo, inventario, compras, sync, suppliers y settings?

## Dependencias compartidas

1. Confirmar ubicación y versión efectiva de `shared/twin-kernel`.
2. Confirmar contrato real de `TwinModuleManifest` usado por PC.
3. Confirmar ubicación y ownership de `shared/licensing`.
4. Confirmar ubicación y rol de `shared/tri-db`.
5. Confirmar si `shared/contracts` o contratos de `global_context/docs/contracts/**` tienen artefactos runtime equivalentes.

## Visual OS y assets

1. Confirmar ownership de `shared-ui/prisma` y `styles/prisma-visual-os`.
2. Confirmar si PC debe versionar su binding `data-prisma-vos-binding="00J"` o si ese versionado depende de governance visual global.
3. Resolver assets listados en `analysis/pc_public_asset_manifest.json` pero ausentes del snapshot:
   - `public/brand/prisma-logo-official.png`
   - `public/landing/prisma-multisucursal-control-total.png`
   - `public/landing/prisma-pc-controla-operacion.png`
   - `public/landing/prisma-pos-vende-con-orden.png`
4. Confirmar si landing debe usar solo SVG presentes o también los PNG faltantes.

## Runtime y CI

1. Ejecutar `npm run check:package` en repo completo.
2. Ejecutar `npm run typecheck` en repo completo.
3. Ejecutar `npm run build` en repo completo.
4. Ejecutar verificadores `tools/verify*.mjs` relevantes en entorno con dependencias externas.
5. Confirmar si CI de `atlas-coordinator` espera solo docs staging o también validación de JSON/schema.

## Backoffice funcional

1. Confirmar si todas las 47 rutas visibles son rutas finales activas o si algunas son pantallas experimentales/iteraciones.
2. Confirmar estado de APIs `POST` y mutaciones reales para sync, suppliers, purchases y inventory.
3. Confirmar permisos/roles efectivos para pantallas administrativas.
4. Confirmar si `/dashboard` y `/` deben aparecer como módulos en registry o si son navegación shell especial.
5. Confirmar si `proveedores-*` está estabilizado como bloque funcional completo o sigue en evolución.

## Sync y eventos

1. Confirmar contrato runtime de eventos entre Tablet y PC.
2. Confirmar reglas finales para duplicates, conflicts y rejected.
3. Confirmar si PC solo observa/ingiere o también reconcilia automáticamente ciertos eventos.
4. Confirmar retención/limpieza de queue sync.

## Licenciamiento

1. Confirmar contrato final de feature gates PC.
2. Confirmar si las licencias dependen de sesión/tenant/local store o servicio externo.
3. Confirmar comportamiento esperado cuando `shared/licensing` no está disponible.

## Criterio para mover fuera de staging

Antes de mover estos archivos a una ruta final, confirmar:

- Ruta final aprobada por coordinador de atlas.
- Schema canónico aprobado.
- Dependencias externas presentes en repo completo.
- Hallazgos de assets resueltos o aceptados.
- CI/document checks pasando.
