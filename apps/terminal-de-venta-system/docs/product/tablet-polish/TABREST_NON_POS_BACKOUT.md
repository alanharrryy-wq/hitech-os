# TABREST_NON_POS Backout

Date: 2026-07-02

## Scope

Back out only the files listed in `TABREST_NON_POS_CHANGED_FILES.md`. Do not run destructive repo-wide cleanup.

## Preferred Backout After Commit

If these changes are committed later as a single commit, revert that commit with a normal Git revert.

## Preferred Backout Before Commit

If still uncommitted, manually reverse the changes in the listed files or apply a reviewed reverse patch for this exact file set.

## Safety Notes

- Do not use `git reset --hard`.
- Do not use `git clean`.
- Do not force push.
- Preserve unrelated user changes if the worktree has moved on.

## Validation After Backout

- Run `pnpm run verify:zero-important` from `apps/terminal-de-venta-system/products/tablet/app`.
- Run the narrow affected Tablet checks that match the backed-out slice.
- Re-run `git diff --check`.
