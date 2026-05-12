# PRISMA Chart Lab Handoff Pack

The handoff packer creates a complete Chart Lab context ZIP without secrets or build outputs.

## Command

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:handoff:pack
```

## Includes

- Chart Lab app, app route, src, scripts, deploy templates, docs.
- PRISMA chart docs.
- Shared chart contracts, mocks, adapters, recipes, state gallery, passports.
- Cloudflare Pages and Tunnel configuration.
- Promotion bridge script and manifests.
- Hash manifest.

## Excludes

- `node_modules`
- `.next`
- `out`
- `.env*`
- build outputs
- secrets
