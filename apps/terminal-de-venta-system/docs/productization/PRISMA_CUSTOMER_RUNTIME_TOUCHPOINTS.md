---
title: PRISMA Customer Runtime Touchpoints
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Customer Runtime Touchpoints

## Decisión

Desde la perspectiva del cliente, Customer Operations aparece en puntos claros y no invasivos.

## Tablet

Touchpoints:

- badge de estado,
- Centro PRISMA ligero,
- soporte rápido,
- diagnóstico básico,
- novedades no invasivas,
- aviso de licencia por vencer,
- aviso de sync pendiente.

Tablet no debe mostrar anuncios comerciales durante venta.

## PC

Touchpoints:

- Centro PRISMA completo,
- dashboard de dispositivos,
- licencia y plan,
- plugins,
- soporte,
- mensajes,
- novedades,
- updates,
- diagnósticos.

## Local Agent

Touchpoints indirectos:

- tray app futura,
- servicio local,
- logs,
- health,
- estado update,
- estado licencia.

## Eventos visibles al cliente

```text
license.expiring
license.offline_grace
support.reply_received
plugin.available
plugin.enabled
update.available
update.applied
backup.failed
sync.pending
sync.failed
```

## Mensajes que no deben aparecer al cajero

- ventas comerciales de plugins,
- detalles de licencia vencida,
- migraciones técnicas,
- errores internos largos,
- stack traces,
- promesas de IA mágica.

## Mensajes para dueño/admin

- plan,
- features,
- licencia,
- actualizaciones,
- nuevas funciones,
- soporte,
- diagnósticos,
- health de dispositivos.

## Criterio de aceptación

El cliente entiende qué pasa, el cajero vende rápido y el dueño tiene control. Tres cosas juntas, milagro raro en software, pero se intenta.
