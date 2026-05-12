# PRISMA Chart Lab Cloudflare Pages

Chart Lab can be exported as a static, public-safe Cloudflare Pages preview.

## Project

- Pages project: `prisma-chart-lab`
- App root: `F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app`
- Output directory: `F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\out`
- Config: `F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app\wrangler.jsonc`

## Build

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:build
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify:no-leaks
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:verify
```

The Cloudflare build forces public-safe mode and static export.

## Deploy

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system\products\chart-lab\app" exec wrangler login
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:cf:deploy
```

No deploy should be claimed until `wrangler whoami`, the deploy command, and an HTTP smoke for the returned URL pass.

## Public Safety

Pages deploys must stay mock/demo only. Do not expose private diagnostics, local filesystem paths, env values, tokens, database URLs, or production-origin bindings.
