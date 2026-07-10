# 05. NDC Event, Action and State Model

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Diferencia

| Concepto | Prefijo | Ejemplo | Regla |
|---|---|---|---|
| Acción | `ACT` | `ACT.sale.checkout` | intención/comando. |
| Evento | `EVT` | `EVT.sale.created` | hecho ocurrido. |
| Estado | `STA` | `STA.sync.pending` | condición derivada. |

## Event envelope

```json
{"event_id":"EVT.sale.created:20260709:000001","event_type":"EVT.sale.created","occurred_at":"2026-07-09T08:15:00-06:00","source":{"tenant_id":"TEN.prisma_rey","business_id":"BIZ.prisma_rey.main","store_id":"STO.prisma_rey.centro","terminal_id":"TERM.pos.01","device_id":"DEV.tb.pos.01","surface_id":"SURF.tb.pos","user_id":"USR.cashier.01","role_id":"ROLE.cashier"},"action_id":"ACT.sale.checkout","entity_refs":["ENT.sale","ENT.payment","ENT.sale_line"],"sync_status":"synced","canonical_status":"pending","evidence_refs":["EVD.receipt","EVD.outbox.event_row"]}
```

## Event classes

Create, Record, Adjust, Approve, Sync, License, Evidence, Alert.

## States

sync, canonical, commercial, device, evidence, surface.

## Transition template

```text
from_state → to_state
trigger: EVT.*
actor: ROLE.*
requires: EVD.*
impact: CAN.* / SURF.* / LIC.*
```
