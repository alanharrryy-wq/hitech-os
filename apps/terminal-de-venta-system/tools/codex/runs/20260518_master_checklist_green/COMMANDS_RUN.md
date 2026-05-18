# Commands Run

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `$env:DATABASE_URL='file:F:/repos/hitech-os/apps/terminal-de-venta-system/tools/_local/tmp/master_checklist_root_validate.db'; pnpm exec prisma validate --schema prisma/schema.prisma`
- Evidence: The schema at prisma\schema.prisma is valid

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `$env:DATABASE_URL='file:F:/repos/hitech-os/apps/terminal-de-venta-system/tools/_local/tmp/master_checklist_tablet_validate.db'; pnpm exec prisma validate --schema products/tablet/app/prisma/schema.prisma`
- Evidence: The schema at products\tablet\app\prisma\schema.prisma is valid

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm run verify:outbox-integrity`
- Evidence: F:\descargasf\OUTBOX_INTEGRITY_REPORT_20260518_171007.md

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm run verify:sync-health`
- Evidence: F:\descargasf\SYNC_HEALTH_REPORT_20260518_171007.md

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm -C products/tablet/app run verify:tablet-sale-flow`
- Evidence: PRISMA_TABLET_STANDALONE_CORE_CLOSEOUT_02 passed with pcRequiredForBasicSale=false and sync metadata assertions

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm run verify:tablet-sync-dispatcher`
- Evidence: PRISMA_TABLET_SYNC_DISPATCHER_01 passed

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm run verify:sync-closure-truth`
- Evidence: PRISMA_SYNC_CLOSURE_TRUTH passed

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm run verify:no-fake-green`
- Evidence: PRISMA_NO_FAKE_GREEN passed

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm run verify:ack-required`
- Evidence: PRISMA_ACK_REQUIRED passed

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm run verify:pc-ingest-idempotency`
- Evidence: PRISMA_PC_INGEST_IDEMPOTENCY_01 passed

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `pnpm run verify:mobile-sync-visibility`
- Evidence: PRISMA_MOBILE_SYNC_VISIBILITY_01 passed

## PASS exit 0

- CWD: `F:\repos\hitech-os\apps\terminal-de-venta-system`
- Command: `python sqlite3 read-only DB evidence check`
- Evidence: F:\repos\hitech-os\apps\terminal-de-venta-system\tools\codex\runs\20260518_master_checklist_green\DB_EVIDENCE.json

## PASS exit 0

- CWD: `F:\repos\hitech-os`
- Command: `git diff --check -- apps/terminal-de-venta-system/products/tablet/app/tools/verify_tablet_standalone_core_closeout_02.mjs`
- Evidence: exit 0; CRLF warning only
