# PRISMA Visual Stack Decision

- Task: `RIFAT centralizar toda la autoridad visual operativa de PRISMA en prisma-html, generar runtime visual canónico Tablet, migrar todas las rutas visuales Tablet, retirar estilos legacy y certificar cero downgrades`
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

- score=80 `products/tablet/app/app/tablet-lab/components/TabletLabAutoStudio.tsx`
- score=80 `products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx`
- score=80 `products/tablet/app/components/catalog/catalog-barcode-field.tsx`
- score=80 `products/tablet/app/components/catalog/catalog-empty-state.tsx`
- score=80 `products/tablet/app/components/catalog/catalog-product-drawer.tsx`
- score=80 `products/tablet/app/components/catalog/catalog-product-form.tsx`
- score=80 `products/tablet/app/components/catalog/catalog-product-table.tsx`
- score=80 `products/tablet/app/components/catalog/catalog-screen.tsx`
- score=80 `products/tablet/app/components/catalog/catalog-stock-field.tsx`
- score=80 `products/tablet/app/components/checkout/checkout-cash-calculator.tsx`
- score=80 `products/tablet/app/components/checkout/checkout-payment-methods.tsx`
- score=80 `products/tablet/app/components/checkout/checkout-screen.tsx`
- score=80 `products/tablet/app/components/checkout/checkout-summary-card.tsx`
- score=80 `products/tablet/app/components/checkout/checkout-summary.tsx`
- score=80 `products/tablet/app/components/checkout/payment-method-selector.tsx`
- score=80 `products/tablet/app/components/checkout/ticket-confirmation.tsx`
- score=80 `products/tablet/app/components/inventory/inventory-operations-workspace.tsx`
- score=80 `products/tablet/app/components/layout/app-shell.tsx`
- score=80 `products/tablet/app/components/layout/nav-link.tsx`
- score=80 `products/tablet/app/components/license/feature-list.tsx`
- score=80 `products/tablet/app/components/license/license-blocked-card.tsx`
- score=80 `products/tablet/app/components/license/license-gate-banner.tsx`
- score=80 `products/tablet/app/components/license/license-refresh-panel.tsx`
- score=80 `products/tablet/app/components/license/license-status-card.tsx`
- score=80 `products/tablet/app/components/license/license-warning-badge.tsx`
- score=80 `products/tablet/app/components/offline/offline-export-audit-screen.tsx`
- score=80 `products/tablet/app/components/operational-screen/index.ts`
- score=80 `products/tablet/app/components/operational-screen/prisma-operational-screen.tsx`
- score=80 `products/tablet/app/components/pos/pos-cobro-surface.tsx`
- score=80 `products/tablet/app/components/pos/pos-customer-binding.tsx`
- score=80 `products/tablet/app/components/pos/pos-error-banner.tsx`
- score=80 `products/tablet/app/components/pos/pos-live-binding.tsx`
- score=80 `products/tablet/app/components/pos/pos-packshots.ts`
- score=80 `products/tablet/app/components/pos/pos-payment-panel.tsx`
- score=80 `products/tablet/app/components/pos/pos-payment-risk-banner.tsx`
- score=80 `products/tablet/app/components/pos/pos-product-list.tsx`
- score=80 `products/tablet/app/components/pos/pos-product-search.tsx`
- score=80 `products/tablet/app/components/pos/pos-sale-success.tsx`
- score=80 `products/tablet/app/components/pos/pos-screen.tsx`
- score=80 `products/tablet/app/components/pos/pos-shortcuts.tsx`

## GovMesh3 escalation

- Also obey `VISUAL_EXPLOITATION_CONTRACT.md`.
- Also obey `APP_CAPABILITY_REQUIREMENTS.json` / `.md`.
- Also obey `SCREEN_VISUAL_STACK_PLAN.md`.
- Also obey `PREMIUM_ACCEPTANCE_BAR.md`.
- Result packages must complete `USED_REJECTED_REQUIREMENT.md`.
