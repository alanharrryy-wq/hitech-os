# ATLAS PC - Ronda 2

Fuente única: `ATLAS_CHAT_PC.zip`  
Destino de staging: `docs/atlas/_incoming/pc/`  
Raíz analizada dentro del ZIP: `source_snapshot/products/pc/app`

## Reglas de esta entrega

- No se modifica código funcional.
- No se escriben archivos en `products/pc/app/docs/atlas/`.
- No se tocan Mobile, Tablet ni Shared Core.
- Todo lo no confirmable con el ZIP queda como pendiente.
- Prisma, Shared Core, `shared/twin-kernel`, `shared/licensing` y `shared/tri-db` se documentan como dependencias externas.

## Identidad confirmada de PC

PC es el backoffice administrativo del sistema. En el paquete se confirma como superficie de gobierno operativo para catálogo, inventario, movimientos, conteos, compras, recepción, reabasto, auditoría, sync, proveedores, settings y dashboard.

Regla de arquitectura repetida por el paquete:

```text
Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.
```

## Inventario confirmado

| Área | Evidencia en ZIP |
|---|---|
| App Next | `products/pc/app/app/**` |
| Componentes | `products/pc/app/components/**` |
| Server/repositories/services | `products/pc/app/src/server/**` |
| Lógica cliente y motores | `products/pc/app/src/lib/**` |
| Manifiestos de módulos | `products/pc/app/src/modules/**/module.manifest.ts` |
| Composición/navegación | `products/pc/app/src/composition/module-registry.ts` |
| Prisma local | `products/pc/app/prisma/schema.prisma` |
| Verificadores | `products/pc/app/tools/**` |
| Fixtures QA | `products/pc/app/fixtures/**` |
| Documentación PC | `products/pc/app/docs/**` |

## Conteos confirmados

| Elemento | Conteo |
|---|---:|
| Archivos inventariados de PC | 400 |
| Rutas visibles | 47 |
| Rutas API | 36 |
| Componentes | 39 |
| Repositorios server | 9 |
| Servicios/motores detectados | 44 |
| Validadores server | 4 |
| Herramientas/verificadores | 34 |
| Markdown docs PC | 78 |
| Assets públicos presentes | 6 |
| Assets listados en manifest | 10 |

## Stack confirmado

| Campo | Valor |
|---|---|
| Package | `@hitech/pc` |
| Versión | `6.1.1` |
| Next | `16.1.6` |
| React | `18.3.1` |
| Prisma client | `5.21.1` |
| TypeScript | `5.8.2` |
| Puerto dev/start | `3130` |
| Node engine | `>=20.0.0 <26.0.0` |

## Scripts confirmados

| Script | Comando |
|---|---|
| `dev` | `next dev -p 3130` |
| `build` | `next build --webpack` |
| `start` | `next start -p 3130` |
| `typecheck` | `tsc --noEmit` |
| `check:package` | `python tools/validate_package.py .` |
| `check:all` | `python tools/validate_package.py . && tsc --noEmit` |
| `db:canonical:generate` | `python ../../../tooling/scripts/generate_prisma_canonical.py pc` |
| `db:canonical:migrate` | referencia a tooling externo de Prisma canónico |

## Rutas visibles confirmadas

Las 47 rutas visibles se derivan de `analysis/routes_and_apis.json` y archivos `app/**/page.tsx`.

Principales superficies:

| Dominio | Rutas confirmadas |
|---|---|
| Dashboard/home | `/`, `/dashboard` |
| Catálogo | `/catalogo`, `/catalogo-global`, `/catalogo-global-v2`, `/catalogo-multisucursal` |
| Inventario/stock | `/inventario`, `/stock`, `/stock-historial`, `/stock-sucursal`, `/ajustes-inventario` |
| Compras/recepción/reabasto | `/compras`, `/compras-inteligentes`, `/recepcion`, `/reabasto`, `/transferencias` |
| Auditoría | `/auditoria`, `/conteos`, `/conteos-ciclicos`, `/historial-conteos` |
| Operación | `/operacion`, `/operacion-dashboard`, `/operaciones`, `/acciones-masivas` |
| Sync | `/sync`, `/sync-health` |
| Proveedores | `/proveedores`, `/proveedores-analytics`, `/proveedores-calidad`, `/proveedores-compras`, `/proveedores-eventos`, `/proveedores-historial`, `/proveedores-lifecycle`, `/proveedores-lista`, `/proveedores-matriz`, `/proveedores-recepcion`, `/proveedores-reconciliacion`, `/proveedores-reportes`, `/proveedores-sugerencias` |
| Admin/configuración | `/settings`, `/licencias`, `/roles-permisos`, `/usuarios-sesiones`, `/notificaciones` |
| Ejecutivas/otros | `/alertas-ejecutivas`, `/auditoria-operativa`, `/cortes-caja`, `/kpis`, `/mermas`, `/ordenes`, `/reportes-exportables`, `/vistas-globales` |

## APIs confirmadas

Se confirman 36 rutas API bajo `app/api/**/route.ts`. La mayoría exporta `GET` y algunas flujos operativos exportan `POST`.

| Área API | Rutas representativas |
|---|---|
| Dashboard | `/api/dashboard/summary` |
| Catálogo | `/api/catalog/brands`, `/api/catalog/categories`, `/api/catalog/export`, `/api/catalog/productos`, `/api/catalog/quality`, `/api/catalog/tags` |
| Inventario | `/api/inventory/adjustments`, `/api/inventory/counts`, `/api/inventory/movements`, `/api/inventory/reorder`, `/api/inventory/snapshots` |
| Compras | `/api/purchases/orders`, `/api/purchases/receptions`, `/api/reorder/suggestions` |
| Sync | `/api/sync/conflicts`, `/api/sync/duplicates`, `/api/sync/ingest`, `/api/sync/queue`, `/api/sync/rejected`, `/api/sync/status` |
| Settings/licencias | `/api/settings`, `/api/settings/users`, `/api/settings/licenses` |
| Proveedores | `/api/suppliers`, `/api/suppliers/export`, `/api/suppliers/health`, `/api/suppliers/import`, `/api/suppliers/orders`, `/api/suppliers/payments`, `/api/suppliers/recommendations`, `/api/suppliers/receptions`, `/api/suppliers/simulate` |
| Backoffice | `/api/backoffice/catalog`, `/api/backoffice/stock`, `/api/backoffice/sync` |

## Módulos registrados

`src/composition/module-registry.ts` y `src/modules/**/module.manifest.ts` confirman manifiestos tipo `TwinModuleManifest` importados desde `@shared-kernel`. Por lo tanto, el contrato del manifiesto es dependencia externa, no propiedad PC.

| Módulo/área | Ruta |
|---|---|
| Catálogo | `/catalogo` |
| Inventario | `/inventario` |
| Compras | `/compras` |
| Recepción | `/recepcion` |
| Reabasto | `/reabasto` |
| Auditoría | `/auditoria` |
| Sync | `/sync` |
| Settings | `/settings` |
| Licencias | `/licencias` |
| Proveedores | `/proveedores` |

## Arquitectura confirmada

### Capas internas PC

| Capa | Rol |
|---|---|
| `app/` | Rutas Next, layouts, páginas y API routes |
| `components/` | UI, shell, tarjetas, tablas, landing, backoffice y proveedores |
| `src/composition/` | Registro y navegación de módulos PC |
| `src/modules/` | Manifiestos y tipos por dominio |
| `src/lib/` | Datos de pantalla, clientes API, motores de proveedores y sync ingest |
| `src/server/` | Prisma client, repositorios, servicios, validadores y licensing gates |
| `tools/` | Verificación, smoke tests, package validator y checks visuales/runtime |

### Dependencias externas documentadas

| Dependencia | Evidencia | Clasificación |
|---|---|---|
| Prisma canónico | scripts `db:canonical:*`, `prisma/schema.prisma` transitional stub | Externa/global |
| `@prisma/client` | `package.json`, repositorios server | Externa runtime |
| `@shared-kernel/*` / `shared/twin-kernel` | `tsconfig.paths`, module manifests | Externa compartida |
| `shared/licensing` | referencias en licenciamiento PC | Externa compartida |
| `shared/tri-db` | referencias de tooling/runtime | Externa/global |
| `shared-ui/prisma` y `styles/prisma-visual-os` | CSS imports y Visual OS binding | Externa visual/global |

## Repositorios Prisma detectados

| Archivo | Modelo/uso detectado |
|---|---|
| `src/server/repositories/catalog.repository.ts` | productos/categorías |
| `src/server/repositories/inventory.repository.ts` | snapshots, movimientos, conteos |
| `src/server/repositories/purchase.repository.ts` | órdenes, recepciones, sugerencias |
| `src/server/repositories/operation.repository.ts` | operación/backoffice |
| `src/server/repositories/audit-repository.prisma.ts` | auditoría/conteos |
| `src/server/repositories/barcode-repository.prisma.ts` | barcodes |
| `src/server/repositories/settings.repository.ts` | settings/usuarios/licencias |
| `src/server/repositories/sync.repository.ts` | sync status/conflicts/queue |
| `src/server/repositories/dashboard.repository.ts` | resumen operativo |

## Servicios y motores detectados

| Familia | Evidencia |
|---|---|
| Catálogo | `src/server/services/catalog.service.ts` |
| Inventario | `src/server/services/inventory-ledger.service.ts` |
| Compras | `src/server/services/purchase.service.ts` |
| Operación | `src/server/services/operation-control.service.ts` |
| Dashboard/KPIs | `src/server/services/dashboard.service.ts`, `kpi-formulas.ts` |
| Sync | `src/server/sync/**`, `src/lib/sync-ingest/**` |
| Proveedores | `src/lib/suppliers/**` |
| Licenciamiento | `src/server/licensing/**` |
| Validadores | `src/server/validators/**` |

## Hallazgos corregidos de Ronda 1

1. `atlas.pc.json` ahora sigue el schema canónico `templates/prisma-atlas.schema.json` con campos requeridos `atlasId`, `app`, `root`, `version`, `changeIntents` y `verification`.
2. La entrega para GitHub queda solo en `docs/atlas/_incoming/pc/`.
3. Las dependencias globales no se documentan como propiedad PC.
4. Los assets faltantes quedan como cobertura/open question y no se inventan.
5. No se sube nada a rutas finales del proyecto.

## Pendientes principales

- Confirmar schema Prisma canónico real fuera del ZIP.
- Confirmar disponibilidad de `shared/twin-kernel`, `shared/licensing`, `shared/tri-db`, `shared-ui/prisma` y `styles/prisma-visual-os` en repo completo.
- Resolver assets públicos listados en manifest pero ausentes en `public/`.
- Ejecutar `typecheck`, `build` y verificadores en repo completo, no en snapshot parcial.
