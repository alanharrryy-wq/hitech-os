# PRISMA Chart Lab

Dedicated visual workshop for PRISMA ECharts operational charts.

The Chart Lab runs independently on port `3000` and is not a production PC, Tablet, Mobile, Web, or Control route. It is a design and validation surface for chart work that can later be promoted through explicit PRISMA product boundaries.

## Local startup

From Windows PowerShell:

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" install
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:dev
```

Open:

```text
http://localhost:3000
```

The lab binds through the package script to `127.0.0.1:3000`.

## Build and validation

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:typecheck
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:build
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify:all
```

`chart-lab:verify` confirms:

- `echarts`, `echarts/core`, `echarts/charts`, `echarts/components`, and `echarts/renderers` resolve from this package.
- the 17 ChartOps charts are registered;
- `Example Future Chart` is registered;
- the lab script binds port `3000`;
- React runtime aliases are not configured.

## Boundaries

- Product apps do not import Chart Lab code.
- Chart Lab can import shared PRISMA chart contracts, mocks, and option builders.
- Mock data is labeled as mock and must not be presented as production truth.
- Promotion into PC, Tablet, Mobile, Web, or Control requires explicit product-surface validation.

## Cloudflare

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:build
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:verify
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:deploy
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:tunnel:doctor
```

Cloudflare builds force public-safe mode and static export to `out`.

## Controls and maps

- Controls: `src/prisma-charts/chart-lab-control-model.ts`
- Control deck: `src/components/ChartControlDeck.tsx`
- Maps: `src/prisma-charts/maps/chart-lab-maps.ts`
- Verifiers: `scripts/verify-chart-lab-*.mjs`

## Promotion

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:promote -- --chart=pc.causal-flow-ribbon --target=pc --dry-run
```

Apply is blocked by default until the exact product wrapper and feature flag are approved.

## Port conflict rule

If port `3000` is busy, stop only a clearly identified previous Chart Lab or dev process. If the owner is unknown, report the process and do not kill it.
