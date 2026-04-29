---
title: PRISMA License Entitlements Contract
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA License Entitlements Contract

## 1. Decisión

La licencia no es un candado bruto. Es un contrato técnico que habilita planes, features, plugins, grace offline y soporte.

Debe permitir activación y desactivación remota, pero sin secuestrar datos ni destruir operación local de manera abrupta.

## 2. Estados de licencia

| Estado | Significado |
|---|---|
| dev | entorno de desarrollo |
| trial | prueba temporal |
| active | licencia activa |
| offline_grace | no se pudo validar remotamente, pero sigue dentro de gracia |
| past_due_external | pendiente administrativo fuera de PRISMA |
| suspended | funciones limitadas por decisión remota |
| revoked | licencia revocada |
| expired | periodo vencido |

## 3. Planes iniciales

| Plan | Habilita |
|---|---|
| TABLET_SOLO | POS standalone, venta local, ticket, stock local, export básico |
| TABLET_PRO | devoluciones, turnos, ajustes locales, export avanzado, outbox visible |
| PC_BACKOFFICE | catálogo, inventario, compras, recepción, auditoría, dashboard, sync |
| TABLET_PC_MANAGED | Tablet + PC, pairing, sync, reconciliación, control multi-dispositivo |

## 4. Entitlements

Los entitlements son las llaves reales de features.

Ejemplos:

```text
pos.sales
pos.returns
shift.open_close
inventory.local.adjust
exports.advanced
support.channel
announcements.view
plugins.promotions.basic
sync.managed
ai.support.readonly.future
```

## 5. Reglas de suspensión

1. Suspensión no debe borrar datos.
2. Suspensión debe permitir exportar y respaldar.
3. Suspensión debe permitir soporte.
4. Suspensión debe bloquear primero features premium.
5. Venta local básica puede tener grace antes de bloqueo fuerte.
6. Toda transición sensible debe quedar auditada.

## 6. Archivo local

Ruta objetivo cliente:

```text
C:\ProgramData\PRISMA\config\license.json
```

Debe contener payload firmado o verificable.

## 7. Grace offline

El cliente puede estar sin internet. La app debe operar con la última licencia válida durante una ventana definida.

Grace no significa carta blanca eterna. Significa continuidad responsable.

## 8. Validación local

La app debe validar:

- firma o checksum,
- businessId,
- deviceId si aplica,
- plan,
- features,
- expiración,
- offline grace,
- versión de formato.

## 9. Prohibiciones

- No guardar secretos en repo.
- No depender de una llamada remota para cada venta.
- No activar plugins incompatibles.
- No ocultar al cliente el estado de licencia.
- No usar licencia para procesar pagos bancarios.

## 10. Pantallas futuras

PC:

```text
/centro-prisma/licencia
/centro-prisma/mi-plan
/centro-prisma/plugins
```

Tablet:

```text
/centro-prisma/estado
/centro-prisma/soporte
```
