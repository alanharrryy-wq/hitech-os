# PRISMA Chart Lab Public-Safe Mode

Public-safe mode turns the Lab into a mock/demo-only Cloudflare preview.

## Environment

```powershell
$env:PRISMA_CHART_LAB_PUBLIC_SAFE = "true"
$env:NEXT_PUBLIC_PRISMA_CHART_LAB_PUBLIC_SAFE = "true"
$env:NEXT_PUBLIC_PRISMA_CHART_LAB_DEPLOYMENT_MODE = "cloudflare-pages"
```

`chart-lab:cf:build` sets these automatically.

## Public-Safe Rules

- no private diagnostics;
- no env values;
- no tokens;
- no database URL values;
- no local filesystem diagnostics;
- no production-origin reuse;
- mock/demo badge visible;
- fallback data never labeled as real.

## Verification

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:verify:no-leaks
```
