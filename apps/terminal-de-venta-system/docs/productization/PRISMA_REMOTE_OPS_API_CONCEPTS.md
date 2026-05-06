---
title: PRISMA Remote Ops API Concepts
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---

# PRISMA Remote Ops API Concepts

## Endpoint conceptual: /api/devices/register

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/devices/heartbeat

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/licenses/refresh

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/announcements/list

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/messages/list

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/messages/send

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/support/tickets/create

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/support/tickets/update

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/diagnostics/upload

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/releases/check

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/plugins/catalog

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/plugins/request-activation

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/commands/poll

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/commands/report

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

## Endpoint conceptual: /api/audit/append

Estado: contrato conceptual, no implementación.

Objetivo: permitir comunicación segura entre Local Agent, Tablet/PC y Remote Ops sin abrir puertos entrantes en el negocio del cliente.

Request mínimo:

```json
{
  "businessId": "biz_demo_store",
  "deviceId": "dev_demo_01",
  "schemaVersion": "1.0.0",
  "requestedAt": "2026-04-28T12:00:00Z"
}
```

Response mínimo:

```json
{
  "ok": true,
  "data": {},
  "meta": {
    "requestId": "req_demo",
    "schemaVersion": "1.0.0"
  }
}
```

Errores esperados:

```text
UNAUTHORIZED_DEVICE
LICENSE_NOT_FOUND
SCHEMA_VERSION_UNSUPPORTED
SIGNATURE_INVALID
COMMAND_NOT_ALLOWED
RATE_LIMITED
REMOTE_UNAVAILABLE
```

Reglas:

- No enviar secretos.
- No enviar DB completa.
- No procesar pagos.
- No depender de esta llamada para cerrar venta local.
- Registrar errores localmente de forma saneada.
- Si hay caída remota, usar cache local y grace donde aplique.

