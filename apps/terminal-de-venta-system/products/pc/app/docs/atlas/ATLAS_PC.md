# ATLAS PC - Ronda 2

Fuente única: `ATLAS_CHAT_PC.zip`
Destino de staging: `docs/atlas/_incoming/pc/`
Raíz analizada dentro del ZIP: `source_snapshot/products/pc/app`

## Reglas de esta entrega

- No se modifica código funcional.
- No se escribe en `products/pc/app/docs/atlas/`.
- No se tocan Mobile, Tablet ni Shared Core.
- Todo lo no confirmable con el ZIP queda pendiente.
- Prisma, Shared Core, `shared/twin-kernel`, `shared/licensing`, `shared/tri-db`, Shared UI y Visual OS global se documentan como dependencias externas.

## Identidad confirmada de PC

PC es el backoffice administrativo: gobierno operativo para catálogo, inventario, movimientos, conteos, compras, recepción, reabasto, auditoría, sync, proveedores, settings, licencias y dashboard.

Regla de arquitectura confirmada por el paquete:

```text
Tablet vende sola.
PC gobierna cuando existe.
Shared Kernel es contrato.
Sync es puente.
Eventos son verdad operacional.
```

## Conteos confirmados

| Elemento | Conteo |
|---|---:|
| Archivos inventariados de PC | 400 |
| Rutas visibles | 47 |
| Rutas API | 36 |
| Componentes TSX | 39 |
| Repositorios server | 9 |
| Servicios/motores detectados | 44 |
| Validadores server | 4 |
| Herramientas/verificadores | 34 |
| Markdown docs PC | 78 |
| Assets públicos presentes | 6 |
| Assets listados por manifest | 10 |

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

## Rutas visibles confirmadas desde `analysis/routes_and_apis.json`

| Grupo | Rutas |
|---|---|
| Gobierno/guía | `/`, `/gobierno`, `/glosario`, `/referencia-visual` |
| Dashboard/operación | `/dashboard`, `/alertas-ejecutivas`, `/alertas-operativas`, `/metricas-dia`, `/scorecards-negocio`, `/tablero-kpi`, `/vistas-ejecutivas` |
| Catálogo | `/catalog`, `/catalogo-activo`, `/existencias-criticas`, `/integridad-barcodes`, `/salud-barcodes`, `/politica-precios`, `/validacion-catalogo` |
| Inventario | `/stock`, `/movements`, `/counts`, `/auditoria-inventario`, `/conteos-operativos`, `/sync-operativo`, `/outbox-operativo` |
| Compras/recepción/reabasto | `/purchasing`, `/receiving`, `/replenishment`, `/ordenes-compra`, `/recepcion-proveedor`, `/incidencias-recepcion`, `/forecast-basico`, `/senal-reabasto` |
| Proveedores | `/proveedores` |
| Sync | `/sync` |
| Settings/licencia | `/settings`, `/settings/license` |
| Reportes/detalle | `/exportables`, `/contratos-reporte`, `/detalle-registros`, `/tablas-operativas` |
| UX/filtros/estado | `/filtros-avanzados`, `/filtros-fecha`, `/estados-operativos`, `/acciones-masivas`, `/ajustes-inventario` |

## APIs confirmadas desde `analysis/routes_and_apis.json`

| Grupo | Rutas API |
|---|---|
| Backoffice | `/api/backoffice/audit/recent`, `/api/backoffice/audit`, `/api/backoffice/catalog`, `/api/backoffice/counts`, `/api/backoffice/dashboard`, `/api/backoffice/movements`, `/api/backoffice/purchasing`, `/api/backoffice/receiving`, `/api/backoffice/replenishment`, `/api/backoffice/stock` |
| Backoffice sync | `/api/backoffice/sync/conflicts`, `/api/backoffice/sync/ingest`, `/api/backoffice/sync` |
| Licencia | `/api/license/features/[key]`, `/api/license/features`, `/api/license/refresh`, `/api/license/refresh/status`, `/api/license/status` |
| Proveedores | `/api/proveedores/auditoria`, `/api/proveedores/calendario`, `/api/proveedores/calidad-datos`, `/api/proveedores/compra-inteligente/crear-pedido`, `/api/proveedores/compra-inteligente`, `/api/proveedores/compra-inteligente/simular`, `/api/proveedores/cuentas-pagar/registrar-pago`, `/api/proveedores/cuentas-pagar`, `/api/proveedores/exportables`, `/api/proveedores/inventario`, `/api/proveedores/operacion`, `/api/proveedores/pedidos`, `/api/proveedores/qa/escenarios`, `/api/proveedores/recepciones/confirmar`, `/api/proveedores/recepciones`, `/api/proveedores/senales` |
| Sync / tri-db | `/api/sync/ingest`, `/api/sync/tri-db/run` |

## Capas confirmadas

| Capa | Responsabilidad | Evidencia |
|---|---|---|
| `app/**` | Rutas visibles, layout global, CSS de superficie y API routes | `source_snapshot/products/pc/app/app/**` |
| `components/**` | Shell, tablas, tarjetas, workspaces, proveedores, licencia y sync | `source_snapshot/products/pc/app/components/**` |
| `src/composition/**` | Registro de módulos y navegación | `module-registry.ts` |
| `src/modules/**` | Manifiestos y tipos por dominio | `module.manifest.ts`, `types.ts` |
| `src/server/services/**` | Workspaces, sync ingest/release, tri-db status/command, KPIs | servicios server |
| `src/server/repositories/**` | Persistencia vía Prisma Client | repositorios Prisma |
| `src/lib/**` | Datos de pantalla, motores suppliers, servicios cliente y backoffice helpers | lib PC |
| `tools/**` | Verificadores y validadores locales | `verify*.mjs`, smoke, validate_package |

## Dependencias externas

| Dependencia | Evidencia | Clasificación |
|---|---|---|
| Prisma canónico | scripts `db:canonical:*`, schema local transicional | Externa/global |
| `@prisma/client` | `package.json`, repositorios | Runtime externo usado por PC |
| `shared/twin-kernel` / `@shared-kernel/*` | `tsconfig.paths`, module manifests | Externa compartida |
| `shared/licensing` | licensing gates y API licencia | Externa compartida |
| `shared/tri-db` | servicios tri-db/status y scripts | Externa/global |
| `shared-ui/prisma`, `styles/prisma-visual-os` | CSS imports y Visual OS binding | Externa visual/global |

## Hallazgos corregidos de Ronda 1

1. `atlas.pc.json` sigue el schema canónico `templates/prisma-atlas.schema.json` con `atlasId`, `app`, `root`, `version`, `changeIntents` y `verification`.
2. La entrega queda exclusivamente en `docs/atlas/_incoming/pc/`.
3. Dependencias globales quedan como externas, no propiedad PC.
4. Los assets faltantes se documentan como pendiente, sin inventarlos.
5. No se sube nada a rutas finales.

## Pendientes principales

- Confirmar Prisma canónico real fuera del ZIP.
- Confirmar disponibilidad de `shared/twin-kernel`, `shared/licensing`, `shared/tri-db`, `shared-ui/prisma` y `styles/prisma-visual-os` en repo completo.
- Resolver cuatro assets listados por manifest pero ausentes de `public/`.
- Ejecutar `check:package`, `typecheck`, `build` y verificadores en repo completo.
