# PRISMA Centro PRISMA UI Shell 03 — Navigation and Permissions


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


## Permisos mínimos

| Permiso | Superficie | Uso | Plan inicial |
| --- | --- | --- | --- |
| center.view | pc | Ver Centro PRISMA | PC_BACKOFFICE / MANAGED |
| license.view | pc | Ver Mi Plan | PC_BACKOFFICE / MANAGED |
| plugins.view | pc | Ver plugins declarativos | PC_BACKOFFICE / MANAGED |
| support.view | pc | Ver soporte | todo plan con PC |
| messages.view | pc | Ver mensajes mock | todo plan con PC |
| announcements.view | pc | Ver novedades | todo plan con PC |
| diagnostics.view | pc | Ver diagnóstico | Pro/PC |
| updates.view | pc | Ver estado updates | PC |
| tablet.status.view | tablet | Ver estado local | TABLET_SOLO+ |
| tablet.support.view | tablet | Ver soporte ligero | TABLET_SOLO+ |
| tablet.messages.view | tablet | Ver mensajes ligeros | TABLET_SOLO+ |
| tablet.announcements.view | tablet | Ver novedades ligeras | TABLET_SOLO+ |

## Política de visibilidad

| Caso | Qué mostrar | Qué no mostrar |
| --- | --- | --- |
| sin permiso | módulo oculto o bloqueado | datos parciales sensibles |
| plan limitado | explicación de plan | mensaje de castigo |
| Tablet solo | estado/soporte/mensajes/novedades | plugins/update/apply |
| PC backoffice | módulos completos read-only/mock | acciones destructivas |
| offline | estado local | sync remoto inmediato |

## Orden de navegación PC

1. Centro PRISMA.
2. Mi Plan.
3. Soporte.
4. Mensajes.
5. Novedades.
6. Diagnóstico.
7. Plugins.
8. Actualizaciones.

## Orden de navegación Tablet

1. Estado.
2. Soporte.
3. Mensajes.
4. Novedades.

## Criterio de rechazo

Se rechaza una implementación si un usuario sin permiso puede ver datos sensibles o si un usuario con plan limitado recibe mensaje que parezca que PRISMA le secuestra su operación. La licencia limita features; no se comporta como cobrador de combi.
