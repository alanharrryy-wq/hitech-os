---
title: PRISMA Customer Operations Data Dictionary
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---

# PRISMA Customer Operations Data Dictionary

## Customer

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
customer.created
customer.updated
customer.disabled
customer.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## Business

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
business.created
business.updated
business.disabled
business.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## Location

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
location.created
location.updated
location.disabled
location.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## Device

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
device.created
device.updated
device.disabled
device.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## License

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
license.created
license.updated
license.disabled
license.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## Entitlement

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
entitlement.created
entitlement.updated
entitlement.disabled
entitlement.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## Plan

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
plan.created
plan.updated
plan.disabled
plan.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## Plugin

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
plugin.created
plugin.updated
plugin.disabled
plugin.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## Release

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
release.created
release.updated
release.disabled
release.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## Announcement

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
announcement.created
announcement.updated
announcement.disabled
announcement.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## MessageThread

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
messagethread.created
messagethread.updated
messagethread.disabled
messagethread.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## SupportTicket

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
supportticket.created
supportticket.updated
supportticket.disabled
supportticket.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## DiagnosticBundle

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
diagnosticbundle.created
diagnosticbundle.updated
diagnosticbundle.disabled
diagnosticbundle.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## RemoteCommand

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
remotecommand.created
remotecommand.updated
remotecommand.disabled
remotecommand.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## AuditLog

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
auditlog.created
auditlog.updated
auditlog.disabled
auditlog.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## LocalAgentState

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
localagentstate.created
localagentstate.updated
localagentstate.disabled
localagentstate.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## FeatureFlag

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
featureflag.created
featureflag.updated
featureflag.disabled
featureflag.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## SupportAttachment

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
supportattachment.created
supportattachment.updated
supportattachment.disabled
supportattachment.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## HealthSnapshot

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
healthsnapshot.created
healthsnapshot.updated
healthsnapshot.disabled
healthsnapshot.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

## UpdateAttempt

Propósito: entidad base de Customer Operations Layer para que Remote Ops, Centro PRISMA y Local Agent hablen el mismo idioma.

Campos comunes sugeridos:

| Campo | Tipo | Regla |
|---|---|---|
| id | string | identificador estable, no derivado de nombre visible |
| businessId | string | requerido cuando aplica a cliente runtime |
| status | string | estado explícito, nunca inferido por ausencia |
| createdAt | datetime | ISO-8601 |
| updatedAt | datetime/null | ISO-8601 o null |
| schemaVersion | string | versión de contrato |

Eventos sugeridos:

```text
updateattempt.created
updateattempt.updated
updateattempt.disabled
updateattempt.verified
```

Reglas:

- No guardar secretos en campos libres.
- No usar nombres visibles como IDs.
- No depender de internet para leer último estado local.
- No usar esta entidad para procesar pagos bancarios.
- Cambios sensibles deben generar auditoría.
- Si afecta licencia, plugin, update, soporte o diagnóstico, debe ser verificable.

Errores comunes:

| Error | Consecuencia |
|---|---|
| usar `name` como ID | rompe migraciones y soporte |
| guardar tokens en metadata | fuga de secretos |
| no versionar schema | drift silencioso |
| mezclar estado remoto y local sin timestamp | soporte a ciegas |

