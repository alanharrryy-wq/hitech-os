# 06. NDC Provenance, Sync and Lineage

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Modelo

```text
AGENT/DEVICE/SURFACE/TOOL → ACTION → EVENT → ENTITY/DATASET → SYNC/OUTBOX → CANONICAL → METRIC/ALERT → SURFACE/UI/REPORT
```

## Roles

producer, actor, observer, curator, validator, consumer.

## Reconciliation: 231 vs 228

NDC revisa: tenant, business, store, date range, timezone, sale status, sync state, duplicates/rejected, canonical freshness, surface filters, metric formula y stale evidence.

## Drift record

```json
{"drift_id":"DRF.sales.count.20260709.001","observed_difference":"Tablet 231 vs PC 228","neutral_target":"MET.sales.today","hypotheses":["pending_sync","duplicate_rejected","date_range_mismatch","store_scope_mismatch","canonical_projection_stale"],"required_evidence":["EVD.tablet.outbox_count","EVD.pc.canonical_query","EVD.metric.formula","EVD.surface.filter_state"],"status":"needs_review"}
```

## Edge chain

```text
ACT.sale.checkout → emits EVT.sale.created → writes ENT.sale → delivered_by DS.tablet_outbox → accepted_by CAN.sale → derives MET.sales.today → projected_to SURF.pc.sales_control → represented_by WID.pc.sales.today_card
```
