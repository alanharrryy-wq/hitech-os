# Dispatcher Brief — Keystone Pitch Terraform v1

## Canonical Layer IDs (Do Not Invent New IDs)

Source of truth: `packages/ui-kit/src/layers/layerIds.ts`

Stage (global overlays):

- `stage.haze`
- `stage.vignette`
- `stage.noise`
- `stage.scanlines`
- `stage.horizon`
- `frame.bezel`

Cards:

- `card.blur`
- `card.innerStroke`
- `card.specular`
- `card.grain`
- `card.shadowAmbient`

Inset:

- `inset.shadow`

Motion:

- `motion.enabled`

## Pitch Contracts Location

Canonical contracts + fixtures for the pitch module live in:

- `packages/contracts/src/domain/pitch/`

Main exports are re-exported from:

- `packages/contracts/src/index.ts`

## Pitch Pages Location (Keystone)

Canonical routes:

- `apps/keystone/app/pitch/page.tsx`
- `apps/keystone/app/pitch/01-double-engine/page.tsx`
- `apps/keystone/app/pitch/02-industrial-flow/page.tsx`
- `apps/keystone/app/pitch/03-hitech-os/page.tsx`
- `apps/keystone/app/pitch/04-valuation/page.tsx`

Reusable pitch UI modules:

- `apps/keystone/components/pitch/`

## Layer Resolution + Debug Rules

- Resolve layer flags on server with `resolveLayerFlags(searchParams)`.
- Querystring precedence:
  1. `layers=none|all|list`
  2. `layerProfile=neutral|fx|perf`
  3. default `neutral` (all OFF)
- Debug panel must only appear when:
  - `?debug=1`
  - `NODE_ENV !== "production"`

## Smoke Test Commands

From `F:\repos\hitech-os`:

1. `pnpm -r --if-present typecheck`
2. `pnpm -r --if-present lint`
3. `pnpm -r --if-present test`
4. `pnpm -r --if-present build`

Keystone-only smoke test loop:

- `pnpm --filter @hitech/keystone test`
- `pnpm --filter @hitech/keystone build`
