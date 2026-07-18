# PRISMA Visual Stack Decision

- Task: `PC96FLOW functional data completion in PC and Tablet with shared kernel, local database schema and additive migrations, durable sync, audit, idempotency, ACK/checkpoint/conflict and quality verification. Resolve canonical owner chains for command center, sales, cash, catalog, pricing, inventory, purchasing, customers, security, organization devices, sync and licensing readiness. Complete the corresponding Tablet POS, checkout, catalog, inventory, sales, returns, shift, offline sync, settings and setup routes. Preserve unrelated current Tablet stylesheet changes.`
- Visual required: `False`

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

- score=160 `products/tablet/app/app/api/pos/sync/health/pc/route.ts`
- score=150 `products/tablet/app/docs/pos/PRISMA_POS_VISUAL_04_CART_CHECKOUT_HIERARCHY.md`
- score=150 `products/tablet/app/docs/pos/PRISMA_TABLET_CHECKOUT_FINALIZATION_FIX_31.md`
- score=150 `products/tablet/app/docs/pos/PRISMA_TABLET_SELL_CHECKOUT_PAYMENT_FLOW_04A.md`
- score=150 `products/tablet/app/docs/qa/pos-checkout-02/acceptance.md`
- score=150 `products/tablet/app/docs/qa/pos-checkout-02/smoke-tests.md`
- score=130 `products/tablet/app/components/checkout/checkout-cash-calculator.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-payment-methods.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-screen.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-summary-card.tsx`
- score=130 `products/tablet/app/components/checkout/checkout-summary.tsx`
- score=130 `products/tablet/app/components/checkout/payment-method-selector.tsx`
- score=130 `products/tablet/app/components/checkout/ticket-confirmation.tsx`
- score=130 `products/tablet/app/components/pos/pos-cobro-surface.tsx`
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
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-cart-panel.tsx`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-category-rail.tsx`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-data.ts`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-icons.tsx`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-shell.tsx`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-product-card.tsx`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-product-grid.tsx`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-route-ui.tsx`

## GovMesh3 escalation

- Also obey `VISUAL_EXPLOITATION_CONTRACT.md`.
- Also obey `APP_CAPABILITY_REQUIREMENTS.json` / `.md`.
- Also obey `SCREEN_VISUAL_STACK_PLAN.md`.
- Also obey `PREMIUM_ACCEPTANCE_BAR.md`.
- Result packages must complete `USED_REJECTED_REQUIREMENT.md`.
