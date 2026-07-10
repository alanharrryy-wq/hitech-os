# 08. NDC Capability, License and Module Model

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Cadena

```text
CAPABILITY → MODULE → PLAN/LICENSE → GRANT → SURFACE VISIBILITY → ROLE ACCESS → EVIDENCE → CLAIM/MONETIZATION
```

## Capability record

```json
{"capability_id":"CAP.analytics.merma","class":"pro","origin_runtime":"3000","destination_surfaces":["SURF.pc.inventory","SURF.mb.owner_home","SURF.cl.merma_trend"],"required_events":["EVT.inventory.waste.recorded"],"required_entities":["ENT.item","ENT.inventory_position"],"license_required":"MOD.abarrotes.pro","evidence_required":["EVD.runtime.chart_demo","EVD.data_source.contract"],"no_humo_limit":"No predictivo sin histórico suficiente.","status":"draft"}
```

## Pricing classes

base, pro, premium, custom, enterprise, internal.

## No-humo

```text
Claim = capability + evidence + limit + surface + role + license
```

Si falta una parte, el claim queda `blocked` o `needs_review`.
