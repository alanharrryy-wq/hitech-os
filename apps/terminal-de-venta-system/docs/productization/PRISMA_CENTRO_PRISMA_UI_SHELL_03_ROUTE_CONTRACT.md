# PRISMA Centro PRISMA UI Shell 03 — Route Contract


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


## Convención

Las rutas son lógicas. No crean archivos `page.tsx`. Una implementación posterior puede mapearlas a Next.js, tabs internas o navegación mobile, pero no puede cambiar intención ni permisos.

## Contrato de ruta

| Campo | Tipo | Requerido | Regla |
| --- | --- | --- | --- |
| routeId | string | sí | estable, único, sin espacios |
| surface | pc/tablet | sí | define responsabilidad |
| pathKey | string | sí | ruta lógica visible |
| title | string | sí | es-MX |
| permission | string | sí | permiso mínimo |
| initialMode | enum | sí | mock_local/read_only/disabled_until_package/blocked_by_plan |
| blocksCheckout | boolean | sí | Tablet debe ser false |
| relatedPackage | string | no | paquete que habilita capacidad futura |

## Rutas PC autorizadas

| routeId | pathKey | Título | Permiso | Modo | Paquete |
| --- | --- | --- | --- | --- | --- |
| pc.center.home | centro-prisma | Centro PRISMA | center.view | mock_local | 03 |
| pc.center.license | centro-prisma/licencia | Mi Plan | license.view | mock_local | 02 |
| pc.center.plugins | centro-prisma/plugins | Plugins | plugins.view | read_only | 07 |
| pc.center.support | centro-prisma/soporte | Soporte | support.view | mock_local | 04/05 |
| pc.center.messages | centro-prisma/mensajes | Mensajes | messages.view | mock_local | 05 |
| pc.center.announcements | centro-prisma/novedades | Novedades | announcements.view | mock_local | 06 |
| pc.center.diagnostics | centro-prisma/diagnostico | Diagnóstico | diagnostics.view | read_only | 04 |
| pc.center.updates | centro-prisma/actualizaciones | Actualizaciones | updates.view | read_only | 08 |

## Rutas Tablet autorizadas

| routeId | pathKey | Título | Permiso | Modo | Paquete |
| --- | --- | --- | --- | --- | --- |
| tablet.center.status | estado | Estado | tablet.status.view | read_only | 03 |
| tablet.center.support | soporte | Soporte | tablet.support.view | mock_local | 04 |
| tablet.center.messages | mensajes | Mensajes | tablet.messages.view | mock_local | 05 |
| tablet.center.announcements | novedades | Novedades | tablet.announcements.view | mock_local | 06 |

## Reglas

- No crear alias no documentados.
- No duplicar `soporte` como `ayuda`, `help`, `tickets` y `support` a la vez.
- No usar inglés visible salvo término técnico inevitable.
- No usar `admin` en Tablet.
- No exponer rutas internas de runtime.
- No poner `actualizar-ahora` antes del paquete 08.

## Stop conditions

| Condición | Por qué bloquea |
| --- | --- |
| Tablet route con blocksCheckout=true | rompe regla madre de Tablet |
| Ruta sin permiso | rompe gobierno operativo |
| Ruta con initialMode real/actionable | promete implementación que no existe |
| Ruta de pagos bancarios | viola No Payment Processing |
| Ruta de plugin execution | se adelanta al paquete 07 y rompe seguridad |
