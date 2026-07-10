# 07. NDC Canonical Projection Model

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Definición

`CAN.*` consolida verdad operacional. No es pantalla, tabla ni reporte por default.

## Canonicals iniciales

| Canonical | Consolida | Proyecciones |
|---|---|---|
| `CAN.sale` | ventas aceptadas | Tablet ticket, PC sales, Mobile summary, Chart Lab. |
| `CAN.inventory_position` | stock por item/store | POS, PC inventory, Mobile alerts. |
| `CAN.cash_session` | caja/turno | POS, PC audit, Mobile risk. |
| `CAN.device_status` | estado device/license | 3150/3160. |
| `CAN.license_status` | licencia/grace/revoke | 3150/3110/Mobile. |
| `CAN.metric.sales.today` | métrica diaria | PC KPI/Mobile/Chart Lab. |

## Status

candidate, pending, accepted, duplicate, rejected, superseded, stale, disputed, needs_review.

## Promotion gate

Debe tener neutral target, scope, acceptance/rejection rules, lineage, evidence policy, surfaces consumidoras, drift handling y curation path.
