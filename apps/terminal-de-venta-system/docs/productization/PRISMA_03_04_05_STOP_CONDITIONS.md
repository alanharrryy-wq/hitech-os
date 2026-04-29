# PRISMA 03-04-05 — Stop Conditions


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


| Área | Se detiene si |
| --- | --- |
| ZIP | contiene .env, DB, .next, node_modules, ejecutables inesperados o rutas absolutas |
| Docs | contradice 00, 01 o 02 |
| Centro UI | acción real sin backend/permiso/auditoría |
| Tablet | flujo bloquea venta local |
| Soporte | dato fuera de allowlist |
| Diagnóstico | bundle sin consentimiento |
| Mensajes | envío remoto en 05 |
| Plugins | ejecución de código en 03 |
| Updates | descarga/aplica update antes de 08 |
| Pagos | procesamiento bancario |

## Decisión

Si aparece una stop condition, se bloquea el paquete y se regenera. Nada de “así déjalo y luego vemos”, esa es la oración oficial de la deuda técnica con sombrero.
