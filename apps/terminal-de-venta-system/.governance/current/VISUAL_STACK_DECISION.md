# PRISMA Visual Stack Decision

- Task: `PRISMA Tablet POS Sell premium visual continuation: audit and stabilize incomplete Codex visual changes for Tablet POS / Vender / Productos / Carrito / Checkout / Cobrar. Preserve real products, prices, SKUs, cart bindings, business logic and Mount Fuji/cloudy background. Scope is Tablet POS sell screen foreground only. Audit new CSS priority override usage and globals.css risk, separate useful visual changes from CSS contamination, then prepare authority for one definitive fix: product vitrines, premium cart column, stable iridescent Cobrar CTA, light tactile foreground. Exclude PC, Mobile, Chart Lab, database sync, schema changes, commits, push, merge, process kill, port cleanup, dev server start, Playwright loop and Prisma hot regeneration.`
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

- score=200 `products/tablet/app/docs/pos/PRISMA_POS_VISUAL_04_CART_CHECKOUT_HIERARCHY.md`
- score=200 `products/tablet/app/docs/pos/PRISMA_TABLET_SELL_CHECKOUT_PAYMENT_FLOW_04A.md`
- score=180 `products/tablet/app/components/prisma-dark-pos/prisma-cart-panel.tsx`
- score=160 `products/pc/app/app/api/charts/pc/tablet-catalog-freshness-grid/route.ts`
- score=160 `products/tablet/app/app/api/pos/sync/health/pc/route.ts`
- score=160 `products/tablet/app/src/lib/catalog-stock-selling-assist/catalog-stock-cart-handoff.ts`
- score=160 `products/tablet/app/src/lib/pos/cart-engine.ts`
- score=160 `products/tablet/app/src/lib/pos/cart-state.ts`
- score=160 `products/tablet/app/src/lib/pos/cart-view-model.ts`
- score=160 `products/tablet/app/src/lib/pos/held-carts.ts`
- score=150 `products/tablet/app/docs/pos/PRISMA_TABLET_CHECKOUT_FINALIZATION_FIX_31.md`
- score=150 `products/tablet/app/docs/qa/PRISMA_TABLET_POS_GOLDEN_FLOW_HOLD_CARTS_04G_ACCEPTANCE.md`
- score=150 `products/tablet/app/docs/qa/PRISMA_TABLET_SELL_CART_03D_QA.md`
- score=150 `products/tablet/app/docs/qa/PRISMA_TABLET_SELL_CHECKOUT_PAYMENT_FLOW_04A_QA.md`
- score=150 `products/tablet/app/docs/qa/pos-checkout-02/acceptance.md`
- score=150 `products/tablet/app/docs/qa/pos-checkout-02/smoke-tests.md`
- score=150 `products/tablet/app/docs/ux/PRISMA_TABLET_POS_GOLDEN_FLOW_HOLD_CARTS_04G.md`
- score=150 `products/tablet/app/docs/ux/PRISMA_TABLET_SELL_CART_03D_FOUNDATION.md`
- score=150 `products/tablet/app/tools/fixtures/tablet_sell_checkout_payment_04a_cases.json`
- score=130 `products/pc/app/app/components/PrismaAtmosphericBackground.tsx`
- score=130 `products/pc/app/components/sync/pc-sync-chart-promotion-panel.tsx`
- score=130 `products/pc/app/components/uiux/chart-insight-card.tsx`
- score=130 `products/tablet/app/components/catalog-stock-selling-assist/catalog-stock-selling-assist-screen.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-cash-calculator.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-payment-methods.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-screen.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-summary-card.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-summary.tsx`
- score=130 `products/tablet/app/components/checkout/payment-method-selector.tsx`
- score=130 `products/tablet/app/components/checkout/ticket-confirmation.tsx`
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

## GovMesh3 escalation

- Also obey `VISUAL_EXPLOITATION_CONTRACT.md`.
- Also obey `APP_CAPABILITY_REQUIREMENTS.json` / `.md`.
- Also obey `SCREEN_VISUAL_STACK_PLAN.md`.
- Also obey `PREMIUM_ACCEPTANCE_BAR.md`.
- Result packages must complete `USED_REJECTED_REQUIREMENT.md`.
