# PRISMA Visual Stack Decision

- Task: `Build PRISMA Premium Visual Mise en Place v1 across Tablet, Mobile/App, PC, Web/Edit, Control Center, Chart Lab and Shared UI, preparing all surfaces to use the full available visual library/effect/token/component ecosystem for future premium design.`
- Visual required: `True`

## Principle

Exploit the maximum safe/governed visual stack per app/surface, not every library blindly.

## Mandatory outputs when visual/premium

- VISUAL_CAPABILITY_MATRIX.json
- VISUAL_CAPABILITY_MATRIX.md
- VISUAL_STACK_DECISION.md
- APP_VISUAL_EXPLOITATION_MATRIX.md
- Per-result used/rejected capability rationale
- Layer budget notes
- Performance risk notes
- Visual evidence or explicit pending visual verification

## Hard rules

- Prefer PRISMA governed components/recipes/tokens before raw libraries.
- Use Liquid/Pill/Cloudglass only when allowed by recipe map, authority map, surface adapter and layer budget.
- Do not install new dependencies.
- Do not claim premium visual exploitation unless used/rejected decisions are documented.
- Do not let visual atmosphere block operational clarity or touch flow.

## Candidate target files

- score=160 `products/pc/app/app/api/charts/pc/tablet-catalog-freshness-grid/route.ts`
- score=130 `products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx`
- score=130 `products/pc/app/components/uiux/chart-insight-card.tsx`
- score=120 `products/pc/app/components/sync/pc-sync-chart-promotion-panel.module.css`
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
- score=110 `products/pc/app/src/prisma-visual-os/interface-constitution/InsightChartFrame.tsx`
- score=110 `products/pc/app/src/server/services/pc-sync-chart-data.service.ts`
- score=110 `products/tablet/app/app/api/pos/sync/health/pc/route.ts`
- score=110 `products/tablet/app/app/prisma-pulse/charts/TabletChartCard.tsx`
- score=110 `products/tablet/app/app/prisma-pulse/charts/TabletShiftPulseStrip.tsx`
- score=110 `products/tablet/app/app/prisma-pulse/charts/TabletSyncOutboxStatusMatrix.tsx`
- score=110 `products/tablet/app/src/server/sync/pc-origin.ts`
- score=100 `products/pc/app/docs/PC_TABLET_CATALOG_MIRROR_04D.md`
- score=100 `products/pc/app/docs/PC_TABLET_COMMUNICATION_NOTES.md`
- score=100 `products/pc/app/public/surface-visual-governor/dashboard/latest/recipe-export/chart.recipe.json`

## GovMesh3 escalation

- Also obey `VISUAL_EXPLOITATION_CONTRACT.md`.
- Also obey `APP_CAPABILITY_REQUIREMENTS.json` / `.md`.
- Also obey `SCREEN_VISUAL_STACK_PLAN.md`.
- Also obey `PREMIUM_ACCEPTANCE_BAR.md`.
- Result packages must complete `USED_REJECTED_REQUIREMENT.md`.
