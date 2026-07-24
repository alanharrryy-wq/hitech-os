# PRISMA Screen Visual Stack Plan

- Task: `RIFAT centralizar toda la autoridad visual operativa de PRISMA en prisma-html, generar runtime visual canónico Tablet, migrar todas las rutas visuales Tablet, retirar estilos legacy y certificar cero downgrades`

## Required order

- Read Authority Mesh files and Field Manual.
- Identify exact target screen from Atlas/docs/repo evidence; do not guess.
- Apply app capability requirements and Visual Exploitation Contract.
- Select minimal safe mutation set.
- Implement using must_use/should_use capabilities unless blocked with evidence.
- Fill used/rejected capability matrix in result package.
- Validate without process/port/dev-server/Prisma-hot manipulation.

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
- score=80 `products/tablet/app/components/pos/pos-ticket-panel.tsx`
- score=80 `products/tablet/app/components/pos/terminal-v2/index.ts`
- score=80 `products/tablet/app/components/pos/terminal-v2/pos-command-dock.tsx`
- score=80 `products/tablet/app/components/pos/terminal-v2/pos-product-canvas.tsx`
- score=80 `products/tablet/app/components/pos/terminal-v2/pos-terminal-header.tsx`
- score=80 `products/tablet/app/components/pos/terminal-v2/pos-terminal-surface.tsx`
- score=80 `products/tablet/app/components/pos/terminal-v2/pos-ticket-rail.tsx`
- score=80 `products/tablet/app/components/pos/use-prisma-packshot-skin.ts`
- score=80 `products/tablet/app/components/premium-visual/TabletPremiumRuntimeEffects.tsx`
- score=80 `products/tablet/app/components/premium-visual/TabletPremiumSurfaces.tsx`
- score=80 `products/tablet/app/components/premium-visual/index.ts`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-cart-panel.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-category-rail.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-data.ts`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-icons.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-shell.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-product-card.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-product-grid.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-route-ui.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-search-row.tsx`

## Focus

- primary_app: `tablet`
- screen_type: `general`
- signals: `[]`
- premium_requested: `True`
- operational_surface: `False`
