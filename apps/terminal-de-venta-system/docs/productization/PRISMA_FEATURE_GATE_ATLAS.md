---
title: PRISMA Feature Gate Atlas
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
---

# PRISMA Feature Gate Atlas


## Proposito

Este atlas convierte las capacidades de PRISMA en llaves estables para licenciamiento, plugins, UI y soporte. La idea es evitar que cada pantalla invente su propio candado como vecindad sin administrador.

| Feature key | Dominio | Riesgo | Offline | Auditoria |
|---|---|---|---|---|
| `pos.sales.complete` | pos | high | allowed-local | si |
| `pos.ticket.local` | pos | high | allowed-local | si |
| `pos.sale.cancel` | pos | high | allowed-local | si |
| `pos.returns.create` | pos | high | allowed-local | si |
| `pos.refund.review` | pos | high | allowed-local | si |
| `pos.cash.close` | pos | high | allowed-local | si |
| `pos.cash.count` | pos | high | allowed-local | si |
| `pos.operator.quick_actions` | pos | high | allowed-local | si |
| `pos.barcode.resolve` | pos | high | allowed-local | si |
| `pos.cart.discount.local` | pos | high | allowed-local | si |
| `inventory.local.decrement` | inventory | high | allowed-local | si |
| `inventory.local.adjust` | inventory | high | allowed-local | si |
| `inventory.low_stock.view` | inventory | high | allowed-local | si |
| `inventory.stockout.mark` | inventory | high | allowed-local | si |
| `inventory.movement.view` | inventory | high | allowed-local | si |
| `inventory.count.quick` | inventory | high | allowed-local | si |
| `inventory.count.approve` | inventory | high | allowed-local | si |
| `inventory.merma.register` | inventory | high | allowed-local | si |
| `inventory.expiration.view` | inventory | high | allowed-local | si |
| `inventory.batch.view` | inventory | high | allowed-local | si |
| `catalog.read` | catalog | low | requires-policy | no |
| `catalog.write` | catalog | low | requires-policy | no |
| `catalog.price.write` | catalog | low | requires-policy | no |
| `catalog.barcode.write` | catalog | low | requires-policy | no |
| `catalog.snapshot.import` | catalog | low | requires-policy | no |
| `catalog.snapshot.publish` | catalog | low | requires-policy | no |
| `catalog.category.write` | catalog | low | requires-policy | no |
| `catalog.inactive.view` | catalog | low | requires-policy | no |
| `catalog.duplicate_barcode.resolve` | catalog | low | requires-policy | no |
| `catalog.bulk_import` | catalog | low | requires-policy | no |
| `shift.open` | shift | low | allowed-local | no |
| `shift.close` | shift | low | allowed-local | no |
| `shift.summary.view` | shift | low | allowed-local | no |
| `shift.cashier.assign` | shift | low | allowed-local | no |
| `shift.incident.note` | shift | low | allowed-local | no |
| `shift.handoff.create` | shift | low | allowed-local | no |
| `shift.reopen.request` | shift | low | allowed-local | no |
| `report.today.basic` | report | low | allowed-local | no |
| `report.today.advanced` | report | low | allowed-local | no |
| `report.sales.export` | report | low | allowed-local | no |
| `report.inventory.export` | report | low | allowed-local | no |
| `report.margin.view` | report | low | allowed-local | no |
| `report.top_skus.view` | report | low | allowed-local | no |
| `report.sync_latency.view` | report | low | allowed-local | no |
| `report.audit.summary` | report | low | allowed-local | no |
| `backup.local.manual` | backup | medium | allowed-local | si |
| `backup.local.scheduled` | backup | medium | allowed-local | si |
| `backup.pre_update.create` | backup | medium | allowed-local | si |
| `backup.pre_migration.create` | backup | medium | allowed-local | si |
| `backup.restore.request` | backup | medium | allowed-local | si |
| `backup.retention.configure` | backup | medium | allowed-local | si |
| `sync.outbox.view` | sync | high | requires-policy | si |
| `sync.managed` | sync | high | requires-policy | si |
| `sync.ingest` | sync | high | requires-policy | si |
| `sync.conflict.resolve` | sync | high | requires-policy | si |
| `sync.retry` | sync | high | requires-policy | si |
| `sync.snapshot.receive` | sync | high | requires-policy | si |
| `sync.snapshot.publish` | sync | high | requires-policy | si |
| `sync.latency.view` | sync | high | requires-policy | si |
| `sync.degraded_mode.view` | sync | high | requires-policy | si |
| `dashboard.kpis` | dashboard | medium | requires-policy | no |
| `dashboard.executive.view` | dashboard | medium | requires-policy | no |
| `dashboard.alerts.view` | dashboard | medium | requires-policy | no |
| `dashboard.scorecards.view` | dashboard | medium | requires-policy | no |
| `dashboard.replenishment.view` | dashboard | medium | requires-policy | no |
| `dashboard.exceptions.view` | dashboard | medium | requires-policy | no |
| `support.basic` | support | medium | cached | no |
| `support.advanced` | support | medium | cached | no |
| `support.remote` | support | medium | cached | no |
| `support.diagnostic.create` | support | medium | cached | no |
| `support.diagnostic.send` | support | medium | cached | no |
| `support.ticket.create` | support | medium | cached | no |
| `support.message.channel` | support | medium | cached | no |
| `support.session.request` | support | medium | cached | no |
| `license.local.read` | license | high | cached | si |
| `license.remote.refresh` | license | high | cached | si |
| `license.status.view` | license | high | cached | si |
| `license.plan.view` | license | high | cached | si |
| `license.entitlements.view` | license | high | cached | si |
| `license.grace.evaluate` | license | high | cached | si |
| `license.activation.request` | license | high | cached | si |
| `plugin.local.enable` | plugin | high | requires-policy | si |
| `plugin.local.disable` | plugin | high | requires-policy | si |
| `plugin.remote.activate` | plugin | high | requires-policy | si |
| `plugin.catalog.view` | plugin | high | requires-policy | si |
| `plugin.permissions.view` | plugin | high | requires-policy | si |
| `plugin.migration.apply` | plugin | high | requires-policy | si |
| `plugin.rollback` | plugin | high | requires-policy | si |
| `plugin.request.activation` | plugin | high | requires-policy | si |
| `announcement.view` | announcement | low | cached | no |
| `announcement.dismiss` | announcement | low | cached | no |
| `announcement.critical.modal` | announcement | low | cached | no |
| `announcement.commercial.card` | announcement | low | cached | no |
| `announcement.targeted.banner` | announcement | low | cached | no |
| `announcement.whats_new.view` | announcement | low | cached | no |
| `ai.support.readonly.future` | ai | low | requires-policy | no |
| `ai.diagnostic.summary.future` | ai | low | requires-policy | no |
| `ai.kpi.explain.future` | ai | low | requires-policy | no |
| `ai.catalog.assist.future` | ai | low | requires-policy | no |
| `ai.action.suggest.future` | ai | low | requires-policy | no |

## Regla

Toda feature visible debe resolverse mediante contrato de licencia o entitlement. No usar `if plan == "pro"` regado en veinte componentes como confeti de boda barata.
