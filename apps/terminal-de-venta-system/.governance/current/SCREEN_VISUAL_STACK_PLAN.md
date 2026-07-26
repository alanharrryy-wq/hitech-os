# PRISMA Screen Visual Stack Plan

- Task: `FIX deuda residual Tablet 3120 posterior al PASS del ChunkLoadError. Corregir exclusivamente: (1) referencias mediaRef locales bajo /product-media/ que apuntan a archivos inexistentes, sin mutar DB ni sync y usando el packshot gobernado ya existente como fallback; (2) GET /api/pos/export/sales-today?format=csv reutilizando el read model canonico probado de sales-today; (3) migrar Tablet de middleware.ts a proxy.ts sin cambiar comportamiento; (4) actualizar solo los verifiers Tablet que resuelven esa convencion. Scope Tablet, Quality y Governance. Excluir PC, Mobile, Web, Chart Lab, Shared UI, Control Center, DB, schema, migraciones, datos, sync, Git y deploy. Runtime permitido unicamente Tablet 3120 despues de demostrar ownership. No ejecutar Prisma generate. Clasificacion Factory Ledger FIX.`

## Required order

- Read Authority Mesh files and Field Manual.
- Identify exact target screen from Atlas/docs/repo evidence; do not guess.
- Apply app capability requirements and Visual Exploitation Contract.
- Select minimal safe mutation set.
- Implement using must_use/should_use capabilities unless blocked with evidence.
- Fill used/rejected capability matrix in result package.
- Validate without process/port/dev-server/Prisma-hot manipulation.

## Candidate target files

- score=160 `products/pc/app/app/api/charts/pc/tablet-catalog-freshness-grid/route.ts`
- score=160 `products/tablet/app/app/api/pos/sync/health/pc/route.ts`
- score=130 `products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx`
- score=130 `products/pc/app/components/uiux/chart-insight-card.tsx`
- score=130 `products/tablet/app/components/pos/pos-customer-binding.tsx`
- score=130 `products/tablet/app/components/pos/pos-error-banner.tsx`
- score=130 `products/tablet/app/components/pos/pos-live-binding.tsx`
- score=130 `products/tablet/app/components/pos/pos-packshots.ts`
- score=130 `products/tablet/app/components/pos/pos-payment-panel.tsx`
- score=130 `products/tablet/app/components/pos/pos-payment-risk-banner.tsx`
- score=130 `products/tablet/app/components/pos/pos-product-list.tsx`
- score=130 `products/tablet/app/components/pos/pos-product-search.tsx`
- score=130 `products/tablet/app/components/pos/pos-sale-success.tsx`
- score=130 `products/tablet/app/components/pos/pos-screen.tsx`
- score=130 `products/tablet/app/components/pos/pos-shortcuts.tsx`
- score=130 `products/tablet/app/components/pos/pos-ticket-panel.tsx`
- score=130 `products/tablet/app/components/pos/terminal-v2/index.ts`
- score=130 `products/tablet/app/components/pos/terminal-v2/pos-command-dock.tsx`
- score=130 `products/tablet/app/components/pos/terminal-v2/pos-product-canvas.tsx`
- score=130 `products/tablet/app/components/pos/terminal-v2/pos-terminal-header.tsx`
- score=130 `products/tablet/app/components/pos/terminal-v2/pos-terminal-surface.tsx`
- score=130 `products/tablet/app/components/pos/terminal-v2/pos-ticket-rail.tsx`
- score=130 `products/tablet/app/components/pos/use-prisma-packshot-skin.ts`
- score=130 `products/tablet/app/components/tablet-pos/touch-pos-ui.tsx`
- score=120 `products/pc/app/components/sync/pc-sync-chart-promotion-panel.module.css`
- score=120 `products/tablet/app/components/pos/pos.module.css`
- score=120 `products/tablet/app/components/pos/pos.visual.presets.json`
- score=120 `products/tablet/app/components/pos/pos.visual.schema.json`
- score=120 `products/tablet/app/components/pos/pos.visual.tokens.json`
- score=120 `products/tablet/app/components/pos/terminal-v2/pos-terminal-surface.module.css`
- score=120 `products/tablet/app/components/tablet-pos/touch-pos.module.css`
- score=110 `products/mobile/app/app/prisma-command/charts/MobileActionInboxPriorityStack.tsx`
- score=110 `products/mobile/app/app/prisma-command/charts/MobileChartCard.tsx`
- score=110 `products/mobile/app/app/prisma-command/charts/MobileConfidenceMeterBands.tsx`
- score=110 `products/mobile/app/app/prisma-command/charts/MobileFreshnessRings.tsx`
- score=110 `products/mobile/app/app/prisma-command/charts/MobileHealthRadarCompact.tsx`
- score=110 `products/mobile/app/app/prisma-command/charts/MobileIncidentSparkCards.tsx`
- score=110 `products/mobile/app/app/prisma-command/charts/MobileOwnerPulseTimeline.tsx`
- score=110 `products/mobile/app/src/lib/prisma-app/mobile-data-plane/pc-adapter.ts`
- score=110 `products/mobile/app/src/lib/prisma-app/mobile-intelligence/chart-series-engine.ts`
- score=110 `products/pc/app/app/api/backoffice/sync/export-pc-to-tablet/route.ts`
- score=110 `products/pc/app/app/api/backoffice/sync/project-tablet-to-pc/route.ts`
- score=110 `products/pc/app/app/api/backoffice/tablet-communication/governance-command/route.ts`
- score=110 `products/pc/app/app/api/backoffice/tablet-communication/route.ts`
- score=110 `products/pc/app/app/api/charts/pc/sync-command-lifecycle-timeline/route.ts`
- score=110 `products/pc/app/app/laboratorio-pc/chart-lab/page.tsx`
- score=110 `products/pc/app/app/prisma-insights/chart-lab/page.tsx`
- score=110 `products/pc/app/app/prisma-insights/charts/PcCausalFlowRibbon.tsx`
- score=110 `products/pc/app/app/prisma-insights/charts/PcChartCard.tsx`
- score=110 `products/pc/app/app/prisma-insights/charts/PcDecisionLedgerTimeline.tsx`
- score=110 `products/pc/app/app/prisma-insights/charts/PcFinancialOperationalWaterfall.tsx`
- score=110 `products/pc/app/app/prisma-insights/charts/PcInventoryRiskTreemap.tsx`
- score=110 `products/pc/app/app/prisma-insights/charts/PcOperationalDensityField.tsx`
- score=110 `products/pc/app/app/prisma-insights/charts/PcServiceDependencyGraph.tsx`
- score=110 `products/pc/app/app/tablet-communication/error.tsx`
- score=110 `products/pc/app/app/tablet-communication/loading.tsx`
- score=110 `products/pc/app/app/tablet-communication/page.tsx`
- score=110 `products/pc/app/src/composition/module-registry.ts`
- score=110 `products/pc/app/src/composition/navigation.ts`
- score=110 `products/pc/app/src/composition/twin-capabilities.ts`

## Focus

- primary_app: `tablet`
- screen_type: `tablet_pos_sell`
- signals: `['pos']`
- premium_requested: `True`
- operational_surface: `True`
