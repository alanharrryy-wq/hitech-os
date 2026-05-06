---
title: PRISMA Centro PRISMA UI Contract
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Centro PRISMA UI Contract

## Decisión

Centro PRISMA es la superficie visible para cliente dentro de Tablet y PC. Ahí viven plan, licencia, soporte, mensajes, novedades, actualizaciones, diagnósticos y plugins.

## PC Backoffice

PC tendrá la versión completa:

```text
/centro-prisma
/centro-prisma/licencia
/centro-prisma/mi-plan
/centro-prisma/plugins
/centro-prisma/soporte
/centro-prisma/mensajes
/centro-prisma/novedades
/centro-prisma/actualizaciones
/centro-prisma/diagnostico
/centro-prisma/dispositivos
```

## Tablet

Tablet tendrá versión ligera:

```text
/centro-prisma
/centro-prisma/estado
/centro-prisma/soporte
/centro-prisma/mensajes
/centro-prisma/novedades
/centro-prisma/diagnostico
```

## Regla Tablet

Tablet no debe interrumpir venta por mensajes comerciales. La caja vende; no es cartelera de cine.

## Roles

```text
cashier
supervisor
owner
technician
provider_support
```

## Visibilidad por rol

| Sección | Cajero | Supervisor | Dueño | Técnico |
|---|---:|---:|---:|---:|
| Estado | sí | sí | sí | sí |
| Soporte | básico | sí | sí | sí |
| Mensajes | limitado | sí | sí | sí |
| Novedades | limitado | sí | sí | sí |
| Licencia | no | parcial | sí | sí |
| Plugins | no | parcial | sí | sí |
| Diagnóstico | no | parcial | sí | sí |
| Updates | no | parcial | sí | sí |

## Estados UI

```text
idle
loading
ready
empty
error
offline
sync_pending
success
blocked_by_role
blocked_by_plan
```

## CTA permitidos

```text
solicitar_soporte
generar_diagnostico
solicitar_activacion
ver_novedades
ver_estado
actualizar_licencia
```

No CTA de pago interno.

## Criterio de aceptación

Centro PRISMA está bien si el dueño entiende el estado del producto sin abrir PowerShell, y el cajero puede seguir cobrando sin que le brinque un popup como vendedor de seguros en semáforo.
