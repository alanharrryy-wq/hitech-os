# PRISMA Screen Visual Stack Plan

- Task: `Corregir LICFLOW3 Cloudflare licensing routes para que POST /api/licenses/activate, /refresh y /revoke funcionen contra app.hitechrts.com sin downgrades, sin duplicar LICFLOW2, sin tocar secretos, sin copiar DB, sin deploy automático no autorizado y preservando Worker real prisma-cloud-semilla y D1 real prisma_cloud_semilla.`

## Required order

- Read Authority Mesh files and Field Manual.
- Identify exact target screen from Atlas/docs/repo evidence; do not guess.
- Apply app capability requirements and Visual Exploitation Contract.
- Select minimal safe mutation set.
- Implement using must_use/should_use capabilities unless blocked with evidence.
- Fill used/rejected capability matrix in result package.
- Validate without process/port/dev-server/Prisma-hot manipulation.

## Candidate target files

- score=80 `products/tablet/app/components/pos/pos-cobro-surface.tsx`
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
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-cart-panel.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-category-rail.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-data.ts`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-icons.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos-shell.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-product-card.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-product-grid.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-route-ui.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-search-row.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-sidebar.tsx`
- score=80 `products/tablet/app/components/prisma-dark-pos/prisma-top-action-bar.tsx`
- score=80 `products/tablet/app/components/tablet-pos/touch-pos-ui.tsx`
- score=70 `products/tablet/app/components/pos/pos-cobro-surface.module.css`
- score=70 `products/tablet/app/components/pos/pos.module.css`
- score=70 `products/tablet/app/components/pos/pos.visual.presets.json`
- score=70 `products/tablet/app/components/pos/pos.visual.schema.json`
- score=70 `products/tablet/app/components/pos/pos.visual.tokens.css`
- score=70 `products/tablet/app/components/pos/pos.visual.tokens.generated.css`
- score=70 `products/tablet/app/components/pos/pos.visual.tokens.json`
- score=70 `products/tablet/app/components/pos/terminal-v2/pos-terminal-surface.module.css`
- score=70 `products/tablet/app/components/prisma-dark-pos/prisma-dark-pos.module.css`
- score=70 `products/tablet/app/components/tablet-pos/touch-pos.module.css`
- score=60 `products/tablet/app/app/api/pos/admin/local-users/route.ts`
- score=60 `products/tablet/app/app/api/pos/admin/sales-reset/route.ts`
- score=60 `products/tablet/app/app/api/pos/catalog/import/route.ts`
- score=60 `products/tablet/app/app/api/pos/catalog/products/route.ts`
- score=60 `products/tablet/app/app/api/pos/catalog/resolve/route.ts`
- score=60 `products/tablet/app/app/api/pos/events/outbox/route.ts`
- score=60 `products/tablet/app/app/api/pos/events/recent/route.ts`
- score=60 `products/tablet/app/app/api/pos/export/contextual/route.ts`
- score=60 `products/tablet/app/app/api/pos/export/events/route.ts`
- score=60 `products/tablet/app/app/api/pos/export/inventory-movements/route.ts`
- score=60 `products/tablet/app/app/api/pos/export/sales-today/route.ts`
- score=60 `products/tablet/app/app/api/pos/inventory/low-stock/route.ts`
- score=60 `products/tablet/app/app/api/pos/inventory/movements/recent/route.ts`
- score=60 `products/tablet/app/app/api/pos/offline/audit/route.ts`
- score=60 `products/tablet/app/app/api/pos/products/barcodes/validate/route.ts`
- score=60 `products/tablet/app/app/api/pos/products/create/route.ts`
- score=60 `products/tablet/app/app/api/pos/products/resolve/route.ts`
- score=60 `products/tablet/app/app/api/pos/products/search/route.ts`
- score=60 `products/tablet/app/app/api/pos/products/update/route.ts`

## Focus

- primary_app: `tablet`
- screen_type: `tablet_pos_sell`
- signals: `['pos']`
- premium_requested: `False`
- operational_surface: `True`
