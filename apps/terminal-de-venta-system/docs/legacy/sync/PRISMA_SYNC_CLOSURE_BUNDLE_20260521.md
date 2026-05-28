---
title: PRISMA_SYNC_CLOSURE_BUNDLE_20260521
path: docs/legacy/sync/PRISMA_SYNC_CLOSURE_BUNDLE_20260521.md
status: LEGACY
version: 2026.05.26-full-doc-governance-v1
updated: 2026-05-26
owner: PRISMA Governance
supersedes: []
live_verification: false
evidence_scope: static package analysis from ALL_CODE_260526_054718, prisma_todo_el_show_260526_070949, GOBIERNO_*_260526_0719, and prior PRISMA project context
note: Legacy document preserved for history. It must not override current authority docs.
---

# LEGACY NOTICE

This document has been moved to legacy.

## Superseded by

- `docs/sync/PC_TABLET_SYNC_CURRENT_AUTHORITY.md`
- `docs/sync/PRISMA_SYNC_ENDPOINTS_REAL_VS_STUBS.md`
- `docs/sync/PC_TO_TABLET_CATALOG_DELTA_CLOSURE_01.md` when the topic is PC → Tablet catalog delta

## Reason

This historical closure/patch document may contain statements that are no longer current after later sync implementation and governance clarification.

---

# Original preserved content

# PRISMA Sync Closure Bundle 2026-05-21

Este bundle cierra los huecos detectados entre Tablet y PC para eventos críticos de operación local-first.

## Cambios incluidos

- PC ahora proyecta más eventos canónicos a tablas reales:
  - `sale.created`
  - `sale.completed`
  - `ticket.closed`
  - `stock.decremented`
  - `stock.adjusted`
  - `catalog.product.created`
  - `catalog.product.updated`
  - `sale.refunded`
  - `sale.cancelled`
  - `shift.closed`
- `sale.completed` crea/actualiza `Sale`, `SaleLine` y `SalePaymentTender`.
- `stock.decremented` actualiza también `Product.stockOnHand`, no solo `StockMovement`.
- Catálogo desde Tablet emite envelopes completos con `terminalId`, `actorId`, `eventType`, `schemaVersion: "1.0.0"`, `costCents` y barcodes.
- Devoluciones desde Tablet cambian de `sale.return.created` a `sale.refunded`, crean líneas locales, movimientos de stock y envelope compatible con PC.
- Sync Tablet -> PC queda default-off por `PRISMA_TABLET_PC_SYNC_ENABLED=false` hasta habilitación explícita.
- Se agrega verificador `tools/verify_prisma_sync_projection_closure_02.mjs`.

## Aplicación

Ejecutar desde PowerShell 7.6.x:

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\APPLY_BUNDLE.ps1 -TargetRoot '<REPO_ROOT>\apps\terminal-de-venta-system'
```

El instalador crea backup en `<OUTPUT_DIR>`, copia solo archivos nuevos/cambiados, corre verificadores y hace rollback automático si algo falla.

## Verificadores esperados

- `node tools/verify_prisma_sync_projection_closure_02.mjs`
- `node tools/verify-sync-closure-truth.mjs`
- `node tools/verify_sync_contract_gate_01.mjs`
- `node tools/verify_prisma_event_sync_architecture_01.mjs`
- `node tools/verify-no-fake-green.mjs`
- `node tools/verify-ack-required.mjs`
- `node products/pc/app/tools/verify_pc_ingest_idempotency_01.mjs` desde `products/pc/app`
- `node products/tablet/app/tools/verify_tablet_sync_dispatcher_01.mjs` desde `products/tablet/app`

## Límite honesto

Este bundle mejora el cierre Tablet -> PC y cubre eventos que antes quedaban reconocidos pero no proyectados. No convierte el sistema en una replicación bidireccional completa PC -> Tablet. Para eso aún falta un pull/snapshot/delta channel desde PC hacia Tablet.
