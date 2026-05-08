# ATLAS PC FUNCTIONAL ENGINES - Ronda 2

Destino único: `docs/atlas/_incoming/pc/`  
Fuente única: `ATLAS_CHAT_PC.zip`

## Alcance

Registra motores, servicios, repositorios, validadores y flujos funcionales confirmados dentro de `source_snapshot/products/pc/app`. No atribuye ownership a Prisma canónico, Shared Core, twin-kernel, licensing ni tri-db.

## Mapa funcional general

```text
UI PC Backoffice
  -> API routes Next
  -> servicios server-side / lib services
  -> repositorios Prisma
  -> Prisma Client / dependencias externas
```

## Servicios server confirmados

| Archivo | Rol confirmado por ubicación/nombre |
|---|---|
| `src/server/services/catalog.service.ts` | Workspace/servicio catálogo |
| `src/server/services/inventory-ledger.service.ts` | Workspace/ledger inventario |
| `src/server/services/kpi-formulas.ts` | Fórmulas KPI y helpers de formato |
| `src/server/services/operation-control.service.ts` | Workspace/control operativo |
| `src/server/services/sync-ingest.service.ts` | Ingest de eventos sync |
| `src/server/services/sync-release.service.ts` | Release/estado sync |
| `src/server/services/tri-db-command.service.ts` | Comandos tri-db, dependencia externa/global |
| `src/server/services/tri-db-status.service.ts` | Estado tri-db, dependencia externa/global |

## Repositorios Prisma confirmados

| Archivo | Rol confirmado |
|---|---|
| `src/server/repositories/audit-repository.prisma.ts` | Auditoría/conteos |
| `src/server/repositories/barcode-repository.prisma.ts` | Barcodes |
| `src/server/repositories/catalog.repository.ts` | Catálogo |
| `src/server/repositories/inventory.repository.ts` | Inventario, movimientos y conteos |
| `src/server/repositories/operation.repository.ts` | Operación/backoffice |
| `src/server/repositories/outbox-repository.prisma.ts` | Outbox/sync |
| `src/server/repositories/product-repository.prisma.ts` | Producto |
| `src/server/repositories/purchase-order-repository.prisma.ts` | Órdenes de compra |
| `src/server/repositories/stock-repository.prisma.ts` | Stock |

## Validadores server confirmados

| Archivo | Función |
|---|---|
| `src/server/validators/catalog-quality.ts` | Calidad de catálogo |
| `src/server/validators/inventory-integrity.ts` | Integridad de inventario |
| `src/server/validators/procurement-integrity.ts` | Integridad procurement/compras |
| `src/server/validators/sync-event-contract.ts` | Contrato/validación de eventos sync |

## Motores por dominio

| Dominio | Evidencia principal | API/rutas relacionadas |
|---|---|---|
| Catálogo | `catalog.service.ts`, `catalog.repository.ts`, `product-repository.prisma.ts`, `barcode-repository.prisma.ts`, `catalog-quality.ts` | `/catalog`, `/catalogo-activo`, `/api/backoffice/catalog` |
| Inventario/stock | `inventory-ledger.service.ts`, `inventory.repository.ts`, `stock-repository.prisma.ts`, `inventory-integrity.ts` | `/stock`, `/movements`, `/counts`, `/api/backoffice/stock`, `/api/backoffice/movements`, `/api/backoffice/counts` |
| Auditoría | `audit-repository.prisma.ts`, `inventory.repository.ts` | `/audit`, `/auditoria-inventario`, `/api/backoffice/audit`, `/api/backoffice/audit/recent` |
| Operación/dashboard | `operation-control.service.ts`, `kpi-formulas.ts`, `operation.repository.ts` | `/dashboard`, `/metricas-dia`, `/tablero-kpi`, `/api/backoffice/dashboard` |
| Procurement | `purchase-order-repository.prisma.ts`, `procurement-integrity.ts`, libs procurement | `/purchasing`, `/receiving`, `/replenishment`, `/api/backoffice/purchasing`, `/api/backoffice/receiving`, `/api/backoffice/replenishment` |
| Sync | `sync-ingest.service.ts`, `sync-release.service.ts`, `outbox-repository.prisma.ts`, `src/server/sync/**`, `sync-event-contract.ts` | `/sync`, `/sync-operativo`, `/outbox-operativo`, `/api/sync/ingest`, `/api/backoffice/sync*` |
| Tri-db | `tri-db-command.service.ts`, `tri-db-status.service.ts` | `/api/sync/tri-db/run`; external/global dependency |
| Licencia | `src/server/licensing/pc-license-api.ts`, `pc-license-refresh.ts`, `pc-license-service.ts` | `/settings/license`, `/api/license/*`; depends on `shared/licensing` |
| Proveedores | `src/lib/suppliers/**`, `components/suppliers/**` | `/proveedores`, `/api/proveedores/**` |

## Motor de proveedores

La familia `src/lib/suppliers/**` es un bloque funcional amplio. Evidencias por nombre de archivo y verificadores:

| Pieza | Rol |
|---|---|
| `action-reducer.ts` | Reducción de acciones/eventos |
| `client-persistence.ts` | Persistencia cliente |
| `data-quality.ts` | Calidad de datos |
| `event-catalog.ts` | Catálogo de eventos |
| `export-contracts.ts` | Contratos de exportación |
| `in-memory-repository.ts` | Repositorio en memoria para escenarios/tests |
| `lifecycle-scenarios.ts` | Escenarios lifecycle |
| `lifecycle-validator.ts` | Validación lifecycle |
| `prisma-mapping.ts` | Mapeo hacia persistencia Prisma |
| `repository-contract.ts` | Contrato de repositorio |
| `transition-policy.ts` | Política de transiciones |

### APIs proveedores confirmadas

- `/api/proveedores/auditoria`
- `/api/proveedores/calendario`
- `/api/proveedores/calidad-datos`
- `/api/proveedores/compra-inteligente`
- `/api/proveedores/compra-inteligente/crear-pedido`
- `/api/proveedores/compra-inteligente/simular`
- `/api/proveedores/cuentas-pagar`
- `/api/proveedores/cuentas-pagar/registrar-pago`
- `/api/proveedores/exportables`
- `/api/proveedores/inventario`
- `/api/proveedores/operacion`
- `/api/proveedores/pedidos`
- `/api/proveedores/qa/escenarios`
- `/api/proveedores/recepciones`
- `/api/proveedores/recepciones/confirmar`
- `/api/proveedores/senales`

## Sync y tri-db

PC confirma superficies y servicios sync, pero el contrato global de eventos y tri-db queda externo.

| Elemento | Clasificación |
|---|---|
| `sync-ingest.service.ts` | Servicio PC |
| `sync-release.service.ts` | Servicio PC |
| `outbox-repository.prisma.ts` | Repositorio PC |
| `src/server/sync/events.ts`, `outbox.ts` | Soporte server PC |
| `tri-db-command.service.ts`, `tri-db-status.service.ts` | Servicios PC que consumen dependencia externa/global |
| `shared/tri-db` | Dependencia externa/global |

## Licenciamiento

`src/server/licensing/**` confirma adaptación PC para licencia:

- `pc-license-api.ts`
- `pc-license-refresh.ts`
- `pc-license-service.ts`

La fuente de reglas/licensing core se mantiene externa: `shared/licensing`.

## Prisma y persistencia

Confirmado:

- PC usa `@prisma/client`.
- PC tiene repositorios `.prisma.ts` y repositorios server.
- `src/server/prisma/client.ts` centraliza cliente/fallback runtime.
- `products/pc/app/prisma/schema.prisma` existe en snapshot.

Pendiente:

- Schema canónico real fuera del ZIP.
- Migraciones reales.
- Disponibilidad de DB completa.

## Verificadores funcionales

Se detectan 34 herramientas/verificadores, incluyendo:

- `tools/validate_package.py`
- `tools/smoke_pc_i01_routes.mjs`
- `tools/run_pc_suppliers_lifecycle_scenarios_02.mjs`
- `tools/verify_pc_catalog_02.mjs`
- `tools/verify_pc_stock_counts_audit_03.mjs`
- `tools/verify_pc_sync_ingest_06.mjs`
- verificadores suppliers, dashboard, visual, runtime y registry.

## Límites de inferencia

No se afirma pass de compilación ni runtime porque el ZIP no incluye dependencias externas. Motores y responsabilidades se declaran por evidencia de archivos, imports, rutas y nombres confirmados, no por ejecución final.
