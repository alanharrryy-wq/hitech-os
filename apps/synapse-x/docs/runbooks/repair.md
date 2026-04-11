# Runbook Repair

## Goal
Restore consistency after failed or partial state.

## Steps
1. validate DB integrity
2. detect failed files
3. reconcile cache with SQLite
4. rebuild indexes
5. retry failed inputs
6. emit diagnostics
