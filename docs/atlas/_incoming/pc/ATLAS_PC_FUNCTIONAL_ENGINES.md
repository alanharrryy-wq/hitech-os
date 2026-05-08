# ATLAS PC FUNCTIONAL ENGINES - Ronda 2

Destino único: `docs/atlas/_incoming/pc/`  
Fuente única: `ATLAS_CHAT_PC.zip`

## Alcance

Este documento registra motores, servicios, repositorios, validadores y flujos funcionales confirmados en PC. No modifica código y no atribuye ownership a Shared Core, Prisma canónico, twin-kernel, licensing ni tri-db.

## Mapa funcional general

```text
UI PC Backoffice
  -> API routes Next
  -> servicios server-side
  -> repositorios Prisma
  -> Prisma client / schema canónico externo

UI PC Backoffice
  -> src/lib/*
  -> motores de dominio, datasets de pantalla y clientes API
```

## Motores por dominio

| Dominio | Evidencia principal | Responsabilidad PC confirmada |
|---|---|---|
| Catálogo | `src/server/services/catalog.service.ts`, `src/server/repositories/catalog.repository.ts` | Workspace de catálogo, productos, categorías, calidad y exportación |
| Inventario | `src/server/services/inventory-ledger.service.ts`, `src/server/repositories/inventory.repository.ts` | Snapshots, movimientos, conteos, ajustes y reorder |
| Compras | `src/server/services/purchase.service.ts`, `src/server/repositories/purchase.repository.ts` | Órdenes, recepciones y sugerencias de compra |
| Operación | `src/server/services/operation-control.service.ts`, `src/server/repositories/operation.repository.ts` | Control operativo de backoffice |
| Dashboard/KPI | `src/server/services/dashboard.service.ts`, `src/server/services/kpi-formulas.ts`, `src/server/repositories/dashboard.repository.ts` | Resumen ejecutivo, métricas y fórmulas KPI |
| Sync | `src/server/sync/**`, `src/lib/sync-ingest/**`, `src/server/repositories/sync.repository.ts` | Ingest, queue, conflicts, duplicates, rejected y status |
| Proveedores | `src/lib/suppliers/**`, `/api/suppliers/**` | Recomendaciones, lifecycle, recepción, pagos, import/export, simulación y calidad |
| Settings/licencias | `src/server/repositories/settings.repository.ts`, `src/server/licensing/**` | Configuración PC, usuarios y feature gates hacia licensing externo |

## Repositorios server confirmados

| Archivo | Evidencia funcional |
|---|---|
| `products/pc/app/src/server/repositories/catalog.repository.ts` | Métodos para productos y categorías; usa Prisma |
| `products/pc/app/src/server/repositories/inventory.repository.ts` | Snapshots, movimientos, conteos; usa modelos de inventario/auditoría |
| `products/pc/app/src/server/repositories/purchase.repository.ts` | Compras, recepciones y sugerencias |
| `products/pc/app/src/server/repositories/operation.repository.ts` | Superficies operativas |
| `products/pc/app/src/server/repositories/dashboard.repository.ts` | Resumen de dashboard |
| `products/pc/app/src/server/repositories/settings.repository.ts` | Settings, usuarios y licencias |
| `products/pc/app/src/server/repositories/sync.repository.ts` | Estado, queue, conflictos y rejected |
| `products/pc/app/src/server/repositories/audit-repository.prisma.ts` | Conteos/auditoría |
| `products/pc/app/src/server/repositories/barcode-repository.prisma.ts` | Barcodes recientes |

## Servicios server confirmados

| Archivo | Rol |
|---|---|
| `src/server/services/catalog.service.ts` | Construcción del workspace de catálogo |
| `src/server/services/inventory-ledger.service.ts` | Construcción del workspace de inventario |
| `src/server/services/purchase.service.ts` | Órdenes, recepciones y compras |
| `src/server/services/operation-control.service.ts` | Vista/estado operativo |
| `src/server/services/dashboard.service.ts` | Dashboard y resumen |
| `src/server/services/kpi-formulas.ts` | Fórmulas KPI y helpers de formato |

## Validadores server confirmados

| Archivo | Función |
|---|---|
| `src/server/validators/catalog-quality.ts` | Calidad de catálogo |
| `src/server/validators/inventory-integrity.ts` | Integridad de inventario |
| `src/server/validators/purchase-integrity.ts` | Integridad de compras/recepción |
| `src/server/validators/settings-integrity.ts` | Integridad de settings/licencias |

## Motor de proveedores

La familia `src/lib/suppliers/**` es el bloque funcional más amplio detectado. Está orientada a lifecycle, políticas, recomendaciones, recepción, órdenes, pagos, exportación, importación, simulación y calidad.

| Pieza detectada | Rol probable confirmado por nombre/uso |
|---|---|
| `lifecycle-scenarios.ts` | Escenarios de vida de proveedor |
| `lifecycle-validator.ts` | Validación de transiciones |
| `transition-policy.ts` | Políticas de transición |
| `event-catalog.ts` | Catálogo de eventos de proveedores |
| `prisma-mapping.ts` | Mapeo hacia persistencia Prisma |
| `action-reducer.ts` | Reducción de acciones/eventos |
| `repository-contract.ts` | Contrato de repositorio de proveedores |
| `in-memory-repository.ts` | Repositorio en memoria para fixtures/tests |
| `data-quality.ts` | Calidad de datos |
| `export-contracts.ts` | Contratos de exportación |

### APIs de proveedores

| API | Responsabilidad |
|---|---|
| `/api/suppliers` | Superficie base de proveedores |
| `/api/suppliers/recommendations` | Recomendaciones |
| `/api/suppliers/orders` | Órdenes |
| `/api/suppliers/receptions` | Recepción |
| `/api/suppliers/payments` | Pagos |
| `/api/suppliers/import` | Importación |
| `/api/suppliers/export` | Exportación |
| `/api/suppliers/simulate` | Simulación |
| `/api/suppliers/health` | Salud/calidad |

## Motor de sync

### Responsabilidades PC confirmadas

- Ingest de payloads sync.
- Clasificación de duplicados.
- Gestión de conflictos.
- Cola/rejected/status.
- Exposición de rutas para observabilidad de sync.

### Dependencias externas

El contrato de eventos y reconciliación global queda fuera de PC. El ZIP incluye `global_context/docs/contracts/EVENT_CONTRACT.md` y `SYNC_RECONCILIATION_CONTRACT.md` como contexto global, no como implementación PC.

## Licenciamiento

`src/server/licensing/**` y `/api/settings/licenses` confirman gates/licencias en PC. Sin embargo, la fuente de verdad de licensing está referenciada como `shared/licensing`, por tanto:

- PC puede aplicar gates y mostrar estado.
- PC no posee el contrato global de licencias.
- Las reglas finales de licensing quedan pendientes de dependencia externa.

## Prisma y persistencia

### Confirmado

- PC usa `@prisma/client`.
- PC tiene repositorios Prisma.
- `src/server/prisma/client.ts` centraliza cliente/fallback runtime.
- `products/pc/app/prisma/schema.prisma` existe en el snapshot.

### Pendiente

- El schema local aparece como stub/transicional.
- Los scripts apuntan a Prisma canónico externo.
- El schema canónico y migraciones reales deben confirmarse en repo completo.

## Fixtures y escenarios

`fixtures/**` contiene material de QA para catálogo, inventario, compras, dashboard, runtime, sync y proveedores. Estos fixtures respaldan el atlas como evidencia de comportamiento esperado, pero no sustituyen ejecución real.

## Verificadores funcionales

Se detectan 34 herramientas/verificadores en `tools/**`, incluyendo package validator, smoke routes, runtime checks, suppliers lifecycle scenarios, sync y verificadores PC por iteración.

## Límites de inferencia

No se puede afirmar desde el ZIP:

- Que todos los servicios compilen en repo completo.
- Que la base canónica esté disponible.
- Que las migraciones estén aplicadas.
- Que todos los endpoints respondan en runtime.
- Que los gates de licencia estén conectados a datos reales.

## Corrección de Ronda 1

En esta ronda, los motores funcionales no se documentan como “mágicos” ni como propiedad global. Cada bloque queda amarrado a archivos de PC o marcado como dependencia externa. Es la diferencia entre decir “la cocina hace comida” y señalar quién trae la tortilla, quién prende el comal y quién cobra, chingón pero con recibo.