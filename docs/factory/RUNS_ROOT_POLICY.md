# Runs Root Policy

## Contract

`tools/codex/runs` is a mandatory junction in every HITECH-OS worktree.

Canonical shared runs root default:

`F:/repos/HITECHOS_SHARED/tools/codex/runs`

Canonical latest pointer:

`<sharedRunsRoot>/LATEST_RUN_ID.txt`

Allowed override precedence:

1. CLI `-SharedRunsRoot`
2. env `HITECH_SHARED_RUNS_ROOT`
3. default path above

## Enforcement

1. `tools/codex/tracking/Invoke-HitechTracking.ps1` runs doctor preflight by default.
2. If drift is detected, tracking exits with rc `2` and writes evidence artifacts.
3. Doctor rc is `0` only when all worktrees are canonical.
4. Ensure defaults to dry-run; repair requires explicit `--write`.
5. Conflict policy is block-by-default. `--force` keeps shared file and archives incoming conflict copy under `<sharedRunsRoot>/conflicts/...`.

Evidence artifacts are always written deterministically (stable key order + newline at EOF):

- `<sharedRunsRoot>/DRIFT_SCAN.json`
- `<sharedRunsRoot>/DRIFT_SCAN.md`
- `<sharedRunsRoot>/REPAIR_REPORT.json`
- `<sharedRunsRoot>/REPAIR_REPORT.md`

## Operator Commands

Doctor:

`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/scripts/Invoke-HitechRunsDoctor.ps1`

Ensure plan (default dry-run):

`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/scripts/Invoke-HitechRunsEnsure.ps1 --dry-run`

Ensure repair:

`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/scripts/Invoke-HitechRunsEnsure.ps1 --write`

## Adding a New Worker Worktree

1. Create/register the worktree with git.
2. Run ensure in write mode once from any worktree:

`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/scripts/Invoke-HitechRunsEnsure.ps1 --write`

3. Confirm doctor returns rc `0`.
4. Do not manually create a standalone `tools/codex/runs` directory inside the new worktree.

## Optional Local Hook

Install optional local git hook helper (off by default):

`pwsh -NoProfile -ExecutionPolicy Bypass -File tools/scripts/Install-HitechHooks.ps1`
