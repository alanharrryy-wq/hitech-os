# PRISMA Screen Visual Stack Plan

- Task: `Corregir PRISMA Tablet Visual Surface V2 para que todas las rutas visibles Tablet rendericen surfaces V2 reales, no sólo root tokens, eliminando documentedLegacySurface como estado terminado, sin Playwright, sin tocar PC/Mobile visualmente, sin regresiones funcionales ni sync.`

## Required order

- Read Authority Mesh files and Field Manual.
- Identify exact target screen from Atlas/docs/repo evidence; do not guess.
- Apply app capability requirements and Visual Exploitation Contract.
- Select minimal safe mutation set.
- Implement using must_use/should_use capabilities unless blocked with evidence.
- Fill used/rejected capability matrix in result package.
- Validate without process/port/dev-server/Prisma-hot manipulation.

## Candidate target files

- score=110 `products/mobile/app/src/lib/prisma-app/mobile-data-plane/pc-adapter.ts`
- score=110 `products/pc/app/app/api/backoffice/sync/export-pc-to-tablet/route.ts`
- score=110 `products/pc/app/app/api/backoffice/sync/project-tablet-to-pc/route.ts`
- score=110 `products/pc/app/app/api/backoffice/tablet-communication/governance-command/route.ts`
- score=110 `products/pc/app/app/api/backoffice/tablet-communication/route.ts`
- score=110 `products/pc/app/app/api/charts/pc/tablet-catalog-freshness-grid/route.ts`
- score=110 `products/pc/app/app/tablet-communication/error.tsx`
- score=110 `products/pc/app/app/tablet-communication/loading.tsx`
- score=110 `products/pc/app/app/tablet-communication/page.tsx`
- score=110 `products/tablet/app/app/api/pos/sync/health/pc/route.ts`
- score=110 `products/tablet/app/src/server/sync/pc-origin.ts`
- score=100 `products/pc/app/docs/PC_TABLET_CATALOG_MIRROR_04D.md`
- score=100 `products/pc/app/docs/PC_TABLET_COMMUNICATION_NOTES.md`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileActionInbox.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileCommandCenter.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileCrystalCommand.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileDailyBrief.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileDashboard.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileDecisionLedger.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileHealthRadar.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileMetricCard.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobileMultiContextSwitcher.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobilePanels.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobilePremiumNavigator.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobilePulseTimeline.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobilePwaInstallCard.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobilePwaInstallPage.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/PrismaMobilePwaRuntime.tsx`
- score=80 `products/mobile/app/src/components/prisma-app/index.ts`
- score=80 `products/pc/app/app/components/PrismaAtmosphericBackground.tsx`
- score=80 `products/pc/app/components/backoffice/data-table.tsx`
- score=80 `products/pc/app/components/backoffice/empty-state.tsx`
- score=80 `products/pc/app/components/backoffice/executive-dashboard.tsx`
- score=80 `products/pc/app/components/backoffice/ingest-event-panel.tsx`
- score=80 `products/pc/app/components/backoffice/kpi-card.tsx`
- score=80 `products/pc/app/components/backoffice/module-overview-page.tsx`
- score=80 `products/pc/app/components/backoffice/status-badge.tsx`
- score=80 `products/pc/app/components/catalog/catalog-dashboard.tsx`
- score=80 `products/pc/app/components/control/cash-sessions-operational-view.tsx`
- score=80 `products/pc/app/components/control/pc-command-actions.tsx`
- score=80 `products/pc/app/components/control/pc-command-center-page.tsx`
- score=80 `products/pc/app/components/control/sales-control-branch-view.tsx`
- score=80 `products/pc/app/components/inventory/inventory-workspace.tsx`
- score=80 `products/pc/app/components/landing/prisma-business-overview.tsx`
- score=80 `products/pc/app/components/landing/prisma-pc-interactive-command.tsx`
- score=80 `products/pc/app/components/layout/app-shell.tsx`
- score=80 `products/pc/app/components/layout/nav-link.tsx`
- score=80 `products/pc/app/components/license/feature-list.tsx`
- score=80 `products/pc/app/components/license/license-blocked-card.tsx`
- score=80 `products/pc/app/components/license/license-gate-banner.tsx`
- score=80 `products/pc/app/components/license/license-refresh-panel.tsx`
- score=80 `products/pc/app/components/license/license-status-card.tsx`
- score=80 `products/pc/app/components/license/license-warning-badge.tsx`
- score=80 `products/pc/app/components/operations/operation-workspace.tsx`
- score=80 `products/pc/app/components/prisma-glass-capsule/index.ts`
- score=80 `products/pc/app/components/prisma-glass-capsule/prisma-glass-capsule.tsx`
- score=80 `products/pc/app/components/suppliers/smart-purchase-workbench.tsx`
- score=80 `products/pc/app/components/suppliers/supplier-action-cockpit.tsx`
- score=80 `products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx`
- score=80 `products/pc/app/components/sync/sync-release-workspace.tsx`

## Focus

- primary_app: `tablet`
- screen_type: `component_system`
- signals: `['tokens']`
- premium_requested: `True`
- operational_surface: `True`
