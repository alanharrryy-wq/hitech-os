# PRISMA Customer Messaging Mock 05 — Acceptance Matrix


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


| Área | Acepta si | Bloquea si |
| --- | --- | --- |
| thread contract | campos requeridos definidos | thread sin status/category |
| message contract | sender/body/status definidos | mensaje sin sender/status |
| mock boundary | sin servidor real | promete envío remoto |
| attachments | solo refs controladas | archivo libre |
| storage | fuera del repo en customer mode | datos vivos en repo |
| Tablet UX | ligera y no bloqueante | bandeja pesada |
| Support relation | referencia 04 | diagnóstico crudo en mensaje |
| No secrets | body sin secretos | token/API key en body |
