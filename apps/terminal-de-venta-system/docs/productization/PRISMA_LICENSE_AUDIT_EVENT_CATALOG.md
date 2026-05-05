---
title: PRISMA License Audit Event Catalog
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
---

# PRISMA License Audit Event Catalog


## Proposito

Eventos administrativos que deben existir cuando la capa de licencia deje de ser mock.

| Codigo | Topic | Severidad | Aviso visible |
|---|---|---|---:|
| `LIC-001-INFO` | `license.loaded` | info | no |
| `LIC-001-WARNING` | `license.loaded` | warning | si |
| `LIC-001-CRITICAL` | `license.loaded` | critical | si |
| `LIC-002-INFO` | `license.invalid` | info | no |
| `LIC-002-WARNING` | `license.invalid` | warning | si |
| `LIC-002-CRITICAL` | `license.invalid` | critical | si |
| `LIC-003-INFO` | `license.refreshed` | info | no |
| `LIC-003-WARNING` | `license.refreshed` | warning | si |
| `LIC-003-CRITICAL` | `license.refreshed` | critical | si |
| `LIC-004-INFO` | `license.status_changed` | info | no |
| `LIC-004-WARNING` | `license.status_changed` | warning | si |
| `LIC-004-CRITICAL` | `license.status_changed` | critical | si |
| `LIC-005-INFO` | `license.grace_started` | info | no |
| `LIC-005-WARNING` | `license.grace_started` | warning | si |
| `LIC-005-CRITICAL` | `license.grace_started` | critical | si |
| `LIC-006-INFO` | `license.grace_expired` | info | no |
| `LIC-006-WARNING` | `license.grace_expired` | warning | si |
| `LIC-006-CRITICAL` | `license.grace_expired` | critical | si |
| `LIC-007-INFO` | `feature.denied` | info | no |
| `LIC-007-WARNING` | `feature.denied` | warning | si |
| `LIC-007-CRITICAL` | `feature.denied` | critical | si |
| `LIC-008-INFO` | `plugin.entitlement_changed` | info | no |
| `LIC-008-WARNING` | `plugin.entitlement_changed` | warning | si |
| `LIC-008-CRITICAL` | `plugin.entitlement_changed` | critical | si |
| `LIC-009-INFO` | `plan.changed` | info | no |
| `LIC-009-WARNING` | `plan.changed` | warning | si |
| `LIC-009-CRITICAL` | `plan.changed` | critical | si |
| `LIC-010-INFO` | `device.license_mismatch` | info | no |
| `LIC-010-WARNING` | `device.license_mismatch` | warning | si |
| `LIC-010-CRITICAL` | `device.license_mismatch` | critical | si |

## Regla

Cambios de plan, estado, feature y plugin no deben ocurrir en silencio. Si no deja rastro, luego soporte termina leyendo el humo como chamán de changarro.
