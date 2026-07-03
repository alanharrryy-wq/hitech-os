# PRISMA Visual Stack Decision

- Task: `Corregir LICFLOW3 Cloudflare licensing routes para que POST /api/licenses/activate, /refresh y /revoke funcionen contra app.hitechrts.com sin downgrades, sin duplicar LICFLOW2, sin tocar secretos, sin copiar DB, sin deploy automático no autorizado y preservando Worker real prisma-cloud-semilla y D1 real prisma_cloud_semilla.`
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

## GovMesh3 escalation

- Also obey `VISUAL_EXPLOITATION_CONTRACT.md`.
- Also obey `APP_CAPABILITY_REQUIREMENTS.json` / `.md`.
- Also obey `SCREEN_VISUAL_STACK_PLAN.md`.
- Also obey `PREMIUM_ACCEPTANCE_BAR.md`.
- Result packages must complete `USED_REJECTED_REQUIREMENT.md`.
