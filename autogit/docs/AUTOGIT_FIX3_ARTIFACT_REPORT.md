# AutoGit fix4 artifact hygiene report

## Why this package exists

The fix2 install result was technically PASS, and the installed AutoGit payload passed selftest. However, a repeated run showed the generated `result.zip` could include stale report files from a previous rollback, specifically `ROLLBACK_SUMMARY.json`, because the installer reused the same report folder between runs.

## Fixed in fix4

- Every install run now starts with a clean report folder.
- Every rollback run now starts with a clean rollback report folder.
- Old report folders are moved to `<LOCAL_PATH>`, not permanently deleted.
- Result ZIPs include only the current run's report files.
- Rollback ZIPs include only the current rollback report files.
- The installed AutoGit payload remains the same fixed payload from fix2, plus this documentation note.

## Validation target

Expected install result should contain no stale `ROLLBACK_SUMMARY.json` unless the ZIP is specifically a rollback result ZIP.
