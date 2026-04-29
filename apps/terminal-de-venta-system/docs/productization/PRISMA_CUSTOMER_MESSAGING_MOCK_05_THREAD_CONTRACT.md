# PRISMA Customer Messaging Mock 05 — Thread Contract


> Paquete: `PRISMA_CENTRO_PRISMA_UI_SHELL_03`  
> Versión documental: `1.1.0`  
> Fecha: `2026-04-28`  
> Incluye documentación consolidada para iteraciones `03`, `04` y `05`.  
> Alcance: docs, schemas, examples, test-cases, manifest y checksums.  
> Restricción: no instala runtime, no crea rutas Next, no toca DB, no toca `.env`, no ejecuta sync remoto y no procesa pagos.

## Base que no se contradice

Este paquete asume que ya existen y quedan como piso:

- `PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00`: contratos base de customer operations, remote ops, updates, soporte, plugins, licencias y frontera de no procesamiento bancario.
- `PRISMA_RUNTIME_CONFIG_BOUNDARY_01`: separación repo / release / runtime cliente, reglas de `ProgramData`, logs, backups, config y prohibición de depender de `cwd`.
- `PRISMA_LICENSE_LOCAL_MOCK_02`: planes, feature flags mock, entitlements, offline grace y contrato local de licencia.

Nada de este paquete invalida lo anterior. Esto no viene a patear la mesa, viene a poner mantel, cubiertos y letrero de “no meter los dedos al enchufe”.


## Thread

| Campo | Tipo | Requerido | Regla |
| --- | --- | --- | --- |
| threadId | string | sí | ID local |
| businessId | string | sí | puede enmascararse en diagnóstico |
| deviceId | string | no | dispositivo origen |
| surface | pc/tablet | sí | superficie |
| category | enum | sí | support/license/diagnostics/plugins/updates/general |
| status | enum | sí | draft/local_only/queued_mock/read/closed_local/blocked_no_server |
| title | string | sí | breve |
| createdAt | date-time | sí | ISO |
| updatedAt | date-time | sí | ISO |
| contextRefs | array | no | refs controladas |

## Message

| Campo | Tipo | Requerido | Regla |
| --- | --- | --- | --- |
| messageId | string | sí | ID local |
| threadId | string | sí | thread padre |
| senderType | enum | sí | customer/provider/system_mock |
| body | string | sí | límite por superficie |
| status | enum | sí | draft/created_local/queued_mock/failed_mock/read_local |
| createdAt | date-time | sí | ISO |
| attachments | array | no | refs controladas |
| contextRefs | array | no | rutas, plan, paquete |

## Context refs permitidos

| Tipo | Ejemplo | Uso |
| --- | --- | --- |
| route | pc.center.diagnostics | referir pantalla |
| license | license.local.status | referir estado |
| diagnostic | bundle.future.id | referir bundle futuro |
| plugin | plugin.catalog.id | referir plugin |
| package | PRISMA_SUPPORT_BUNDLE_LOCAL_04 | referir paquete |
