---
title: TABLET_SOLO License Playbook
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
---

# TABLET_SOLO License Playbook


## Proposito

Playbook operativo para resolver features del plan `TABLET_SOLO`.

| Estado | Feature | Allowed | Reason |
|---|---|---:|---|
| `active` | `pos.sales.complete` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.ticket.local` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.sale.cancel` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `pos.returns.create` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `pos.refund.review` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `pos.cash.close` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `pos.cash.count` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `pos.operator.quick_actions` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `pos.barcode.resolve` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `pos.cart.discount.local` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.local.decrement` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.local.adjust` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.low_stock.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.stockout.mark` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.movement.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.count.quick` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.count.approve` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.merma.register` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.expiration.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `inventory.batch.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.read` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.write` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.price.write` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.barcode.write` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.snapshot.import` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.snapshot.publish` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.category.write` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.inactive.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.duplicate_barcode.resolve` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `catalog.bulk_import` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `shift.open` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `shift.close` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `shift.summary.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `shift.cashier.assign` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `shift.incident.note` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `shift.handoff.create` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `shift.reopen.request` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `report.today.basic` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.today.advanced` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `report.sales.export` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `report.inventory.export` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `report.margin.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `report.top_skus.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `report.sync_latency.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `report.audit.summary` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `backup.local.manual` | true | `ENTITLED_BY_PLAN` |
| `active` | `backup.local.scheduled` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `backup.pre_update.create` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `backup.pre_migration.create` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `backup.restore.request` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `backup.retention.configure` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.outbox.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.managed` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.ingest` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.conflict.resolve` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.retry` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.snapshot.receive` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.snapshot.publish` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.latency.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `sync.degraded_mode.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `dashboard.kpis` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `dashboard.executive.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `dashboard.alerts.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `dashboard.scorecards.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `dashboard.replenishment.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `dashboard.exceptions.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `support.basic` | true | `ENTITLED_BY_PLAN` |
| `active` | `support.advanced` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `support.remote` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `support.diagnostic.create` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `support.diagnostic.send` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `support.ticket.create` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `support.message.channel` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `support.session.request` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `license.local.read` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `license.remote.refresh` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `license.status.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `license.plan.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `license.entitlements.view` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |
| `active` | `license.grace.evaluate` | false | `FEATURE_NOT_INCLUDED_IN_PLAN` |

## Politica

Este playbook sirve para pruebas de UX, soporte y futura implementacion. No debe usarse como sustituto de schema ni como autorizacion de pagos.
