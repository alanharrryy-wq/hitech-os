# PRISMA Visual Stack Decision

- Task: `Corregir PRISMA Tablet Visual Surface V2 para que todas las rutas visibles Tablet rendericen surfaces V2 reales, no sólo root tokens, eliminando documentedLegacySurface como estado terminado, sin Playwright, sin tocar PC/Mobile visualmente, sin regresiones funcionales ni sync.`
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

## GovMesh3 escalation

- Also obey `VISUAL_EXPLOITATION_CONTRACT.md`.
- Also obey `APP_CAPABILITY_REQUIREMENTS.json` / `.md`.
- Also obey `SCREEN_VISUAL_STACK_PLAN.md`.
- Also obey `PREMIUM_ACCEPTANCE_BAR.md`.
- Result packages must complete `USED_REJECTED_REQUIREMENT.md`.
