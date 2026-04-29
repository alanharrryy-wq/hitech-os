# PRISMA Customer Messaging Mock 05 — Local Storage Policy


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


## Relación con Runtime 01

En customer mode, mensajes locales no deben vivir en el repo. Deben vivir bajo runtime root del cliente cuando exista implementación.

## Ubicaciones conceptuales

```text
C:\ProgramData\PRISMA\businesses\<businessId>\shared\messages\
C:\ProgramData\PRISMA\businesses\<businessId>\tablet\messages\
C:\ProgramData\PRISMA\businesses\<businessId>\pc\messages\
```

## Archivos conceptuales

| Archivo | Uso |
| --- | --- |
| threads.jsonl | threads locales append-friendly |
| messages.jsonl | mensajes locales append-friendly |
| outbox-mock.jsonl | cola mock futura |
| indexes.json | índices reconstruibles |

## Reglas

1. No guardar en repo en customer mode.
2. No guardar adjuntos crudos.
3. No guardar secretos.
4. Separar fixtures de datos vivos.
5. Permitir export diagnóstico solo bajo allowlist 04.
6. Mantener límite de longitud.
7. Categorías cerradas.
