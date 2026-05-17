# Removal Summary

Status: GO

Branch: `fix/remove-scene-studio-blocker`

Commit: `3f39219b`

PR: `https://github.com/alanharrryy-wq/hitech-os/pull/72`

Decision:

Scene Studio / Pitch was removed from active scope by route/API stubbing and validation isolation. No broad Scene Studio repair was performed.

## What changed

- Scene Studio nav entry removed from Keystone shell.
- `/dev/scene-studio` now returns Next `notFound()`.
- `/api/scene-studio/run` now returns `410 Gone`.
- `/pitch` and Pitch subroutes now return Next `notFound()`.
- Keystone TypeScript excludes off-scope Scene Studio/Pitch/DevConsole/test surfaces.
- Keystone Vitest excludes off-scope Scene Studio/Pitch/DevConsole/test surfaces.
- Root `ci` no longer invokes Scene Studio proof.

## What did not change

- No PRISMA runtime files were edited.
- No PRISMA schema files were edited by this branch.
- Tablet-first operation was not changed.
- PC and Mobile remain adders only.
- No dependency or lockfile changes were introduced.
- No source files were deleted.
- No quarantine move was needed.

## Restore instructions

If Scene Studio/Pitch must return later:

1. Revert commit `fix(repo): remove scene studio from active scope`.
2. Repair Scene Studio/Pitch contracts in a dedicated Keystone PR.
3. Re-enable route/API/typecheck/test scope only after `pnpm -C apps\keystone run typecheck`, `pnpm -C apps\keystone run build`, and `pnpm -C apps\keystone run test` pass.
