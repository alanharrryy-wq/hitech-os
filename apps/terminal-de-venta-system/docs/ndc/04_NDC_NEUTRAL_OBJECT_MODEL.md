# 04. NDC Neutral Object Model

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Familias neutrales

| Familia | Prefijo | Pregunta | Ejemplos |
|---|---|---|---|
| Entity | `ENT` | cosa de negocio | `ENT.sale`, `ENT.item`, `ENT.cash_session` |
| Event | `EVT` | qué ocurrió | `EVT.sale.created`, `EVT.payment.recorded` |
| Action | `ACT` | qué se intentó | `ACT.sale.checkout`, `ACT.inventory.adjust` |
| State | `STA` | estado derivado | `STA.sync.pending`, `STA.canonical.accepted` |
| Metric | `MET` | valor calculado | `MET.sales.today`, `MET.stock.critical_count` |
| Alert | `ALT` | riesgo/aviso | `ALT.stock.low`, `ALT.cash.risk` |
| Evidence | `EVD` | prueba | `EVD.receipt`, `EVD.screenshot.pos_ticket` |
| Capability | `CAP` | capacidad | `CAP.pos.sale`, `CAP.analytics.merma` |
| Canonical | `CAN` | verdad consolidada | `CAN.sale`, `CAN.inventory_position` |

## Ejemplo record

```json
{"record_id":"ENT.sale","record_type":"neutral_entity","prefix":"ENT","definition":"Venta neutral independiente de surface.","scope_required":["tenant","business","store","source_device","source_surface"],"events_required":["EVT.sale.created"],"canonical_projection":"CAN.sale","status":"defined","evidence_policy":"required_for_instance"}
```

## Separation from implementation

| Neutral | DB/API/UI posible |
|---|---|
| `ENT.sale` | `sales` table, `/api/sales`, ticket UI. |
| `MET.sales.today` | SQL view, endpoint, KPI card. |
| `ACT.sale.checkout` | button, service, command handler. |
| `CAN.sale` | projection table, reducer, materialized view. |
