---
title: PRISMA Customer Messaging Contract
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Customer Messaging Contract

## 1. Decisión

PRISMA debe incluir un canal de comunicación entre el cliente y el proveedor dentro de Tablet y PC.

Este canal sirve para soporte, avisos, solicitudes de activación, capacitación, dudas operativas, respuestas técnicas y futura asistencia con IA.

## 2. Canales

| Canal | Uso |
|---|---|
| support | soporte técnico |
| license | dudas de licencia |
| plugin_request | solicitud de plugin o feature |
| training | capacitación |
| bug_report | reporte de falla |
| admin | comunicación administrativa no bancaria |
| ai_support_future | canal preparado para IA futura |

## 3. Reglas

1. Mensajes deben ser estructurados.
2. Adjuntos deben ser permitidos por tipo.
3. Diagnósticos se adjuntan solo con consentimiento.
4. Tablet no debe interrumpir checkout por mensajes normales.
5. PC puede mostrar centro completo de mensajes.
6. Todo thread debe tener estado.

## 4. Estados de thread

```text
open
waiting_customer
waiting_provider
resolved
closed
archived
```

## 5. Prioridades

```text
low
normal
high
urgent
```

## 6. Modelo mínimo

```json
{
  "threadId": "thr_123",
  "businessId": "biz_abc",
  "deviceId": "dev_tablet_01",
  "category": "support",
  "status": "open",
  "priority": "normal",
  "subject": "No puedo exportar ventas",
  "createdAt": "2026-04-28T12:00:00Z"
}
```

## 7. Mensaje mínimo

```json
{
  "messageId": "msg_123",
  "threadId": "thr_123",
  "senderType": "customer",
  "senderRole": "owner",
  "body": "No puedo exportar ventas del día.",
  "attachments": [],
  "contextRefs": [],
  "createdAt": "2026-04-28T12:01:00Z"
}
```

## 8. Futuro IA

La IA no reemplaza este contrato. La IA se monta encima de threads, mensajes, diagnósticos y contexto autorizado.

Primer modo permitido:

```text
read-only
```

Segundo modo futuro:

```text
suggest-actions
```

Modo peligroso que requiere gobierno adicional:

```text
execute-approved-actions
```

## 9. No debe hacer

- No usar chat para pagos bancarios integrados.
- No mandar secretos.
- No adjuntar DB completa sin permiso explícito.
- No ejecutar comandos desde mensajes.
- No permitir adjuntos arbitrarios peligrosos.
