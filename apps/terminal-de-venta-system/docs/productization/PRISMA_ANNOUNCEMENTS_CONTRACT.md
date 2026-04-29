---
title: PRISMA Announcements Contract
project: PRISMA Terminal de Venta
package: PRISMA_CUSTOMER_OPERATIONS_FOUNDATION_00
status: foundation-contract
visible_language: es-MX
scope: customer-operations-layer
---


# PRISMA Announcements Contract

## 1. Decisión

PRISMA debe poder mostrar novedades, avisos, banners y popups controlados desde Remote Ops.

Esta capa sirve para informar, capacitar, advertir y presentar funciones disponibles, sin interrumpir la operación de caja salvo caso crítico.

## 2. Tipos

| Tipo | Uso |
|---|---|
| info | información ligera |
| notice | aviso relevante |
| warning | advertencia operativa |
| critical | bloqueo o riesgo crítico |
| commercial | feature disponible o upgrade |
| training | guía/capacitación |
| release | notas de versión |

## 3. Severidad

| Severidad | Comportamiento |
|---|---|
| info | badge o card |
| notice | banner |
| warning | banner persistente |
| critical | modal controlado |
| commercial | centro de novedades, no checkout |

## 4. Reglas anti-spam

1. No popup comercial durante checkout.
2. No repetir anuncio descartado salvo nueva versión.
3. Target por rol, plan, dispositivo y versión.
4. Caducidad obligatoria para campañas.
5. Mensajes críticos deben explicar acción requerida.
6. Tablet debe priorizar venta sobre marketing.

## 5. Targeting

Campos mínimos:

```text
targetPlans
targetRoles
targetDevices
targetVersions
showFrom
showUntil
showOnce
dismissible
priority
```

## 6. CTA permitidos

```text
view_details
open_support
request_activation
open_release_notes
dismiss
```

No se permite CTA de pago interno.

## 7. Ejemplo

```json
{
  "announcementId": "ann_001",
  "title": "Nuevo módulo de promociones",
  "body": "El módulo de promociones está disponible para solicitar activación.",
  "severity": "commercial",
  "targetPlans": ["TABLET_PRO", "TABLET_PC_MANAGED"],
  "targetRoles": ["owner", "supervisor"],
  "ctaType": "request_activation",
  "dismissible": true
}
```

## 8. Criterio de aceptación

Un anuncio está bien implementado si informa sin estorbar, respeta roles y nunca convierte la caja en espectacular luminoso de tianguis.
