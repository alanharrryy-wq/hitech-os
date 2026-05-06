# PRISMA Support Bundle Local 04 — Diagnostic Fields


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


## Snapshot raíz

| Campo | Tipo | Requerido | Descripción |
| --- | --- | --- | --- |
| snapshotId | string | sí | ID del snapshot |
| schemaVersion | string | sí | versión de contrato |
| createdAt | date-time | sí | fecha de generación |
| runtimeMode | string | sí | modo runtime |
| surface | pc/tablet/both | sí | superficie |
| businessIdMasked | string | sí | negocio enmascarado |
| deviceIdMasked | string | sí | dispositivo enmascarado |
| sections | object | sí | secciones incluidas |

## Runtime paths

| Campo | Regla |
| --- | --- |
| runtimeRoot | normalizado |
| logsRoot | escribible |
| backupRoot | escribible |
| dbPath | ruta permitida, no contenido |
| repoRootDetected | boolean para detectar customer data en repo |

## Database

| Campo | Permitido |
| --- | --- |
| exists | sí |
| sizeBytes | sí |
| lastModifiedAt | sí |
| integrityStatus | unknown/ok/warn/error |
| tablesCount | opcional si lectura segura |

## Outbox

| Campo | Descripción |
| --- | --- |
| pending | eventos pendientes |
| sent | eventos enviados |
| failed | eventos fallidos |
| acked | eventos confirmados |
| conflict | eventos en conflicto |

## Plugins

| Campo | Descripción |
| --- | --- |
| pluginId | ID declarativo |
| version | versión |
| status | active/inactive/blocked/mock |
| manifestHash | hash del manifest |
