# 10. NDC Evidence, Curation and Governance

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Evidence types

screenshot, DOM snapshot, computed CSS, API response, DB row, outbox event, test result, log/trace, manual decision, document canon, metric sample, chart demo, release report, audit event.

## Evidence record

```json
{"evidence_id":"EVD.runtime.pc.sales.card.screenshot","evidence_type":"screenshot","source_tool":"ScreensQA","artifact_uri":"raw_inputs/screensqa/sales-card.png","target_refs":["SURF.pc.sales_control","WID.pc.sales.today_card"],"supports":["represented_by"],"does_not_prove":["CAN.sale.accepted","MET.sales.today.formula"],"confidence":"medium","freshness":"unknown","review_status":"needs_review"}
```

## Readiness states

ready, needs_review, blocked, partial, stale, orphan, conflict.

**Orphan nunca puede ser ready sin curation.**

## Curation files

`manual_decisions.jsonl`, `aliases.jsonl`, `overrides.jsonl`, `review_notes.jsonl`, `canonical_promotions.jsonl`.

## Decision types

alias, override, promote, reject, split, merge, dispute, note.

## Gates

scope.required, event.provenance, evidence.minimum, no_humo.claim, surface.projection, canonical.acceptance, tenant.leakage, db.handoff.
