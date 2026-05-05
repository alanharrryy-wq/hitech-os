---
title: PRISMA Rollout and Support Playbook
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Rollout and Support Playbook

## Objetivo

Definir cómo se despliega Customer Operations sin romper operación.

## Antes de activar

- verificar backup,
- verificar licencia local,
- verificar runtime root,
- verificar que Tablet cierre venta sin PC,
- verificar que PC abra dashboard,
- verificar exports,
- verificar logs.

## Piloto

Usar canal:

```text
pilot
```

Solo con clientes controlados.

## Stable

Pasar a stable cuando:

- no rompe venta,
- no rompe export,
- no rompe backup,
- diagnostics genera bundle saneado,
- rollback probado,
- licencia offline grace probado.

## Soporte nivel 1

- revisar Centro PRISMA,
- pedir diagnóstico basic,
- revisar versión,
- revisar licencia,
- revisar estado outbox.

## Soporte nivel 2

- diagnóstico standard,
- revisar logs saneados,
- revisar plugins,
- reintentar sync,
- refrescar licencia.

## Soporte nivel 3

- diagnóstico deep,
- hotfix firmado,
- rollback,
- intervención guiada.

## Nunca hacer

- pedir al cliente borrar DB,
- pedir ejecutar comandos raros sin respaldo,
- modificar archivos a mano sin manifest,
- mandar ZIP informal,
- instalar plugin sin verify,
- procesar pagos dentro de PRISMA.

## Plantilla de respuesta técnica

```text
Resumen:
Impacto:
Acción aplicada:
Validación:
Rollback disponible:
Siguiente revisión:
```

## Criterio de aceptación

Un rollout está bien si el cliente puede seguir vendiendo y soporte puede explicar qué pasó sin sacar el rosario del cajón.
