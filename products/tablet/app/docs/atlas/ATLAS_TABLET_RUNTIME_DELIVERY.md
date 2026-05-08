# ATLAS TABLET RUNTIME DELIVERY - Ronda 2

## Alcance

Este documento cubre runtime, scripts, verificación y entrega del paquete Tablet/POS observado en el ZIP. No mueve archivos a rutas finales y no modifica código funcional.

## Runtime confirmado

| Área | Evidencia |
| --- | --- |
| Next app | `products/tablet/app/app/**` |
| APIs Next | `products/tablet/app/app/api/**/route.ts` |
| Servidor | `products/tablet/app/src/server/**` |
| Prisma | `products/tablet/app/prisma/schema.prisma` |
| SQLite local | `products/tablet/app/data/tablet-pos.db` y `products/tablet/app/prisma/data/tablet-pos.db` |
| Scripts runtime | `scripts/tablet-runtime-gates.mjs`, `scripts/tablet-db.mjs` |
| QA tools | `tools/verify_tablet_*.mjs`, `tools/validate_package.py`, `tools/db_summary.py` |

## Scripts de package confirmados

| Script | Comando |
| --- | --- |
| `dev` | `next dev -p 3120` |
| `build` | `next build --webpack` |
| `start` | `next start -p 3120` |
| `typecheck` | `tsc --noEmit` |
| `check:package` | `python tools/validate_package.py .` |
| `check:all` | `python tools/validate_package.py . && tsc --noEmit` |
| `db:summary` | `python tools/db_summary.py data/tablet-pos.db` |
| `db:tablet:init` | `node scripts/tablet-db.mjs init` |
| `db:tablet:generate` | `node scripts/tablet-db.mjs generate` |
| `db:tablet:push` | `node scripts/tablet-db.mjs push` |
| `db:tablet:seed` | `node scripts/tablet-db.mjs seed` |
| `db:tablet:info` | `node scripts/tablet-db.mjs info` |
| `tablet:i01:runtime` | `node scripts/tablet-runtime-gates.mjs --mode=verify` |
| `verify:i01-runtime` | `node tools/verify_tablet_i01_runtime.mjs` |
| `db:tablet:init:safe` | `node scripts/tablet-runtime-gates.mjs --mode=db-init` |
| `typecheck:i01` | `node scripts/tablet-runtime-gates.mjs --mode=typecheck` |
| `verify:i02-catalogo` | `node tools/verify_tablet_i02_catalogo.mjs` |
| `verify:i03a-ticket-detail` | `node tools/verify_tablet_i03a_ticket_detail.mjs` |
| `verify:03-pos` | `node tools/verify_tablet_03_pos_unificado.mjs` |
| `verify:04-offline` | `node tools/verify_tablet_04_offline_export.mjs` |
| `verify:05-release` | `node tools/verify_tablet_05_release_readiness.mjs` |

## Verificación ejecutada/observada

| Check | Estado | Comentario |
| --- | --- | --- |
| `python tools/validate_package.py .` | FAILED | Falta Shared Kernel/licensing/shared-ui fuera del ZIP |
| `node tools/verify_tablet_i01_runtime.mjs` | PASS | Scaffolding runtime correcto |
| `node tools/verify_tablet_i02_catalogo.mjs` | PASS | Catálogo local correcto |
| `node tools/verify_tablet_i03a_ticket_detail.mjs` | FAIL | Falla endpoint directo y enlace codificado |
| `node tools/verify_tablet_04_offline_export.mjs` | FAIL | Falla render de outbox |
| `node tools/verify_tablet_05_release_readiness.mjs` | BLOCKED/TIME-LIMITED | Release queda bloqueado por I03A/T04; ejecución larga puede exceder límite local |

## Dependencias externas de runtime

Validación de paquete falla por referencias externas no incluidas en el ZIP:

- `../../../shared/twin-kernel/src/types/module.ts`
- `@shared-kernel/types/module`
- `@shared-kernel/runtime/module-registry`
- `@shared-kernel/data/twin-capability-manifest`
- `@shared-kernel/runtime/twin-capability-registry`
- `@shared-kernel/sync/events`
- `../../../../../../shared/licensing`
- `../../../../../shared/licensing`
- `shared-ui/prisma` CSS tokens/components
- `styles/prisma-visual-os` y herramientas relacionadas

Estos elementos son dependencias externas. No se duplican ni se documentan como ownership Tablet.

## Entrega staging

La entrega de Ronda 2 debe permanecer en:

`docs/atlas/_incoming/tablet/`

No debe escribirse en:

- `products/tablet/app/docs/atlas/`
- rutas de Mobile
- rutas de PC
- rutas de Shared Core
- rutas de Backoffice

## Criterios para promover a ruta final

1. Cerrar I03A.
2. Cerrar T04.
3. Ejecutar `verify:05-release` completo sin bloqueo.
4. Reintentar `check:package` en monorepo completo con dependencias compartidas presentes.
5. Confirmar assets PNG reales y derechos/uso.
6. Validar `atlas.tablet.json` contra schema si el coordinador define uno final.

## Riesgo operativo

El ZIP confirma un POS local con piezas reales, DB, APIs y verificadores. El riesgo principal no es falta de estructura; es declarar release antes de que los verificadores de ticket y offline dejen de gritar. Es el clásico local con caja funcionando pero ticketera floja: hay negocio, pero todavía te cae Profeco si te haces el valiente.