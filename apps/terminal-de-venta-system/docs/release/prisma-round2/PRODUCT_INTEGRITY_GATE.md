# PRISMA Round 2.1 Product Integrity Gate

Product root:

`F:\repos\hitech-os\apps\terminal-de-venta-system`

## Purpose

This gate turns Round 2 honest notes into a repeatable product contract.

It is not a demo gate. It does not start servers, does not modify visual baselines, does not add dependencies, and does not promote experimental lanes.

## Command

```powershell
pnpm run verify:product-integrity
```

Optional report location:

```powershell
pnpm run verify:product-integrity -- --out-dir tools/codex/runs/prisma-round2-product-integrity
```

## Checks

The gate verifies:

- Active pnpm workspace packages exist.
- Active workspace packages have lockfile importers.
- Active workspace packages do not use floating `latest` or `*` dependency versions.
- `products/web/app` remains preserved but off-release until approved.
- No generated artifact directories exist in source lanes.
- No local DB files are tracked.
- No generated Prisma Client output is tracked.
- Active Next.js `next-env.d.ts` files did not drift.
- Round 2 gates remain wired.
- PC schema remains build-local and non-canonical.
- Release lane docs exist.
- Scoped Round 2/Product Integrity diff is whitespace-clean.

## GO Criteria

All checks must pass.

`products/web/app` can exist locally, but it must not be active in `pnpm-workspace.yaml` until promoted with exact versions and lockfile evidence.

## NO-GO Criteria

The gate fails if:

- An active workspace package lacks a lockfile importer.
- An active workspace package uses floating dependency versions.
- Generated build/cache output is found in source lanes.
- Local DB files are tracked.
- Prisma generated client output is tracked.
- Active `next-env.d.ts` files drift.
- PC schema loses its non-canonical header.
- Round 2 validation scripts are disconnected.

## Relationship To Round 2

Run this gate before the existing Round 2 product gate:

```powershell
pnpm run verify:product-integrity
pnpm run verify:round2
```

The first command proves repository integrity. The second proves product behavior and architecture boundaries.
