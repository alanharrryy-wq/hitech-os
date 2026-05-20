# Runbook: Tablet to PC Sync Closure

## Safe order

1. Run installer dry-run.
2. Review generated plan and logs under F:\descargasf.
3. Run existing verify commands.
4. Apply only after dry-run is clean.
5. Run installer verify.
6. Run all pnpm gates.
7. Run the golden runtime test with PC unavailable, then PC available.

## PC offline behavior

PC offline must not block Tablet checkout. Dispatcher records retry metadata and schedules next attempt. Operators may continue selling locally.

## Rollback

Use installer rollback mode. File rollback restores patched files from backup or removes files created by this patch. Database migration rollback is not automatic; do not apply DB migration without a database backup and duplicate preflight.
