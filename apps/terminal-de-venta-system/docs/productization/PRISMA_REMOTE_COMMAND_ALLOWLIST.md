---
title: PRISMA Remote Command Allowlist
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Remote Command Allowlist

## Decisión

Remote Ops solo puede solicitar acciones predefinidas. No puede ejecutar comandos libres.

## Permitidos

| Comando | Descripción | Requiere consentimiento |
|---|---|---:|
| CHECK_HEALTH | revisar estado técnico | no |
| GENERATE_DIAGNOSTIC_BUNDLE | generar diagnóstico | sí |
| REFRESH_LICENSE | refrescar licencia | no |
| CHECK_FOR_UPDATES | buscar updates | no |
| STAGE_UPDATE | preparar update | sí si pesa o impacta |
| APPLY_APPROVED_UPDATE | aplicar update aprobado | sí |
| DISABLE_PLUGIN | desactivar plugin | sí |
| ENABLE_PLUGIN | activar plugin autorizado | sí |
| RETRY_SYNC | reintentar sync | no/parcial |

## Prohibidos

```text
RUN_ARBITRARY_COMMAND
EXECUTE_POWERSHELL
DELETE_DATABASE
EDIT_FILE_RAW
UPLOAD_FULL_DATABASE_WITHOUT_CONSENT
OPEN_INBOUND_PORT
INSTALL_UNSIGNED_PLUGIN
APPLY_UNSIGNED_UPDATE
```

## Estados

```text
queued
received
validated
rejected
running
succeeded
failed
expired
cancelled
```

## Validación

Cada comando debe validar:

- firma,
- businessId,
- deviceId,
- expiración,
- commandType,
- precondiciones,
- permisos del actor,
- estado local.

## Resultado

```json
{
  "commandId": "cmd_001",
  "status": "succeeded",
  "startedAt": "2026-04-28T12:00:00Z",
  "finishedAt": "2026-04-28T12:00:03Z",
  "summary": "Health OK",
  "errorCode": null
}
```

## Criterio de aceptación

Si alguien pide ejecutar algo fuera de allowlist, el sistema debe decir que no. Sin dramas, sin negociación, sin “pero tantito”.
