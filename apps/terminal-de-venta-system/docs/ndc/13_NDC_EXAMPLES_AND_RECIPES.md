# 13. NDC Examples and Recipes

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Venta creada desde Tablet

```json
{"neutral_entity":"ENT.sale","event":"EVT.sale.created","action":"ACT.sale.checkout","scope":{"tenant":"TEN.prisma_rey","business":"BIZ.prisma_rey.main","store":"STO.prisma_rey.centro","terminal":"TERM.pos.01","source_device":"DEV.tb.pos.01","source_surface":"SURF.tb.pos","user":"USR.cashier.01","role":"ROLE.cashier"},"canonical":{"projection":"CAN.sale","status":"accepted","sync_status":"synced","lineage":["tablet_outbox","cloud_gateway","canonical_sales"]},"visible_in":["SURF.tb.pos.ticket","SURF.pc.sales_control","SURF.mb.owner_home","SURF.cl.sales_trend"],"ui_examples":["TB-POS-PAY-BTN-01","PC-SALES-MAIN-TBL-01","MB-HOME-KPI-01","CL-SALES-CH-01"]}
```

## Recetas

### Agregar panel
Crear PNL, hijos WID/TBL/CHT/FRM/BTN, neutral_target, surface_id, reads/writes/actions, evidence policy y matrix view.

### Agregar métrica Chart Lab
Crear MET, DS contract, formula, scope dimensions, surfaces destino, license/pricing, evidence/demo, no-humo limit.

### Explicar 231 vs 228
Crear DRF, target MET/CAN, comparar scope/status/date/sync/filter/formula, asociar evidence y resolver.

### Agregar vertical
Mantener neutrales, crear translation catalog, pack, event examples, projection map y no-humo claims.
