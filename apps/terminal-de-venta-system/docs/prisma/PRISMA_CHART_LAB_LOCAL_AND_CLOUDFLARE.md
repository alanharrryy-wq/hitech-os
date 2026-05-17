# PRISMA Chart Lab Local And Cloudflare Notes

The PRISMA Chart Lab is the canonical local visual workshop for ECharts-based PRISMA operational charts.

## Local origin

```text
http://localhost:3000
http://127.0.0.1:3000
```

## Install and verify

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" install
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify
```

## Start the lab

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:dev
```

The underlying package script binds to `127.0.0.1` and port `3000`.

## Build

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:typecheck
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:build
```

## Port conflict policy

If port `3000` is occupied, stop only a clearly identified previous Chart Lab or dev process. If the process is unknown, report it and do not kill it.

## Cloudflare status

Chart Lab now has governed Cloudflare-ready paths:

- Cloudflare Pages static export: `pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:build`
- Pages verification: `pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:verify`
- Pages deploy: `pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:deploy`
- Tunnel doctor: `pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:tunnel:doctor`
- Tunnel runner: `pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:tunnel:run`

Public exposure remains preview-only, public-safe, and separate from Mobile, Control, EIT, Tablet, and PC origins.

Detailed docs:

- `F:\repos\hitech-os\apps\terminal-de-venta-system\docs\prisma\PRISMA_CHART_LAB_CLOUDFLARE.md`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\docs\prisma\PRISMA_CHART_LAB_TUNNEL.md`
- `F:\repos\hitech-os\apps\terminal-de-venta-system\docs\prisma\PRISMA_CHART_LAB_PUBLIC_SAFE.md`
