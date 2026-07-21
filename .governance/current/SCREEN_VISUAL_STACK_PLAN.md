# PRISMA Screen Visual Stack Plan

- Task: `PC96FLOW functional data completion in PC and Tablet with shared kernel, local database schema and additive migrations, durable sync, audit, idempotency, ACK/checkpoint/conflict and quality verification. Resolve canonical owner chains for command center, sales, cash, catalog, pricing, inventory, purchasing, customers, security, organization devices, sync and licensing readiness. Complete the corresponding Tablet POS, checkout, catalog, inventory, sales, returns, shift, offline sync, settings and setup routes. Preserve unrelated current Tablet stylesheet changes.`

## Required order

- Read Authority Mesh files and Field Manual.
- Identify exact target screen from Atlas/docs/repo evidence; do not guess.
- Apply app capability requirements and Visual Exploitation Contract.
- Select minimal safe mutation set.
- Implement using must_use/should_use capabilities unless blocked with evidence.
- Fill used/rejected capability matrix in result package.
- Validate without process/port/dev-server/Prisma-hot manipulation.

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
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-search-row.tsx`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-sidebar.tsx`
- score=130 `products/tablet/app/components/prisma-dark-pos/prisma-top-action-bar.tsx`
- score=130 `products/tablet/app/components/tablet-pos/touch-pos-ui.tsx`
- score=120 `products/tablet/app/components/checkout/checkout.module.css`
- score=120 `products/tablet/app/components/pos/pos-cobro-surface.module.css`
- score=120 `products/tablet/app/components/pos/pos.module.css`
- score=120 `products/tablet/app/components/pos/pos.visual.presets.json`
- score=120 `products/tablet/app/components/pos/pos.visual.schema.json`
- score=120 `products/tablet/app/components/pos/pos.visual.tokens.css`
- score=120 `products/tablet/app/components/pos/pos.visual.tokens.generated.css`
- score=120 `products/tablet/app/components/pos/pos.visual.tokens.json`
- score=120 `products/tablet/app/components/pos/terminal-v2/pos-terminal-surface.module.css`
- score=120 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos.module.css`
- score=120 `products/tablet/app/components/tablet-pos/touch-pos.module.css`
- score=110 `products/pc/app/app/api/backoffice/sync/export-pc-to-tablet/route.ts`
- score=110 `products/pc/app/app/api/backoffice/sync/project-tablet-to-pc/route.ts`
- score=110 `products/pc/app/app/api/backoffice/tablet-communication/governance-command/route.ts`
- score=110 `products/pc/app/app/api/backoffice/tablet-communication/route.ts`
- score=110 `products/pc/app/app/api/charts/pc/tablet-catalog-freshness-grid/route.ts`

## Focus

- primary_app: `tablet`
- screen_type: `tablet_pos_sell`
- signals: `['pos', 'checkout']`
- premium_requested: `False`
- operational_surface: `True`
