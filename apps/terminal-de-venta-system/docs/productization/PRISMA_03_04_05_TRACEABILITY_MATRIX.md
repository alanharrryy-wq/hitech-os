# PRISMA 03-04-05 — Traceability Matrix


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


| ID | Elemento | Permiso | Modo | Paquete | Fuente |
| --- | --- | --- | --- | --- | --- |
| pc.center.home | Centro PRISMA | center.view | mock_local | 03 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| pc.center.license | Mi Plan | license.view | mock_local | 02 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| pc.center.plugins | Plugins | plugins.view | read_only | 07 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| pc.center.support | Soporte | support.view | mock_local | 04/05 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| pc.center.messages | Mensajes | messages.view | mock_local | 05 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| pc.center.announcements | Novedades | announcements.view | mock_local | 06 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| pc.center.diagnostics | Diagnóstico | diagnostics.view | read_only | 04 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| pc.center.updates | Actualizaciones | updates.view | read_only | 08 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| tablet.center.status | Estado | tablet.status.view | read_only | 03 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| tablet.center.support | Soporte | tablet.support.view | mock_local | 04 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| tablet.center.messages | Mensajes | tablet.messages.view | mock_local | 05 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| tablet.center.announcements | Novedades | tablet.announcements.view | mock_local | 06 | PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md |
| support.allowlist | allowlist | support.view/diagnostics.view | read_only | 04 | PRISMA_SUPPORT_BUNDLE_LOCAL_04_MASTER_SPEC.md |
| support.secret_redaction | secret_redaction | support.view/diagnostics.view | read_only | 04 | PRISMA_SUPPORT_BUNDLE_LOCAL_04_MASTER_SPEC.md |
| support.diagnostic_fields | diagnostic_fields | support.view/diagnostics.view | read_only | 04 | PRISMA_SUPPORT_BUNDLE_LOCAL_04_MASTER_SPEC.md |
| support.support_bundle_manifest | support_bundle_manifest | support.view/diagnostics.view | read_only | 04 | PRISMA_SUPPORT_BUNDLE_LOCAL_04_MASTER_SPEC.md |
| support.consent_state | consent_state | support.view/diagnostics.view | read_only | 04 | PRISMA_SUPPORT_BUNDLE_LOCAL_04_MASTER_SPEC.md |
| messaging.thread | thread | messages.view/tablet.messages.view | mock_local | 05 | PRISMA_CUSTOMER_MESSAGING_MOCK_05_MASTER_SPEC.md |
| messaging.message | message | messages.view/tablet.messages.view | mock_local | 05 | PRISMA_CUSTOMER_MESSAGING_MOCK_05_MASTER_SPEC.md |
| messaging.local_outbox | local_outbox | messages.view/tablet.messages.view | mock_local | 05 | PRISMA_CUSTOMER_MESSAGING_MOCK_05_MASTER_SPEC.md |
| messaging.attachment_refs | attachment_refs | messages.view/tablet.messages.view | mock_local | 05 | PRISMA_CUSTOMER_MESSAGING_MOCK_05_MASTER_SPEC.md |
| messaging.storage_policy | storage_policy | messages.view/tablet.messages.view | mock_local | 05 | PRISMA_CUSTOMER_MESSAGING_MOCK_05_MASTER_SPEC.md |

## Uso

Esta matriz permite que un implementador encuentre rápido qué documento manda para cada elemento. Si algo no aparece aquí, no se implementa por ocurrencia. Así evitamos el deporte nacional de “lo metí porque se veía fácil”.
