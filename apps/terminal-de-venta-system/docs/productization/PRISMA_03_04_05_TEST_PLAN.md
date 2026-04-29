# PRISMA 03-04-05 — Test Plan Documental


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


## ZIP tests

| Test | Esperado |
| --- | --- |
| entries under payload | todas las entradas bajo payload/ |
| json parse | todos los JSON válidos |
| forbidden files | sin .env/.db/.next/node_modules |
| path traversal | sin .. ni rutas absolutas |
| manifest | lista archivos reales |
| checksums | externos al manifest |

## 03 tests

| Test | Esperado |
| --- | --- |
| PC route count | 8 rutas |
| Tablet route count | 4 rutas |
| route schema | surface/path/title/permission/initialMode |
| module cards | allowed/prohibited actions |
| permissions | todos los permisos mapeados |

## 04 tests

| Test | Esperado |
| --- | --- |
| bundle manifest | bundleId/createdAt/schemaVersion |
| diagnostic snapshot | version/runtime/database/outbox/plugins |
| redaction rules | denylist mínima |
| allowlist | logs, DB, runtime, plugins |

## 05 tests

| Test | Esperado |
| --- | --- |
| thread schema | category/status/surface requeridos |
| message schema | senderType/status/body requeridos |
| outbox mock | remoteEnabled=false |
| examples | status local_only/blocked_no_server |
