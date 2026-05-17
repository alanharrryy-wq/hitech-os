<!-- Generated from ATLAS_CHAT_SHARED_CORE.zip on 2026-05-08. Do not treat this as source code. -->

# ATLAS_SHARED_CORE_FUNCTIONAL_ENGINES

Estado: atlas inicial mejorado.
Alcance: motores compartidos que no pertenecen a una sola app: licensing, twin-kernel, verticals, tri-db, Prisma/global DB y productization schemas.

## Vista general

| Motor | Raíces | Responsabilidad | Consumidores confirmados/inferidos |
|---|---|---|---|
| Licensing | `shared/licensing/**`, `tooling/licensing/**`, docs productization license | Estado de licencia, planes, feature gates, firma, refresh, local store, server mock tooling | Tablet y PC por dependencias hacia `shared/licensing`; Mobile pendiente de confirmar. |
| Twin Kernel | `shared/twin-kernel/**`, `packages/shared-kernel/**` | Capability registry, parity matrix, module registry, sync events y regla twin | Tablet/PC por tsconfig/imports; Mobile referencia shared/twin-kernel en dependency hits. |
| Verticals | `shared/verticals/**`, `tools/verticals/**` | Vertical registry, capabilities, data extensions, events, permissions, UX ops y validation | Shared contract para Tablet/PC; app-specific adoption queda fuera. |
| Tri-DB bridge/status | `shared/tri-db/status.latest.json`, docs sync/hardening | Evidencia de bridge Tablet <-> PC/canonical y estado de sincronización | PC lee status; Tablet produce outbox; bridge no debe interrumpir venta. |
| Prisma/global DB | `prisma/**`, `docs/architecture/PRISMA_SCHEMA_OWNERSHIP.md` | Schema canónico/backoffice, migrations, seeds, smoke | PC/backoffice y consolidación; Tablet local schema autónomo según contrato. |
| Productization/runtime schemas | `docs/productization/**`, `tooling/productization/**` | Runtime config, support bundles, remote ops, messages, plugin manifests, customer runtime | Distribución, soporte, licencia y operaciones remotas. |

## Licensing engine

### Archivos fuente principales

| Archivo | Rol confirmado |
|---|---|
| `shared/licensing/index.ts` | Export barrel de módulos de licensing. |
| `shared/licensing/feature-keys.ts` | Feature keys y grupos básicos/pro/backoffice. |
| `shared/licensing/plan-catalog.ts` | Catálogo de planes, ranks y features por plan. |
| `shared/licensing/feature-resolver.ts` | Resolución allow/deny/warn/fallback por licencia y feature. |
| `shared/licensing/license-gate.ts` | API de estado/resolución y envelope `LICENSE_FEATURE_DENIED`. |
| `shared/licensing/license-schema.ts` | Validación estructural de licencia local. |
| `shared/licensing/license-loader.ts` | Carga local de licencia. |
| `shared/licensing/license-signature.ts`, `signed-license-types.ts` | Firma/licencia firmada. |
| `shared/licensing/local-license-store.ts` | Store local de licencia. |
| `tooling/licensing/**` | Fixtures, server mock, validators, dispatch guards, signing scan y matrices. |

### Planes detectados

`plan-catalog.ts` confirma planes como:

```text
TABLET_SOLO, TABLET_PRO, TABLET_PC_REQUIRED, DEVELOPMENT, TABLET_SOLO_FALLBACK
```

### Regla de continuidad

`feature-resolver.ts` confirma que `BASIC_POS_FEATURES` siguen permitidas bajo missing/invalid/suspended/revoked/expired mediante fallback policy, mientras funciones avanzadas quedan restringidas según estado. Esto protege la regla madre: Tablet vende sola.

### Riesgo

Modificar licensing puede interrumpir venta, habilitar funciones fuera de plan o romper UI de estado. Riesgo alto. Requiere fixtures y matrices antes de release.

## Twin Kernel engine

### Raíces

```text
packages/shared-kernel/README.md
shared/twin-kernel/src/index.ts
shared/twin-kernel/src/data/twin-capability-manifest.ts
shared/twin-kernel/src/data/twin-parity-matrix.ts
shared/twin-kernel/src/runtime/module-registry.ts
shared/twin-kernel/src/runtime/twin-capability-registry.ts
shared/twin-kernel/src/sync/events.ts
shared/twin-kernel/src/sync/twin-capability-events.ts
shared/twin-kernel/src/types/*.ts
shared/twin-kernel/src/validation/twin-capability-validator.ts
```

### Regla twin

Si cambia identidad compartida, naming compartido, eventos compartidos o sync contract, es twin change. Si sólo mejora operación local Tablet o PC, es local.

### Capacidades y paridad

El manifest contiene capacidades con dominios como catalog/inventory y roles por superficie (`source_of_truth`, `observer`, `executor`), `ownsWrites`, eventos permitidos, offline mode y audit level. Eso sirve como contrato de paridad para que PC y Tablet no se inventen ownership como compadres peleándose la bocina.

## Verticals engine

### Registro

Verticales detectados: `convenience, restaurant, pharmacy, beauty, hardware, apparel, repair, field_route, grocery_scale, food_truck`.

### Estados del registry detectados

| Status | Verticales |
|---|---|
| available | convenience, restaurant, pharmacy, beauty, hardware |
| draft | apparel, repair, field_route, grocery_scale, food_truck |

### Submotores verticales

| Submotor | Rutas |
|---|---|
| Data core/extensions | `shared/verticals/data-models/**` |
| Event catalogs/policies | `shared/verticals/events/**` |
| Permissions catalogs/policies | `shared/verticals/permissions/**` |
| Profiles/compatibility | `shared/verticals/registry/**` |
| UX operations | `shared/verticals/ux/**` |
| Validation fixtures/scenarios/smoke | `shared/verticals/validation/**` |
| Validation tools | `tools/verticals/validate_vertical_contracts_00a.py` a `validate_vertical_validation_fixtures_00f.py` |

### Regla de core data

`core-data-model.v0.json` declara entidades con `tabletLocal`, `pcAuthoritative` y `extensionAllowed`. Eso evita que un vertical meta mesas, recetas, reparaciones o atributos regulados dentro de `Product` sin contrato de extensión.

## Tri-DB bridge/status

`shared/tri-db/status.latest.json` confirma:

| Campo | Valor |
|---|---|
| Version | `20260506_v06` |
| Status | `READY` |
| Último bridge status | `READY` |
| Última generación sync | `2026-05-06T22:08:58.397578+00:00` |
| Tablas proyectadas | `23` |
| Rows insert/update | `586` |
| Outbox acknowledged | `72` |
| PC covers tablet | `True` |

### Lectura arquitectónica

- Tablet DB local existe y es readable según evidencia del status.
- PC/canonical DB existe y es readable según evidencia del status.
- PC cubre Tablet en paridad según status.
- `OutboxEvent` aparece en ambos lados, pero con estados distintos: Tablet `acked`, PC `failed/pending/sent` en el snapshot.

### Límite importante

`RUNTIME_MODES_CONTRACT.md` advierte no depender de `tools/_local/data/terminal-de-venta-system/canonical.db` para vender. Tri-DB status es evidencia/puente/operación de sync, no permiso para afectar venta local.

## Prisma/global DB engine

### Archivos

```text
prisma/schema.prisma
prisma/migrations/20260425000000_canonical_foundation/migration.sql
prisma/migrations/migration_lock.toml
prisma/seed.mjs
prisma/runtime-smoke.mjs
prisma/seeds/canonical.seed.json
prisma/seeds/pc_mass_catalog_04d.json
prisma/sql/seed-procurement.sql
```

### Modelos detectados

```text
Business, Store, Terminal, TaxRate, PriceList, PriceListItem, Product, Barcode, StockSnapshot, StockMovement, Supplier, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine, ReplenishmentSignal, CashSession, CashMovement, Sale, SaleLine, SaleReturn, AuditCount, OutboxEvent
```

### Regla de cambio

Cada cambio estructural debe tener migración, review, backup, validación, rollback y documentación. Además debe responder: qué módulo lo usa, qué pantalla lo muestra, qué evento lo afecta, qué permiso lo protege, qué pasa offline, qué reporte lo consume y qué plugin lo necesita.

## Productization/runtime schemas

### Dominios detectados

| Dominio | Rutas principales |
|---|---|
| Runtime config | `docs/productization/PRISMA_RUNTIME_CONFIG_*`, `tooling/productization/schemas/runtime-config.schema.json`, fixtures/examples runtime config |
| Support bundles | `PRISMA_SUPPORT_BUNDLE_LOCAL_04_*`, support schemas/test cases |
| Remote ops | `PRISMA_REMOTE_OPS_*`, remote command schemas/examples/test cases |
| Customer messaging/announcements | customer-message/announcement schemas and fixtures |
| Plugins | plugin manifest schemas, loader security cases, lifecycle playbook |
| License local/catalog | license-local examples, feature catalog, license event catalog |
| Security/privacy | `PRISMA_SECURITY_PRIVACY_BASELINE.md`, redaction schemas, support bundle allowlist/secret redaction |

## Change-intent map

| Intención | Motor | Primeros archivos | Verificación | Riesgo |
|---|---|---|---|---|
| Habilitar función por plan | Licensing | `feature-keys.ts`, `plan-catalog.ts`, `feature-resolver.ts` | license resolution matrix, fixtures signed/unsigned | Alto |
| Cambiar evento sync | Twin Kernel + contracts | `sync-event-contract.v1.json`, `shared/twin-kernel/src/sync/**` | validators, outbox cases, tri-db status | Crítico |
| Agregar vertical | Verticals | registry, profile, data extension, event/permission policy, UX op | validate_vertical_* y acceptance matrix | Alto |
| Cambiar schema root | Prisma | `schema.prisma`, migration, seed, smoke | runtime-smoke, migration validation, backup | Crítico |
| Cambiar soporte/runtime config | Productization | schemas, examples, docs productization | contract casebooks, schema validation | Medio/alto |

## Rollback por motor

| Motor | Rollback mínimo |
|---|---|
| Licensing | Restaurar plan catalog/feature resolver/fixtures previos y revalidar matrices. |
| Twin Kernel | Restaurar manifest/parity/events previos; si hubo event rename, mantener alias o migración. |
| Verticals | Revertir registry/profile/policies/fixtures del vertical; correr validators. |
| Tri-DB | No editar status a mano como solución; restaurar proceso/bridge que lo genera y validar DBs. |
| Prisma | Restaurar backup/migración previa; nunca borrar datos manualmente. |
| Productization | Revertir schemas/examples/manifests y correr test cases. |

## Pendientes funcionales

1. Confirmar si Mobile consume licensing o sólo Visual OS/twin-kernel en este snapshot.
2. Confirmar estado final de todos los verticales draft antes de exponerlos en UI.
3. Confirmar pipeline oficial que genera `shared/tri-db/status.latest.json`.
4. Confirmar si `packages/shared-kernel` reemplazará o convivirá con `shared/twin-kernel` como ubicación empaquetable final.
