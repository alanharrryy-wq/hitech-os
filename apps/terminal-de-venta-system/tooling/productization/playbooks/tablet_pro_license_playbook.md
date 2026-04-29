---
title: TABLET_PRO License Playbook
project: PRISMA Terminal de Venta
package: PRISMA_LICENSE_LOCAL_MOCK_02
status: productization-contract
visible_language: es-MX
---

# TABLET_PRO License Playbook


## Proposito

Playbook operativo para resolver features del plan `TABLET_PRO`.

| Estado | Feature | Allowed | Reason |
|---|---|---:|---|
| `active` | `pos.sales.complete` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.ticket.local` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.sale.cancel` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.returns.create` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.refund.review` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.cash.close` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.cash.count` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.operator.quick_actions` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.barcode.resolve` | true | `ENTITLED_BY_PLAN` |
| `active` | `pos.cart.discount.local` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.local.decrement` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.local.adjust` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.low_stock.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.stockout.mark` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.movement.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.count.quick` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.count.approve` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.merma.register` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.expiration.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `inventory.batch.view` | true | `ENTITLED_BY_PLAN` |
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
| `active` | `shift.open` | true | `ENTITLED_BY_PLAN` |
| `active` | `shift.close` | true | `ENTITLED_BY_PLAN` |
| `active` | `shift.summary.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `shift.cashier.assign` | true | `ENTITLED_BY_PLAN` |
| `active` | `shift.incident.note` | true | `ENTITLED_BY_PLAN` |
| `active` | `shift.handoff.create` | true | `ENTITLED_BY_PLAN` |
| `active` | `shift.reopen.request` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.today.basic` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.today.advanced` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.sales.export` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.inventory.export` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.margin.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.top_skus.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.sync_latency.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `report.audit.summary` | true | `ENTITLED_BY_PLAN` |
| `active` | `backup.local.manual` | true | `ENTITLED_BY_PLAN` |
| `active` | `backup.local.scheduled` | true | `ENTITLED_BY_PLAN` |
| `active` | `backup.pre_update.create` | true | `ENTITLED_BY_PLAN` |
| `active` | `backup.pre_migration.create` | true | `ENTITLED_BY_PLAN` |
| `active` | `backup.restore.request` | true | `ENTITLED_BY_PLAN` |
| `active` | `backup.retention.configure` | true | `ENTITLED_BY_PLAN` |
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
| `active` | `support.advanced` | true | `ENTITLED_BY_PLAN` |
| `active` | `support.remote` | true | `ENTITLED_BY_PLAN` |
| `active` | `support.diagnostic.create` | true | `ENTITLED_BY_PLAN` |
| `active` | `support.diagnostic.send` | true | `ENTITLED_BY_PLAN` |
| `active` | `support.ticket.create` | true | `ENTITLED_BY_PLAN` |
| `active` | `support.message.channel` | true | `ENTITLED_BY_PLAN` |
| `active` | `support.session.request` | true | `ENTITLED_BY_PLAN` |
| `active` | `license.local.read` | true | `ENTITLED_BY_PLAN` |
| `active` | `license.remote.refresh` | true | `ENTITLED_BY_PLAN` |
| `active` | `license.status.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `license.plan.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `license.entitlements.view` | true | `ENTITLED_BY_PLAN` |
| `active` | `license.grace.evaluate` | true | `ENTITLED_BY_PLAN` |

## Politica

Este playbook sirve para pruebas de UX, soporte y futura implementacion. No debe usarse como sustituto de schema ni como autorizacion de pagos.
