# PRISMA 03-04-05 — Field Catalog


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


## Catálogo de campos

| Grupo | Campo | Tipo lógico | Requerido | Contrato |
| --- | --- | --- | --- | --- |
| center_route | routeId | documental | sí | ver schema correspondiente |
| center_route | surface | documental | sí | ver schema correspondiente |
| center_route | pathKey | documental | sí | ver schema correspondiente |
| center_route | title | documental | sí | ver schema correspondiente |
| center_route | permission | documental | sí | ver schema correspondiente |
| center_route | initialMode | documental | según caso | ver schema correspondiente |
| center_route | blocksCheckout | documental | según caso | ver schema correspondiente |
| center_route | relatedPackage | documental | según caso | ver schema correspondiente |
| module_card | cardId | documental | sí | ver schema correspondiente |
| module_card | routeId | documental | sí | ver schema correspondiente |
| module_card | title | documental | sí | ver schema correspondiente |
| module_card | state | documental | sí | ver schema correspondiente |
| module_card | allowedActions | documental | sí | ver schema correspondiente |
| module_card | prohibitedActions | documental | según caso | ver schema correspondiente |
| module_card | emptyStateCopy | documental | según caso | ver schema correspondiente |
| module_card | riskNote | documental | según caso | ver schema correspondiente |
| support_bundle | bundleId | documental | sí | ver schema correspondiente |
| support_bundle | schemaVersion | documental | sí | ver schema correspondiente |
| support_bundle | createdAt | documental | sí | ver schema correspondiente |
| support_bundle | businessIdMasked | documental | sí | ver schema correspondiente |
| support_bundle | deviceIdMasked | documental | sí | ver schema correspondiente |
| support_bundle | runtimeMode | documental | según caso | ver schema correspondiente |
| support_bundle | includedSections | documental | según caso | ver schema correspondiente |
| support_bundle | checksums | documental | según caso | ver schema correspondiente |
| diagnostic_snapshot | snapshotId | documental | sí | ver schema correspondiente |
| diagnostic_snapshot | runtimeMode | documental | sí | ver schema correspondiente |
| diagnostic_snapshot | surface | documental | sí | ver schema correspondiente |
| diagnostic_snapshot | businessIdMasked | documental | sí | ver schema correspondiente |
| diagnostic_snapshot | deviceIdMasked | documental | sí | ver schema correspondiente |
| diagnostic_snapshot | sections.version | documental | según caso | ver schema correspondiente |
| diagnostic_snapshot | sections.database | documental | según caso | ver schema correspondiente |
| diagnostic_snapshot | sections.outbox | documental | según caso | ver schema correspondiente |
| message_thread | threadId | documental | sí | ver schema correspondiente |
| message_thread | businessId | documental | sí | ver schema correspondiente |
| message_thread | deviceId | documental | sí | ver schema correspondiente |
| message_thread | surface | documental | sí | ver schema correspondiente |
| message_thread | category | documental | sí | ver schema correspondiente |
| message_thread | status | documental | según caso | ver schema correspondiente |
| message_thread | title | documental | según caso | ver schema correspondiente |
| message_thread | contextRefs | documental | según caso | ver schema correspondiente |
| message | messageId | documental | sí | ver schema correspondiente |
| message | threadId | documental | sí | ver schema correspondiente |
| message | senderType | documental | sí | ver schema correspondiente |
| message | body | documental | sí | ver schema correspondiente |
| message | status | documental | sí | ver schema correspondiente |
| message | attachments | documental | según caso | ver schema correspondiente |
| message | contextRefs | documental | según caso | ver schema correspondiente |
| message | createdAt | documental | según caso | ver schema correspondiente |
| message_outbox | outboxItemId | documental | sí | ver schema correspondiente |
| message_outbox | threadId | documental | sí | ver schema correspondiente |
| message_outbox | messageId | documental | sí | ver schema correspondiente |
| message_outbox | status | documental | sí | ver schema correspondiente |
| message_outbox | createdAt | documental | sí | ver schema correspondiente |
| message_outbox | remoteEnabled | documental | según caso | ver schema correspondiente |
| message_outbox | reason | documental | según caso | ver schema correspondiente |

## Reglas de naming

- IDs internos en inglés estable.
- Labels visibles en español.
- Estados en enum cerrado.
- No usar strings mágicos sin schema.
- No mezclar `mock`, `real`, `read_only` y `disabled` en una misma bandera ambigua.

## Campos que nunca deben aparecer

| Campo/patrón | Motivo |
| --- | --- |
| password | secreto |
| rawToken | secreto |
| DATABASE_URL completa | credencial |
| customerFullDump | datos sensibles |
| rawDbDump | riesgo extremo |
| executeCommand | remote execution no permitido |
| paymentProcessorSecret | No Payment Processing |
