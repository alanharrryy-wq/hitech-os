# PRISMA Screen Visual Stack Plan

- Task: `Construir y certificar PRISMA Support Resolver Operational Cockpit y modernizar todas las superficies afectadas del Prisma Cloud Command Center 3160, fusionando old + new, actualizando motores, adapters, contratos, endpoints y stores, garantizando consistencia multidispositivo, coherencia de licencias, datos sincronizados entre PC, Tablet, Mobile y 3160, y simplificando todas las operaciones de licencias sin regresiones.`

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
- score=110 `products/mobile/app/src/lib/prisma-app/mobile-data-plane/pc-adapter.ts`
- score=110 `products/pc/app/app/api/backoffice/sync/export-pc-to-tablet/route.ts`
- score=110 `products/pc/app/app/api/backoffice/sync/project-tablet-to-pc/route.ts`
- score=110 `products/pc/app/app/api/backoffice/tablet-communication/governance-command/route.ts`
- score=110 `products/pc/app/app/api/backoffice/tablet-communication/route.ts`
- score=110 `products/pc/app/app/api/charts/pc/tablet-catalog-freshness-grid/route.ts`
- score=110 `products/pc/app/app/tablet-communication/error.tsx`
- score=110 `products/pc/app/app/tablet-communication/loading.tsx`
- score=110 `products/pc/app/app/tablet-communication/page.tsx`
- score=110 `products/pc/app/src/composition/module-registry.ts`
- score=110 `products/pc/app/src/composition/navigation.ts`
- score=110 `products/pc/app/src/composition/twin-capabilities.ts`
- score=110 `products/pc/app/src/lib/suppliers/in-memory-repository.ts`
- score=110 `products/pc/app/src/lib/suppliers/repository-contract.ts`
- score=110 `products/pc/app/src/server/repositories/audit-repository.prisma.ts`
- score=110 `products/pc/app/src/server/repositories/barcode-repository.prisma.ts`
- score=110 `products/pc/app/src/server/repositories/catalog.repository.ts`
- score=110 `products/pc/app/src/server/repositories/inventory.repository.ts`

## Focus

- primary_app: `tablet`
- screen_type: `dashboard`
- signals: `['pos', 'kpi']`
- premium_requested: `True`
- operational_surface: `True`
