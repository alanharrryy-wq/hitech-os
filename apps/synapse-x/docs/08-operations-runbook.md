# Operations Runbook

## Main Operations
- ingest now
- full ingest
- repair
- watch on
- watch off

## Expected Safety
All operations should be idempotent where possible.

## Repair Includes
- DB integrity checks
- index rebuild
- cache/DB reconciliation
- retry failed files
- raw reference validation

## Logging
Every operational action should produce clear logs and diagnostics.
