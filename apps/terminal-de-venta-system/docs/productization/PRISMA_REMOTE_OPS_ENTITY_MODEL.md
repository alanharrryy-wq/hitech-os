---
title: PRISMA Remote Ops Entity Model
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Remote Ops Entity Model

## Entidades proveedor

```text
ProviderAccount
Customer
Business
Location
Device
License
Entitlement
Plan
Plugin
Release
Announcement
MessageThread
SupportTicket
DiagnosticBundle
RemoteCommand
AuditLog
```

## Customer

Representa al cliente comercial. Puede tener uno o más negocios.

Campos sugeridos:

```text
customerId
name
contactName
contactEmail
contactPhone
status
createdAt
updatedAt
```

## Business

Representa un negocio operando PRISMA.

```text
businessId
customerId
businessName
locale
timezone
status
createdAt
```

## Location

Para multi-sucursal futuro.

```text
locationId
businessId
name
addressLabel
status
```

## Device

Representa instalaciones locales.

```text
deviceId
businessId
locationId
deviceType: tablet | pc | local_agent
deviceName
installedVersion
lastSeenAt
licenseStatus
syncStatus
healthStatus
```

## License

```text
licenseId
businessId
plan
status
validUntil
offlineGraceUntil
features
plugins
signature
```

## Entitlement

```text
entitlementId
businessId
featureKey
status
source
expiresAt
```

## Plugin

```text
pluginId
name
version
status
requiredPlan
compatiblePrismaVersions
permissions
signature
```

## Release

```text
releaseId
packageName
packageVersion
channel
compatibleVersions
manifestSha256
signature
publishedAt
```

## Announcement

```text
announcementId
title
body
severity
targetPlans
targetRoles
targetVersions
showFrom
showUntil
dismissible
```

## SupportTicket

```text
ticketId
businessId
deviceId
category
priority
status
subject
createdAt
updatedAt
```

## DiagnosticBundle

```text
bundleId
businessId
deviceId
level
createdAt
includes
excludes
checksum
```

## RemoteCommand

Solo comandos allowlist.

```text
commandId
businessId
deviceId
commandType
payload
requestedAt
expiresAt
signature
status
```

## AuditLog

Todo cambio sensible debe tener auditoría.

```text
auditId
actorType
actorId
businessId
deviceId
action
entityType
entityId
before
after
createdAt
```

## Relaciones

```text
Customer 1..n Business
Business 1..n Device
Business 1..n License
License 1..n Entitlement
Business 1..n SupportTicket
SupportTicket 1..n MessageThread
Device 1..n DiagnosticBundle
Release 1..n Plugin compatibility references
```

## Decisión de diseño

Remote Ops no debe modelar pagos bancarios. Puede modelar estados administrativos externos, por ejemplo `past_due_external`, pero no debe guardar tarjeta, cuenta bancaria, SPEI ni pasarela.
