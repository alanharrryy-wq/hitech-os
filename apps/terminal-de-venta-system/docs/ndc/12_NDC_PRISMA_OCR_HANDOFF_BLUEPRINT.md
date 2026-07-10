# 12. NDC Prisma OCR Handoff Blueprint

> Estado: NDC DOC1 canon documental completo. No DB, no Prisma schema, no migrations, no Git, no servidores. Las matrices son vistas generadas, no fuente de verdad.

## Estado

No crea DB. Define condiciones para `ndc db1`.

## Posibles tablas futuras

| Familia | Tabla futura |
|---|---|
| scope | `ndc_scope_records` |
| neutral | `ndc_records` |
| edges | `ndc_edges` |
| evidence | `ndc_evidence` |
| curation | `ndc_curation_decisions` |
| matrix views | `ndc_matrix_views` |
| export runs | `ndc_export_runs` |
| drift | `ndc_drift_cases` |
| gates | `ndc_gate_results` |

## Blockers para DB

Falta ID grammar, scope registry, neutral object registry, edge registry, evidence schema, curation schema, matrix definitions, canonical status rules, no-humo rules o rollback strategy.

## Invariants futuros

record_id único, edge deterministic, tenant requerido, curation append-only, exports reproducibles, orphans no ready, cross-tenant con grant explícito.
