# Service Repository Map

| file | kind | readsOrWrites | entities | status |
| --- | --- | --- | --- | --- |
| products/tablet/app/src/composition/module-registry.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/tablet/app/src/composition/navigation.ts | service/repository | read/no_confirmado | license,sale,sync,canonical | PASS |
| products/tablet/app/src/lib/catalog/product-form-state.ts | service/repository | read/no_confirmado | business,sync | PASS |
| products/tablet/app/src/lib/catalog-stock-selling-assist/catalog-stock-cart-handoff.ts | service/repository | read/no_confirmado | business,sale | PASS |
| products/tablet/app/src/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-contract.ts | service/repository | read/no_confirmado | business,outbox | PASS |
| products/tablet/app/src/lib/catalog-stock-selling-assist/catalog-stock-selling-assist-view-model.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/lib/contextual-export-reports/contextual-export-contract.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/tablet/app/src/lib/contextual-export-reports/contextual-export-view-model.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/tablet/app/src/lib/core/types.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/tablet/app/src/lib/data/demo.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/tablet/app/src/lib/i18n/messages/es.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/lib/i18n/tablet-visible-labels.ts | service/repository | read/no_confirmado | sale,outbox,sync | PASS |
| products/tablet/app/src/lib/offline/offline-state.ts | service/repository | read/no_confirmado | outbox | PASS |
| products/tablet/app/src/lib/operational-gate/can-sell.ts | service/repository | read/no_confirmado | cash session | PASS |
| products/tablet/app/src/lib/pending-offline-sync/sync-panel-contract.ts | service/repository | read/no_confirmado | sync | PASS |
| products/tablet/app/src/lib/pending-offline-sync/sync-panel-view-model.ts | service/repository | read/no_confirmado | sale,sale line,sync | PASS |
| products/tablet/app/src/lib/pos/cart-engine.ts | service/repository | read/no_confirmado | client,business | PASS |
| products/tablet/app/src/lib/pos/cart-state.ts | service/repository | read/no_confirmado | client,business,sale,tender,cash session,sync,canonical | PASS |
| products/tablet/app/src/lib/pos/payment-error-normalizer.ts | service/repository | read/no_confirmado | sync | PASS |
| products/tablet/app/src/lib/pos/payment-flow.ts | service/repository | read/write | client,business,sale,tender,cash session,sync | PASS |
| products/tablet/app/src/lib/pos/payment-idempotency.ts | service/repository | read/no_confirmado | client,sync | PASS |
| products/tablet/app/src/lib/pos/payment-ledger.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/lib/pos/payment-offline-policy.ts | service/repository | read/no_confirmado | sale,sale line | PASS |
| products/tablet/app/src/lib/pos/payment-operation-events.ts | service/repository | read/no_confirmado | client,business,sale | PASS |
| products/tablet/app/src/lib/pos/payment-session.ts | service/repository | read/no_confirmado | business,cash session,sync | PASS |
| products/tablet/app/src/lib/pos/payment-state.ts | service/repository | read/no_confirmado | client,tender | PASS |
| products/tablet/app/src/lib/pos/payment-tender.ts | service/repository | read/no_confirmado | client,tender | PASS |
| products/tablet/app/src/lib/pos/payment-view-model.ts | service/repository | read/no_confirmado | sale,tender | PASS |
| products/tablet/app/src/lib/pos/pos-visible-errors.ts | service/repository | read/no_confirmado | business,sync | PASS |
| products/tablet/app/src/lib/pos/shift-flow.ts | service/repository | read/no_confirmado | business,sale,sync | PASS |
| products/tablet/app/src/lib/pos/ticket-success-view-model.ts | service/repository | read/no_confirmado | sale,sale line,sync | PASS |
| products/tablet/app/src/lib/pos-ui/pos-error-copy.ts | service/repository | read/no_confirmado | business | PASS |
| products/tablet/app/src/lib/returns-contextual/return-audit-ledger.ts | service/repository | read/no_confirmado | sale,audit | PASS |
| products/tablet/app/src/lib/returns-contextual/return-flow.ts | service/repository | read/write | sale,sync | PASS |
| products/tablet/app/src/lib/returns-contextual/return-policy-engine.ts | service/repository | read/no_confirmado | sale,sale line | PASS |
| products/tablet/app/src/lib/returns-contextual/return-reasons.ts | service/repository | read/no_confirmado | client | PASS |
| products/tablet/app/src/lib/returns-contextual/return-stock-impact.ts | service/repository | read/no_confirmado | sale,sale line | PASS |
| products/tablet/app/src/lib/returns-contextual/return-view-model.ts | service/repository | read/no_confirmado | business,sale,sale line,cash session | PASS |
| products/tablet/app/src/lib/sales-today/sales-kpi-engine.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/lib/sales-today/sales-ticket-export.ts | service/repository | read/no_confirmado | sale,sale line | PASS |
| products/tablet/app/src/lib/sales-today/sales-ticket-filters.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/lib/sales-today/types.ts | service/repository | read/no_confirmado | client,business,sale,sale line,cash session | PASS |
| products/tablet/app/src/lib/sales-today/view-model.ts | service/repository | read/no_confirmado | sale,sale line | PASS |
| products/tablet/app/src/lib/services/checkout.ts | service/repository | read/no_confirmado | outbox | PASS |
| products/tablet/app/src/lib/services/dashboard.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/tablet/app/src/lib/services/hardening.ts | service/repository | read/no_confirmado | outbox,sync | PASS |
| products/tablet/app/src/lib/services/returns.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/tablet/app/src/lib/services/sales.ts | service/repository | read/no_confirmado | sale,sale line,sync | PASS |
| products/tablet/app/src/lib/services/shift.ts | service/repository | read/no_confirmado | sale,cash session,sync | PASS |
| products/tablet/app/src/lib/services/stock.ts | service/repository | read/no_confirmado | sync | PASS |
| products/tablet/app/src/lib/services/sync.ts | service/repository | read/no_confirmado | sale,outbox,sync | PASS |
| products/tablet/app/src/lib/services/ux-pro.ts | service/repository | read/no_confirmado | client,sale,outbox,sync,audit | PASS |
| products/tablet/app/src/lib/shift-cash-closure/shift-cash-closure-contract.ts | service/repository | read/no_confirmado | business,sale | PASS |
| products/tablet/app/src/lib/shift-cash-closure/shift-cash-closure-view-model.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/lib/tablet-home/home-view-model.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/lib/tablet-home/operational-priority.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/lib/tablet-runtime-snapshot/shell-contract.ts | service/repository | read/no_confirmado | business,sale,cash session,sync | PASS |
| products/tablet/app/src/lib/tablet-runtime-snapshot/view-model.ts | service/repository | read/no_confirmado | sale,sync,audit | PASS |
| products/tablet/app/src/lib/tablet-runtime-snapshot/visible-copy.ts | service/repository | read/no_confirmado | business,outbox | PASS |
| products/tablet/app/src/modules/pos/module.manifest.ts | service/repository | read/no_confirmado | outbox | PASS |
| products/tablet/app/src/modules/sales/module.manifest.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/modules/sync/module.manifest.ts | service/repository | read/no_confirmado | sync | PASS |
| products/tablet/app/src/navigation/tablet-page-contracts.ts | service/repository | read/no_confirmado | license,sale,outbox,sync,canonical | PASS |
| products/tablet/app/src/server/licensing/tablet-customer-setup.ts | service/repository | read/no_confirmado | device | PASS |
| products/tablet/app/src/server/licensing/tablet-license-api.ts | service/repository | read/no_confirmado | license,sync | PASS |
| products/tablet/app/src/server/licensing/tablet-license-refresh.ts | service/repository | read/no_confirmado | license,sync | PASS |
| products/tablet/app/src/server/licensing/tablet-license-service.ts | service/repository | read/no_confirmado | license | PASS |
| products/tablet/app/src/server/local-catalog/index.ts | service/repository | read/no_confirmado | business,sync | PASS |
| products/tablet/app/src/server/operable-release-gate/index.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/server/pos-api/errors.ts | service/repository | read/no_confirmado | business,tender,sync | PASS |
| products/tablet/app/src/server/pos-api/local-admin.prisma.ts | service/repository | read/write | client,business,license,sync,audit | PASS |
| products/tablet/app/src/server/pos-api/product-mutation-validators.ts | service/repository | read/no_confirmado | business | PASS |
| products/tablet/app/src/server/pos-api/product-mutations.prisma.ts | service/repository | read/write | client,business,outbox,sync | PASS |
| products/tablet/app/src/server/pos-api/product-queries.prisma.ts | service/repository | read/no_confirmado | client,business,sync | PASS |
| products/tablet/app/src/server/pos-api/return-validators.ts | service/repository | read/no_confirmado | business,sale,cash session,sync | PASS |
| products/tablet/app/src/server/pos-api/returns-policy.prisma.ts | service/repository | read/no_confirmado | client,business,sale,sale line,sync | PASS |
| products/tablet/app/src/server/pos-api/returns.prisma.ts | service/repository | read/write | client,business,sale,sale line,cash session,outbox,sync | PASS |
| products/tablet/app/src/server/pos-api/sales-detail.prisma.ts | service/repository | read/no_confirmado | client,business,license,sale,sale line,tender,cash session,outbox,sync,canonical,audit | PASS |
| products/tablet/app/src/server/pos-api/sales-reset.prisma.ts | service/repository | read/write | client,business,license,sale,sale line,tender,cash session,outbox,sync,audit | PASS |
| products/tablet/app/src/server/pos-api/sales-summary.prisma.ts | service/repository | read/no_confirmado | client,business,sale,sale line,cash session,sync | PASS |
| products/tablet/app/src/server/pos-api/supplier-mutations.prisma.ts | service/repository | read/write | client,business,outbox,sync | PASS |
| products/tablet/app/src/server/pos-api/validators.ts | service/repository | read/no_confirmado | client,business,sale,sale line,tender,cash session,sync | PASS |
| products/tablet/app/src/server/pos-engine/audit.ts | service/repository | read/no_confirmado | audit | PASS |
| products/tablet/app/src/server/pos-engine/constants.ts | service/repository | read/no_confirmado | business,sale,cash session,outbox,sync | PASS |
| products/tablet/app/src/server/pos-engine/errors.ts | service/repository | read/no_confirmado | business,tender,sync | PASS |
| products/tablet/app/src/server/pos-engine/event-factory.ts | service/repository | read/no_confirmado | business,sale,sale line,tender,cash session | PASS |
| products/tablet/app/src/server/pos-engine/events.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/server/pos-engine/ids.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/server/pos-engine/repository.prisma.ts | service/repository | read/write | client,business,sale,sale line,tender,cash session,outbox,sync | PASS |
| products/tablet/app/src/server/pos-engine/types.ts | service/repository | read/no_confirmado | client,business,sale,sale line,tender,cash session | PASS |
| products/tablet/app/src/server/pos-export/contextual.ts | service/repository | read/no_confirmado | business,sale,sync | PASS |
| products/tablet/app/src/server/pos-export/index.ts | service/repository | read/no_confirmado | client,business,sale,sale line,outbox,sync | PASS |
| products/tablet/app/src/server/pos-outbox/index.ts | service/repository | read/no_confirmado | client,business,outbox,sync | PASS |
| products/tablet/app/src/server/pos-reports/index.ts | service/repository | read/no_confirmado | client,business,sale,outbox,sync | PASS |
| products/tablet/app/src/server/pos-runtime/index.ts | service/repository | read/no_confirmado | sale | PASS |
| products/tablet/app/src/server/pos-security/audit.ts | service/repository | read/write | business,sale,audit | PASS |
| products/tablet/app/src/server/pos-shift/repository.prisma.ts | service/repository | read/write | client,business,sale,cash session,outbox,sync | PASS |
| products/tablet/app/src/server/pos-shift/types.ts | service/repository | read/no_confirmado | business,sale | PASS |
| products/tablet/app/src/server/pos-shift/validators.ts | service/repository | read/no_confirmado | business,sync | PASS |
| products/tablet/app/src/server/pos-sync-panel/index.ts | service/repository | read/no_confirmado | client,business,sale,outbox,sync | PASS |
| products/tablet/app/src/server/prisma/client.ts | service/repository | read/no_confirmado | client,sync | PASS |
| products/tablet/app/src/server/repositories/dashboard-kpi.repository.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/tablet/app/src/server/repositories/outbox-repository.prisma.ts | service/repository | read/no_confirmado | client,outbox | PASS |
| products/tablet/app/src/server/repositories/product-repository.prisma.ts | service/repository | read/no_confirmado | client | PASS |
| products/tablet/app/src/server/repositories/return-repository.prisma.ts | service/repository | read/no_confirmado | client,sale | PASS |
| products/tablet/app/src/server/repositories/sale-repository.prisma.ts | service/repository | read/no_confirmado | client,sale,sale line | PASS |
| products/tablet/app/src/server/repositories/shift-repository.prisma.ts | service/repository | read/no_confirmado | client,cash session | PASS |
| products/tablet/app/src/server/sync/catalog-pull.ts | service/repository | read/write | client,business,device,sale,sync | PASS |
| products/tablet/app/src/server/sync/dispatcher.ts | service/repository | read/write | client,business,sale,outbox,sync,canonical | PASS |
| products/tablet/app/src/server/sync/events.ts | service/repository | read/no_confirmado | sale,cash session,sync | PASS |
| products/tablet/app/src/server/sync/outbox.ts | service/repository | read/no_confirmado | outbox,sync | PASS |
| products/tablet/app/src/server/sync/pc-origin.ts | service/repository | read/no_confirmado | sync | PASS |
| products/tablet/app/src/server/tablet-runtime-snapshot/build.ts | service/repository | read/no_confirmado | business,sale,cash session,sync | PASS |
| products/tablet/app/src/server/tablet-runtime-snapshot/env.ts | service/repository | read/no_confirmado | business | PASS |
| products/tablet/app/src/server/tablet-runtime-snapshot/index.ts | service/repository | read/no_confirmado | sync | PASS |
| products/tablet/app/src/server/tablet-runtime-snapshot/queries.prisma.ts | service/repository | read/no_confirmado | client,business,sale,cash session,outbox,sync | PASS |
| products/tablet/app/src/server/tablet-runtime-snapshot/types.ts | service/repository | read/no_confirmado | business,sale | PASS |
| products/tablet/app/src/visual-os/realtime/prisma-realtime-client.ts | service/repository | read/write | client,sync | PASS |
| products/pc/app/src/composition/module-registry.ts | service/repository | read/no_confirmado | license,device,sale,cash session,sync,audit | PASS |
| products/pc/app/src/composition/navigation.ts | service/repository | read/no_confirmado | client,license,device,sale,tender,sync | PASS |
| products/pc/app/src/lib/backoffice/conflicts.ts | service/repository | read/no_confirmado | sale | PASS |
| products/pc/app/src/lib/backoffice/dashboard.ts | service/repository | read/no_confirmado | client,sale,sale line,outbox,sync,canonical,audit | PASS |
| products/pc/app/src/lib/backoffice/event-contract.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/lib/backoffice/overview.ts | service/repository | read/no_confirmado | client,outbox,sync,canonical,audit | PASS |
| products/pc/app/src/lib/backoffice/security-audit.ts | service/repository | read/write | business,sync,audit | PASS |
| products/pc/app/src/lib/backoffice/sync-ingest-store.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/lib/core/route-contracts.ts | service/repository | read/no_confirmado | license,device,sale,cash session,sync,audit | PASS |
| products/pc/app/src/lib/core/types.ts | service/repository | read/no_confirmado | sync,audit | PASS |
| products/pc/app/src/lib/data/demo.ts | service/repository | read/no_confirmado | outbox,sync,audit | PASS |
| products/pc/app/src/lib/i01/governance-data.ts | service/repository | read/no_confirmado | sync,audit | PASS |
| products/pc/app/src/lib/i03/project-index.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/i05/replenishment-sync-data.ts | service/repository | read/no_confirmado | outbox,sync,audit | PASS |
| products/pc/app/src/lib/i06/dashboard-data.ts | service/repository | read/no_confirmado | sale,outbox,audit | PASS |
| products/pc/app/src/lib/i06/dashboard-helpers.ts | service/repository | read/no_confirmado | sale,outbox,audit | PASS |
| products/pc/app/src/lib/i07/validation-data.ts | service/repository | read/no_confirmado | sale | PASS |
| products/pc/app/src/lib/i08/ux-data.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/i09/detail-data.ts | service/repository | read/no_confirmado | sale,outbox,audit | PASS |
| products/pc/app/src/lib/i10/reporting-data.ts | service/repository | read/no_confirmado | outbox,sync,audit | PASS |
| products/pc/app/src/lib/i18n/messages/es.ts | service/repository | read/no_confirmado | sync,audit | PASS |
| products/pc/app/src/lib/services/catalog.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/lib/services/dashboard.ts | service/repository | read/no_confirmado | outbox,sync | PASS |
| products/pc/app/src/lib/services/inventory.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/services/procurement.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/lib/services/sync.ts | service/repository | read/no_confirmado | outbox,sync | PASS |
| products/pc/app/src/lib/suppliers/action-reducer.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/suppliers/client-persistence.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/suppliers/data-quality.ts | service/repository | read/no_confirmado | sale,sync,audit | PASS |
| products/pc/app/src/lib/suppliers/event-catalog.ts | service/repository | read/write | business | PASS |
| products/pc/app/src/lib/suppliers/export-contracts.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/suppliers/fixtures.ts | service/repository | read/no_confirmado | business,sale,sync,audit | PASS |
| products/pc/app/src/lib/suppliers/in-memory-repository.ts | service/repository | read/no_confirmado | sync,audit | PASS |
| products/pc/app/src/lib/suppliers/inventory-bridge.ts | service/repository | read/no_confirmado | client,sale,sync | PASS |
| products/pc/app/src/lib/suppliers/lifecycle-engine.ts | service/repository | read/no_confirmado | sync,audit | PASS |
| products/pc/app/src/lib/suppliers/lifecycle-report.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/suppliers/lifecycle-scenarios.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/suppliers/lifecycle-validator.ts | service/repository | read/write | sync,audit | PASS |
| products/pc/app/src/lib/suppliers/operations-view-model.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/suppliers/prisma-mapping.ts | service/repository | read/no_confirmado | business,audit | PASS |
| products/pc/app/src/lib/suppliers/repository-contract.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/suppliers/server.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/lib/suppliers/smart-purchase-engine.ts | service/repository | read/no_confirmado | sale,audit | PASS |
| products/pc/app/src/lib/suppliers/transition-policy.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/lib/suppliers/types.ts | service/repository | read/no_confirmado | sale,audit | PASS |
| products/pc/app/src/lib/suppliers/visible-labels.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/modules/audit/module.manifest.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/modules/catalog/types.ts | service/repository | read/no_confirmado | business,canonical | PASS |
| products/pc/app/src/modules/inventory/types.ts | service/repository | read/no_confirmado | canonical,audit | PASS |
| products/pc/app/src/modules/operations/types.ts | service/repository | read/no_confirmado | sale,canonical | PASS |
| products/pc/app/src/modules/sync/module.manifest.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/modules/sync/tri-db-status.types.ts | service/repository | read/no_confirmado | sale,outbox,sync | PASS |
| products/pc/app/src/modules/sync/types.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/prisma-visual-os/interface-constitution/types.ts | service/repository | read/no_confirmado | sync,audit | PASS |
| products/pc/app/src/server/licensing/pc-customer-setup.ts | service/repository | read/no_confirmado | device | PASS |
| products/pc/app/src/server/licensing/pc-license-api.ts | service/repository | read/no_confirmado | license,sync | PASS |
| products/pc/app/src/server/licensing/pc-license-refresh.ts | service/repository | read/no_confirmado | license,sync | PASS |
| products/pc/app/src/server/licensing/pc-license-service.ts | service/repository | read/no_confirmado | license,sync,audit | PASS |
| products/pc/app/src/server/prisma/client.ts | service/repository | read/no_confirmado | client,sync,canonical | PASS |
| products/pc/app/src/server/repositories/audit-repository.prisma.ts | service/repository | read/no_confirmado | client,audit | PASS |
| products/pc/app/src/server/repositories/barcode-repository.prisma.ts | service/repository | read/no_confirmado | client | PASS |
| products/pc/app/src/server/repositories/catalog.repository.ts | service/repository | read/no_confirmado | client,business,sync | PASS |
| products/pc/app/src/server/repositories/inventory.repository.ts | service/repository | read/no_confirmado | client,business,sync,audit | PASS |
| products/pc/app/src/server/repositories/operation.repository.ts | service/repository | read/no_confirmado | client,business,sale,cash session,sync | PASS |
| products/pc/app/src/server/repositories/outbox-repository.prisma.ts | service/repository | read/no_confirmado | client,outbox | PASS |
| products/pc/app/src/server/repositories/product-repository.prisma.ts | service/repository | read/no_confirmado | client | PASS |
| products/pc/app/src/server/repositories/purchase-order-repository.prisma.ts | service/repository | read/no_confirmado | client | PASS |
| products/pc/app/src/server/repositories/stock-repository.prisma.ts | service/repository | read/no_confirmado | client | PASS |
| products/pc/app/src/server/services/catalog-delta-export.service.ts | service/repository | read/write | client,business,sync,canonical,audit | PASS |
| products/pc/app/src/server/services/catalog.service.ts | service/repository | read/no_confirmado | sync,canonical | PASS |
| products/pc/app/src/server/services/inventory-ledger.service.ts | service/repository | read/no_confirmado | sync,canonical,audit | PASS |
| products/pc/app/src/server/services/kpi-formulas.ts | service/repository | read/no_confirmado | sale | PASS |
| products/pc/app/src/server/services/operation-control.service.ts | service/repository | read/no_confirmado | sale,sync,canonical | PASS |
| products/pc/app/src/server/services/pc-command-center.service.ts | service/repository | read/write | client,tenant,business,license,device,sale,sale line,tender,cash session,outbox,sync,canonical,audit | PASS |
| products/pc/app/src/server/services/pc-data-mode-contract.service.ts | service/repository | read/write | client,business,device,sale,sale line,cash session,outbox,sync,canonical,audit | PASS |
| products/pc/app/src/server/services/pc-sync-chart-data.service.ts | service/repository | read/no_confirmado | client,business,device,sync,audit | PASS |
| products/pc/app/src/server/services/sync-ingest.service.ts | service/repository | read/write | client,business,sale,outbox,sync | PASS |
| products/pc/app/src/server/services/sync-observability.service.ts | service/repository | read/write | client,business,device,outbox,sync | PASS |
| products/pc/app/src/server/services/sync-projectors.service.ts | service/repository | read/write | client,business,sale,sale line,tender,cash session,outbox,sync,canonical | PASS |
| products/pc/app/src/server/services/sync-release.service.ts | service/repository | read/no_confirmado | client,business,sale,outbox,sync | PASS |
| products/pc/app/src/server/services/tri-db-command.service.ts | service/repository | read/no_confirmado | outbox,sync,canonical | PASS |
| products/pc/app/src/server/services/tri-db-status.service.ts | service/repository | read/no_confirmado | sale,outbox,sync | PASS |
| products/pc/app/src/server/sync/events.ts | service/repository | read/no_confirmado | sale,cash session,sync | PASS |
| products/pc/app/src/server/sync/outbox.ts | service/repository | read/no_confirmado | outbox | PASS |
| products/pc/app/src/server/validators/catalog-quality.ts | service/repository | read/no_confirmado | sync,audit | PASS |
| products/pc/app/src/server/validators/inventory-integrity.ts | service/repository | read/no_confirmado | sale,audit | PASS |
| products/pc/app/src/server/validators/sync-event-contract.ts | service/repository | read/write | business,sale,cash session,outbox,sync,canonical | PASS |
| products/pc/app/src/uiux/catalog-screen-contract.ts | service/repository | read/no_confirmado | sync | PASS |
| products/pc/app/src/uiux/copy-dictionary.ts | service/repository | read/no_confirmado | license,device,canonical,audit | PASS |
| products/pc/app/src/uiux/decision-model.ts | service/repository | read/no_confirmado | license,device,sale,cash session,outbox,sync,canonical,audit | PASS |
| products/pc/app/src/uiux/page-contracts.ts | service/repository | read/no_confirmado | license,device,sale,tender,cash session,outbox,sync,canonical,audit | PASS |
| products/pc/app/src/uiux/pc-product-navigation.ts | service/repository | read/no_confirmado | business,license,device,sale,cash session,outbox,sync,canonical,audit | PASS |
| products/pc/app/src/uiux/purchasing-screen-contract.ts | service/repository | read/no_confirmado | tender,audit | PASS |
| products/pc/app/src/uiux/reports-screen-contract.ts | service/repository | read/no_confirmado | audit | PASS |
| products/pc/app/src/uiux/route-map.ts | service/repository | read/no_confirmado | business,license,device,sale,cash session,outbox,sync,audit | PASS |
| products/pc/app/src/uiux/sales-and-cash-screen-contract.ts | service/repository | read/no_confirmado | sale,cash session,audit | PASS |
| products/pc/app/src/uiux/settings-screen-contract.ts | service/repository | read/no_confirmado | license,audit | PASS |
| products/pc/app/src/uiux/status-translator.ts | service/repository | read/no_confirmado | canonical | PASS |
| products/pc/app/src/uiux/suppliers-screen-contract.ts | service/repository | read/no_confirmado | tender,audit | PASS |
| products/pc/app/src/uiux/sync-screen-contract.ts | service/repository | read/no_confirmado | outbox,sync | PASS |
| products/pc/app/src/uiux/system-screen-contract.ts | service/repository | read/no_confirmado | device,sync,audit | PASS |
| products/pc/app/src/uiux/technical-route-map.ts | service/repository | read/no_confirmado | license,device,audit | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobileActionInbox.tsx | service/repository | read/no_confirmado | client | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobileCommandCenter.tsx | service/repository | read/no_confirmado | client,sale,tender,sync | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobileCrystalCommand.tsx | service/repository | read/no_confirmado | client,sale,outbox,sync | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobileDailyBrief.tsx | service/repository | read/no_confirmado | client | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobileDashboard.tsx | service/repository | read/no_confirmado | client,sync | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobileDecisionLedger.tsx | service/repository | read/no_confirmado | client,audit | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobileHealthRadar.tsx | service/repository | read/no_confirmado | client | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobileMultiContextSwitcher.tsx | service/repository | read/no_confirmado | client,business,device,sale,sync | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobilePanels.tsx | service/repository | read/no_confirmado | client,sale,sync | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobilePremiumNavigator.tsx | service/repository | read/no_confirmado | client,device,sale,sale line,sync | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobilePulseTimeline.tsx | service/repository | read/no_confirmado | client | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobilePwaInstallCard.tsx | service/repository | read/no_confirmado | client,device,sync | PASS |
| products/mobile/app/src/components/prisma-app/PrismaMobilePwaRuntime.tsx | service/repository | read/write | client | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/alerts-policy.ts | service/repository | read/no_confirmado | device,sale,outbox,sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/cash-policy.ts | service/repository | read/no_confirmado | sale,canonical | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/config.ts | service/repository | read/no_confirmado | tenant,business,license,device,sale,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/data-readiness.ts | service/repository | read/no_confirmado | sale,outbox,sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/diagnostics.ts | service/repository | read/no_confirmado | sale,outbox,sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/endpoint-handlers.ts | service/repository | read/no_confirmado | sale,sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/endpoints.ts | service/repository | read/no_confirmado | business,sale,outbox,sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/http.ts | service/repository | read/no_confirmado | sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/inventory-adapter.ts | service/repository | read/no_confirmado | canonical | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/local-db-snapshot.ts | service/repository | read/no_confirmado | business,sale,sale line,cash session,outbox,sync,canonical | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/money.ts | service/repository | read/no_confirmado | sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/outbox-adapter.ts | service/repository | read/no_confirmado | outbox,sync,canonical | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/payload-builders.ts | service/repository | read/no_confirmado | tenant,business,license,device,sale,sale line,outbox,sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/pc-adapter.ts | service/repository | read/no_confirmado | sale,sync,canonical | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/sales-adapter.ts | service/repository | read/no_confirmado | sale,sale line,canonical | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/state-loader.ts | service/repository | read/no_confirmado | sale,sale line,outbox,sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-data-plane/types.ts | service/repository | read/no_confirmado | tenant,business,license,device,sale,sale line,outbox,sync,canonical | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/action-inbox-engine.ts | service/repository | read/no_confirmado | device,sale,sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/alert-engine.ts | service/repository | read/no_confirmado | device,sale,outbox,sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/chart-series-engine.ts | service/repository | read/no_confirmado | sale,sale line,outbox,sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/connectors.ts | service/repository | read/no_confirmado | sale,outbox,sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/contracts.ts | service/repository | read/no_confirmado | business,device,sale,sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/daily-brief-engine.ts | service/repository | read/no_confirmado | business | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/health-radar-engine.ts | service/repository | read/no_confirmado | sale,outbox,sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/snapshot-engine.ts | service/repository | read/no_confirmado | business,sale,sync | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/source-status.ts | service/repository | read/no_confirmado | sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/timeline-engine.ts | service/repository | read/no_confirmado | sale | PASS |
| products/mobile/app/src/lib/prisma-app/mobile-intelligence/view-models.ts | service/repository | read/no_confirmado | sale,outbox,sync | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-app-api-contracts.ts | service/repository | read/no_confirmado | tenant,business,license,device,sale,sync | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-app-section-contracts.ts | service/repository | read/no_confirmado | client,sale,sync | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-action-inbox.ts | service/repository | read/no_confirmado | client,sale,sync | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-api-client.ts | service/repository | read/no_confirmado | client,sale,sync | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-cache.ts | service/repository | read/no_confirmado | client | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-command-center.ts | service/repository | read/no_confirmado | client,sale,sync,audit | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-customer-setup.ts | service/repository | read/no_confirmado | device | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-daily-brief.ts | service/repository | read/no_confirmado | client,business,sale,sale line,tender | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-decision-ledger.ts | service/repository | read/no_confirmado | client,business,audit | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-health-radar.ts | service/repository | read/no_confirmado | client,business,sale,sale line,tender,sync | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-pulse-timeline.ts | service/repository | read/no_confirmado | client,business,sale,sale line,sync | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-pwa-client.ts | service/repository | read/no_confirmado | device,sync | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-snapshot-contract.ts | service/repository | read/no_confirmado | client,sale | PASS |
| products/mobile/app/src/lib/prisma-app/prisma-mobile-view-model.ts | service/repository | read/no_confirmado | business,sale,sale line,sync | PASS |
| infra/cloudflare/licflow3-worker/src/worker.js | service/repository | read/write | client,tenant,business,license,device,setup bundle,claim slot,sale,outbox,sync,canonical,audit | PASS |
