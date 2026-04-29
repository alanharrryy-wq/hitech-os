# PRISMA 03-04-05 — Implementation Handoff


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


## Para Codex/agente implementador futuro

No empieces creando pantallas. Primero lee:

1. `PRISMA_03_04_05_INDEX.md`
2. `PRISMA_CENTRO_PRISMA_UI_SHELL_03_ROUTE_CONTRACT.md`
3. `PRISMA_CENTRO_PRISMA_UI_SHELL_03_EMPTY_STATES_AND_MOCK_POLICY.md`
4. `PRISMA_SUPPORT_BUNDLE_LOCAL_04_DATA_ALLOWLIST.md`
5. `PRISMA_CUSTOMER_MESSAGING_MOCK_05_THREAD_CONTRACT.md`
6. `PRISMA_03_04_05_STOP_CONDITIONS.md`

## Implementación futura permitida

| Fase | Permitido | Prohibido |
| --- | --- | --- |
| 03A | rutas PC mock/read-only | soporte real, update real, plugin execution |
| 03B | rutas Tablet ligeras | backoffice pesado |
| 04A | diagnostic dry-run redactado | upload remoto |
| 04B | bundle local manifestado | DB dump |
| 05A | fixtures de threads/messages | envío remoto |
| 05B | outbox mock local | bridge real |

## Validaciones antes de tocar código

- Confirmar que la ruta está en el route contract.
- Confirmar permiso.
- Confirmar modo inicial.
- Confirmar estado vacío.
- Confirmar paquete relacionado.
- Confirmar que no rompe Tablet standalone.
- Confirmar que no toca pagos.
- Confirmar que no abre comunicación remota.

## Frase guía

Centro PRISMA debe parecer producto serio, no tablero de botones falsos. Si una acción no existe, se explica. Si requiere paquete futuro, se declara. Si es sensible, se pide permiso o consentimiento. Si toca dinero, datos o runtime, no se improvisa.
