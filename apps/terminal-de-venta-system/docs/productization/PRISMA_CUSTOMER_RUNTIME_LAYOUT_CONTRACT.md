---
title: PRISMA Customer Runtime Layout Contract
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Customer Runtime Layout Contract

## 1. Decision

Los datos del cliente viven por negocio y por superficie operativa.

```text
C:\ProgramData\PRISMA\businesses\<businessId>\
```

Este layout permite separar una demo, una tienda real, una sucursal futura y un ambiente de soporte sin revolver datos como cubeta de tornillos.

## 2. Layout base

```text
C:\ProgramData\PRISMA\
  config\
    runtime.json
    license.json
    devices.json
    paths.json
    sync.json

  businesses\
    <businessId>\
      business.json
      tablet\
        data\
        outbox\
        exports\
        backups\
        logs\
        diagnostics\
      pc\
        data\
        imports\
        exports\
        backups\
        logs\
        diagnostics\
      sync\
        inbox\
        outbox\
        conflicts\
        archive\
      shared\
        snapshots\
        contracts\
        audit\
      support\
        bundles\

  updates\
    downloads\
    staged\
    applied\

  rollback\
    snapshots\
    manifests\

  logs\
    install\
    agent\
```

## 3. Responsabilidad por carpeta

| Carpeta | Responsable | Contenido |
|---|---|---|
| config | installer/local-agent | configuracion global |
| tablet/data | Tablet | SQLite Tablet |
| tablet/outbox | Tablet | eventos pendientes |
| pc/data | PC | DB backoffice |
| pc/imports | PC | entradas controladas |
| sync | Local Agent/PC | intercambio y conflictos |
| support/bundles | soporte | diagnosticos exportables |
| updates | installer/agent | paquetes versionados |
| rollback | installer/agent | snapshots de reversa |

## 4. Reglas de separacion

- Un `businessId` nunca comparte DB con otro.
- Un plugin no escribe fuera de su superficie permitida.
- Logs no son fuente de verdad.
- Exports no son backups.
- Backups no reemplazan migraciones.
- Support bundles no deben incluir secretos.

## 5. Validacion de instalador

El instalador debe crear las carpetas necesarias antes de primera ejecucion. Si no puede, debe fallar con mensaje claro y no dejar instalacion a medias.
