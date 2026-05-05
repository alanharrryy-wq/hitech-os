---
title: PRISMA Local Agent Contract
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Local Agent Contract

## Decisión

El Local Agent es el puente local entre runtime cliente y Remote Ops. Puede iniciar como módulo interno y luego separarse como producto instalable.

## Responsabilidades

- refrescar licencia;
- cachear entitlements;
- consultar updates;
- stagear paquetes;
- aplicar updates aprobados;
- instalar/desactivar plugins;
- generar diagnostics;
- sincronizar mensajes;
- obtener announcements;
- enviar heartbeat;
- ejecutar comandos allowlist.

## No responsabilidades

- no cerrar ventas;
- no calcular totales;
- no descontar stock;
- no procesar pagos;
- no editar DB a mano;
- no ejecutar PowerShell arbitrario;
- no abrir puertos entrantes por defecto.

## Heartbeat mínimo

```json
{
  "deviceId": "dev_001",
  "businessId": "biz_001",
  "app": "local_agent",
  "version": "0.0.1",
  "licenseStatus": "active",
  "syncStatus": "ok",
  "pendingOutboxCount": 0,
  "lastBackupAt": "2026-04-28T12:00:00Z",
  "diskFreeMb": 20480,
  "plugins": [],
  "errorsLast24h": 0
}
```

## Command loop

```text
poll remote ops
validate response signature
filter expired commands
validate commandType allowlist
check local preconditions
execute safe handler
write audit log
return result
```

## Estados locales

```text
healthy
warning
degraded
offline
needs_attention
update_pending
rollback_available
```

## Seguridad

1. Firma de comandos.
2. Firma/checksum de paquetes.
3. Allowlist cerrada.
4. Logs saneados.
5. Nunca ejecutar shell libre.
6. Nunca enviar secretos.
7. Consentimiento para diagnostics.

## Ubicación futura

```text
products/local-agent
```

Antes de eso puede vivir en:

```text
tooling/local-agent
```

## Criterio de aceptación

El agente está bien diseñado si permite soporte y updates sin convertirse en dueño de la caja. Es mayordomo técnico, no patrón del changarro.
