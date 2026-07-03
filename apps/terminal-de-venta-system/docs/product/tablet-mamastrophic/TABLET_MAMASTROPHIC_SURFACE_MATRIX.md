# TABLET MAMASTROPHIC SURFACE MATRIX

Date: 2026-07-03

| Surface | Route(s) | Current owner | Current create/action support | Initial decision |
|---|---|---|---|---|
| Inicio | `/` | `components/tablet-home/tablet-home-screen.tsx` | Real links to POS, Shift, Stock, Sales, Returns, Sync, License | Add explicit `Acciones rapidas`/tile semantics and keep max 6 actions. |
| Shell/nav | all final Tablet routes | `components/tablet-shell/prisma-tablet-shell.tsx`, `tablet-nav.ts` | Bottom dock real links; topbar context links | Keep dock primary, add/verify overflow rules without exposing lab routes. |
| POS | `/pos`, `/checkout` | `components/pos/pos-screen.tsx`, `components/pos/terminal-v2/*`, `pos.module.css` | Real search, scan, add, held tickets, checkout, product-create handoff | Polish autocollapsible search and verifier coverage; do not turn POS into catalog admin. |
| Turno y caja | `/shift` | `components/shift/shift-cash-closure-screen.tsx` | Real open/close/current APIs | Add quick action strip around real open/close/export/sell links. |
| Inventario | `/stock`, `/existencias`, `/inventory/low-stock`, `/catalog` | `components/catalog-stock-selling-assist/*`, `components/catalog/*` | Product create/update in Catalog, add-to-sale, export menu closed by default | Make Inventory the creation hub with active `Nuevo producto` routed to Catalog and blocked/deferred stock/category details where no owner exists. |
| Ventas de hoy | `/sales/today` | `components/sales/sales-today-screen.tsx` | Real ticket list, search, contextual export, return from ticket | Add quick tiles for nueva venta, buscar ticket, exportar, crear devolucion. |
| Historial | `/sales/history` | `components/sales/sales-history-screen.tsx` | Real date/query filters, ticket list | Add create/action strip for buscar, rango, export, devolucion desde ticket where contextual. |
| Devoluciones | `/returns`, `/sales/today/:saleId/return` | `components/returns/return-from-ticket-screen.tsx` | Real closed-ticket flow and return create API | Add `Nueva devolucion` tile that enters real ticket selection, not a fake form. |
| Sincronizacion | `/sync`, `/events/outbox` | `components/sync/pending-offline-sync-panel-screen.tsx`, legacy outbox screen in `touch-pos-ui.tsx` | Real dispatch, retry, panel, catalog pull | Add action tiles for sync, retry, backup, offline; keep diagnostics collapsed. |
| Offline | `/offline` | `components/offline/offline-export-audit-screen.tsx` | Real offline audit and export links | Add quick tiles for backup, pendientes, retry connection, sync. |
| Licencia | `/settings/license` | `app/settings/license/page.tsx`, `components/license/*` | Read-only canonical governor, refresh status | Add human action tiles for soporte/copy/export where real, keep details collapsed. |
| Exportaciones | `/settings/export` | `components/tablet-pos/touch-pos-ui.tsx` `ExportSettingsScreen` | Real export endpoints for sales/events/inventory movements | Replace flat buttons with tiles by type and visible success/error feedback. |
| Configuracion | `/settings/data`, `/settings/license`, `/settings/export` | contracts/nav plus license/export pages | License/export routes real; local admin is internal/admin | Use More/config links only; do not expose reset/local-data admin controls. |
| Estado operativo | `/prisma-pulse` | `app/prisma-pulse/*` | Candidate support route | Keep as support/candidate until cleaned; do not promote without verifier and copy cleanup. |

## Deferred Or Blocked Actions

- `Nuevo proveedor`: API exists, but visible Tablet owner/form is not established for final customer flow. Keep deferred unless implemented in a scoped supervisor form.
- `Ajustar stock`: recent movement read APIs exist, but no final visible stock-adjust mutation owner was found in preflight. Document as deferred unless an existing mutation owner is confirmed.
- `Nueva categoria`: product form uses category text, but no standalone category persistence owner was found in preflight. Document as deferred or implement only as part of product form if already supported.
- `Importar licencia`: no Tablet-local final import UI owner confirmed in the canonical license surface. Keep read-only/support unless a real owner is found.
