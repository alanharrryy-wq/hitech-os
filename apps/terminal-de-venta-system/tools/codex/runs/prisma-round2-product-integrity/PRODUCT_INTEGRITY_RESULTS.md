# PRISMA Round 2.1 Product Integrity Results

STATUS: GO

PASS: 7
WARN: 1
FAIL: 0

Repo root: F:\repos\hitech-os\apps\terminal-de-venta-system

| Status | Check | Evidence |
| --- | --- | --- |
| PASS | workspace-lockfile - Active workspace packages are resolvable and locked | products/pc/app has package.json<br>products/tablet/app has package.json<br>products/mobile/app has package.json<br>products/chart-lab/app has package.json |
| PASS | web-off-release-lane - products/web/app is preserved outside the active workspace | products/web/app/package.json exists<br>products/web/app is not listed in pnpm-workspace.yaml<br>RELEASE_LANES.md documents the off-release decision |
| WARN | generated-artifacts - Ignored local generated artifact directories are present but not source | products/chart-lab/app/.next is ignored by git and not tracked<br>products/chart-lab/app/out/_next/static/chunks/next/dist is ignored by git and not tracked<br>products/mobile/app/.next is ignored by git and not tracked<br>products/pc/app/.next is ignored by git and not tracked<br>products/tablet/app/.next is ignored by git and not tracked<br>No source contract was changed; local build output should stay uncommitted. |
| PASS | tracked-local-state - No tracked local DB or generated Prisma client output | git ls-files has no .db/.sqlite/.sqlite3 files<br>git ls-files has no generated Prisma client output |
| PASS | next-env-churn - No active Next.js env-file churn | products/tablet/app/next-env.d.ts<br>products/pc/app/next-env.d.ts<br>products/mobile/app/next-env.d.ts<br>products/chart-lab/app/next-env.d.ts |
| PASS | integrity-docs - Release lane and integrity gate docs exist and classify dirty lanes | docs/release/prisma-round2/RELEASE_LANES.md<br>docs/release/prisma-round2/PRODUCT_INTEGRITY_GATE.md |
| PASS | round2-contracts - Round 2 contracts and gates remain wired | verify:round2 present<br>verify:product-integrity present<br>PC schema is marked build-local and non-canonical |
| PASS | scoped-diff-whitespace - Scoped release diff is whitespace-clean | git diff --check passed for Product Integrity and Round 2 release paths |
