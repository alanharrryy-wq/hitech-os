# PRISMA 03-04-05 — Rollout Plan


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


## Fase documental actual

| Paso | Acción | Resultado |
| --- | --- | --- |
| 1 | instalar docs 03-04-05 | contratos disponibles |
| 2 | validar schemas | JSON parsean |
| 3 | verificar manifest/checksums | integridad documental |
| 4 | preparar implementación futura | agente sabe rutas y límites |

## Fase implementación posterior sugerida

| Orden | Paquete técnico futuro | Implementa | No implementa |
| --- | --- | --- | --- |
| 03A | PC shell routes mock | rutas y pantallas PC | soporte real |
| 03B | Tablet shell light | pantallas ligeras | backoffice pesado |
| 04A | diagnostic snapshot dry-run | snapshot redactado | upload remoto |
| 04B | support bundle writer | bundle local manifestado | envío remoto |
| 05A | local messaging fixtures | threads/messages mock | servidor |
| 05B | local outbox mock | cola local mock | bridge remoto |

## Regla de aceleración

Se pueden agrupar documentos. No se deben agrupar side effects. Esa diferencia es la que separa ingeniería de “a ver si prende”.
