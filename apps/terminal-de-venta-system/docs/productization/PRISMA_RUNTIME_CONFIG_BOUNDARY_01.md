---
title: PRISMA Runtime Config Boundary 01
project: PRISMA Terminal de Venta
package: PRISMA_RUNTIME_CONFIG_BOUNDARY_01
status: productization-contract
visible_language: es-MX
scope: runtime-config-boundary
---

# PRISMA Runtime Config Boundary 01

## 1. Decision madre

PRISMA debe dejar de asumir que el repositorio de desarrollo es el lugar donde vive el producto del cliente.

Esta entrega define la frontera tecnica entre:

```text
dev repo -> release bundle -> customer runtime
```

El objetivo no es reescribir Tablet ni PC. El objetivo es crear el contrato que despues permitira mover datos, configuracion, licencias, logs, backups, updates, plugins, diagnosticos y soporte a rutas de cliente, sin depender de `cwd` ni de `F:\repos\hitech-os`.

## 2. Regla brutalmente simple

```text
El repo produce el producto.
El ZIP entrega el producto.
ProgramData guarda la vida del cliente.
Program Files guarda binarios instalados.
El cwd no manda.
```

Si una venta, backup, licencia o plugin necesita saber desde que carpeta se abrio PowerShell, ese flujo ya nacio chueco, como puesto de tacos con extension electrica mojada.

## 3. Alcance de esta entrega

Esta entrega instala documentacion, schemas, ejemplos, checklists y plan de instalador para la frontera runtime/config.

No modifica runtime real.
No modifica DB.
No cambia rutas Next.
No toca ventas.
No toca PC Backoffice.
No conecta Remote Ops.
No mete pagos bancarios.

## 4. Componentes que quedan definidos

| Componente | Funcion |
|---|---|
| Runtime root | raiz de datos del cliente |
| Config root | configuracion local |
| Business root | datos separados por negocio |
| Tablet data | DB, exports, backups, logs de Tablet |
| PC data | DB, imports, exports, backups, logs de PC |
| Sync root | inbox/outbox/conflicts/archive |
| Local Agent root | estado de licencias, updates, mensajes y health |
| Support root | bundles y diagnosticos |
| Updates root | downloads, staged, applied |
| Rollback root | snapshots, manifests, restore points |

## 5. Ruta cliente recomendada

```text
C:\ProgramData\PRISMA\
  config\
  businesses\
    <businessId>\
      tablet\
      pc\
      sync\
      shared\
      support\
  updates\
  rollback\
  logs\
```

## 6. Ruta de binarios recomendada

```text
C:\Program Files\PRISMA\
  tablet\
  pc\
  local-agent\
```

## 7. Ruta de preferencias por usuario

```text
%LOCALAPPDATA%\PRISMA\
```

Debe usarse solo para preferencias por usuario, cache no critica o estado visual. No para ventas, DB, licencias ni backups principales.

## 8. Modos runtime

| Modo | Descripcion | Internet requerido | PC requerido |
|---|---|---:|---:|
| dev | usa repo y fixtures controlados | no | no |
| standalone | Tablet vende sola | no | no |
| pro | Tablet con operacion avanzada | no permanente | no |
| pc_backoffice | PC gobierna inventario/backoffice | no permanente | si para backoffice |
| managed | Tablet + PC administrados | intermitente | si para gobierno |
| degraded_managed | cae red/PC pero Tablet sigue vendiendo | no para venta local | no para venta local |

## 9. Variables permitidas

Las variables de entorno pueden existir, pero no deben ser el unico contrato. Deben resolver hacia config explicita.

Ejemplos permitidos:

```text
PRISMA_RUNTIME_ROOT
PRISMA_CONFIG_ROOT
PRISMA_BUSINESS_ID
PRISMA_DEVICE_ID
PRISMA_RUNTIME_MODE
PRISMA_LICENSE_FILE
PRISMA_TABLET_DATABASE_URL
PRISMA_PC_DATABASE_URL
```

## 10. Anti reglas

Queda prohibido para runtime cliente:

- escribir DB en el repo;
- guardar secretos en archivos commiteados;
- depender del directorio actual;
- asumir `F:\repos\hitech-os`;
- empaquetar `.next`, `node_modules`, logs, DB dev, backups o temporales;
- mezclar datos de negocios distintos en la misma carpeta;
- bloquear venta local por falla de Remote Ops.

## 11. Siguiente paso tecnico

Despues de esta entrega, la siguiente implementacion debe ser una capa no invasiva que pueda resolver rutas runtime desde config, con modo dev y modo customer, sin cambiar comportamiento de venta.
