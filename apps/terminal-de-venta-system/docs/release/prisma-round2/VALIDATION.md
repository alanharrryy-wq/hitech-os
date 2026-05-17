# Validation

Run from:

`F:\repos\hitech-os\apps\terminal-de-venta-system`

## Prisma

```powershell
$env:DATABASE_URL="file:./tools/_local/tmp/prisma-round2-local.db"
npx prisma validate --schema prisma/schema.prisma
```

```powershell
$env:DATABASE_URL="file:./prisma-round2-local.db"
npx prisma validate --schema products/tablet/app/prisma/schema.prisma
```

```powershell
Set-Location F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app
$env:DATABASE_URL="file:./prisma-round2-local.db"
npx prisma validate --schema ./prisma/schema.prisma
npx prisma generate --schema ./prisma/schema.prisma
```

```powershell
Set-Location F:\repos\hitech-os\apps\terminal-de-venta-system\products\tablet\app
$env:DATABASE_URL="file:./prisma-round2-local.db"
$env:TABLET_DATABASE_URL="file:./prisma-round2-local.db"
npx prisma generate --schema ./prisma/schema.prisma
```

## App Gates

```powershell
pnpm -C products/tablet/app run typecheck
pnpm -C products/tablet/app run build
pnpm -C products/pc/app run typecheck
pnpm -C products/pc/app run build
pnpm -C products/mobile/app run typecheck
pnpm -C products/mobile/app run build
```

No `lint` or `test` script exists in these three app package files at the time of this report.

## Product Integrity

```powershell
pnpm run verify:product-integrity
```

Expected:

- active workspace packages are locked
- `products/web/app` is preserved off-release
- generated artifacts stay out of source lanes
- local DB and generated Prisma Client output are not tracked
- active `next-env.d.ts` files do not drift
- Round 2 gates remain wired
- PC schema remains build-local and non-canonical

## QA Readonly

```powershell
python tools/qa/prisma_round2_readonly_audit.py --repo-root . --out-dir tools/codex/runs/prisma-round2-productization/qa --format markdown all
```

Expected:

- PASS: 17
- WARN: 0
- FAIL: 0

## Smoke

```powershell
pnpm run verify:round2
```

Expected:

- shared sync contract passes
- Tablet standalone sale core passes
- Tablet catalog/stock/POS smoke matrix passes
- Tablet offline/outbox smoke matrix passes
- Tablet shift/cash route smoke matrix passes
- Tablet contextual export smoke matrix passes
- PC backoffice source route smoke passes
- Mobile supervisor release boundary passes
