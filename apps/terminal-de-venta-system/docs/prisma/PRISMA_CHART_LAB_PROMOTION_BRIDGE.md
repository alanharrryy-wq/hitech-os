# PRISMA Chart Promotion Bridge

The promotion system is named **Chart Promotion Bridge**.

## Dry Run

```powershell
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:promote -- --chart=pc.causal-flow-ribbon --target=pc --dry-run
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:promote -- --chart=tablet.shift-pulse-strip --target=tablet --dry-run
pnpm -C "F:\repos\hitech-os\apps\terminal-de-venta-system" chart-lab:promote -- --chart=mobile.owner-pulse-timeline --target=mobile --dry-run
```

Dry-run writes a manifest under `F:\repos\hitech-os\apps\terminal-de-venta-system\tools\_local\evidence\chart-lab`.

## Apply Policy

Apply is intentionally blocked by default until an operator approves the exact target wrapper and feature flag path. This keeps PC, Tablet, Mobile, and Web product laws intact.

If apply is later enabled, it must create a backup under `tools/_local/backups/chart-promotion`, keep feature flags off, write only allowed files, and run target validation.
