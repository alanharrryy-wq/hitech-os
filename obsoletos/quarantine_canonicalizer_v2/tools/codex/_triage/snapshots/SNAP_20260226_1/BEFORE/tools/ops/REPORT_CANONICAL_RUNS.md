# REPORT_CANONICAL_RUNS

## Scope

Validation target: canonical shared runs root governance for tracking/ensure/doctor across worktrees.

- Repo root: `F:/repos/hitech-os`
- Canonical shared runs root: `F:/repos/HITECHOS_SHARED/tools/codex/runs`
- Canonical latest pointer: `F:/repos/HITECHOS_SHARED/tools/codex/runs/LATEST_RUN_ID.txt`

## What Was Failing

1. Tracking run selection was path-leaking through worktree-local junction paths.

- Symptom: `RUN_SUMMARY.json` could report `run_dir` as `F:/repos/<worktree>/tools/codex/runs/<RUN_ID>` depending on caller worktree.

2. `RunsRootOverride` was additive, not authoritative.

- Symptom: even with canonical override intent, tracking still scanned caller repo roots.

3. Empty-candidate/empty-input paths triggered hard parameter-binding errors.

- Symptom: `TRACKING ERROR` messages (for `Candidates`, `BestRun`, `InputPaths`) instead of deterministic BLOCKED output when no run candidates existed in canonical shared root.

## What Was Fixed

1. Enforced canonical shared runs root in official tracking entrypoint when doctor preflight is active.

- File: `tools/codex/tracking/Invoke-HitechTracking.ps1`
- Change: after successful doctor, tracking now forces `RunsRootOverride` to `doctor.drift_scan.shared_runs_root_native`.

2. Made explicit `RunsRootOverride` authoritative in tracking core.

- File: `tools/codex/tracking/Tracking.Commands.ps1`
- Change: when override roots are provided, repo-root discovery is skipped and only override roots are used.

3. Resolved junction-backed runs roots to their junction target.

- File: `tools/codex/tracking/Tracking.Pathing.ps1`
- Change: `Resolve-TrackingRunsRoot` now resolves canonical junction target when possible.

4. Hardened tracking against empty collections/null best run.

- Files:
  - `tools/codex/tracking/Tracking.Commands.ps1`
  - `tools/codex/tracking/Tracking.RunDiscovery.ps1`
  - `tools/codex/tracking/Tracking.Render.ps1`
  - `tools/codex/tracking/Tracking.Artifacts.ps1`
  - `tools/codex/tracking/Tracking.Hashing.ps1`
- Change: allowed empty collections/null where deterministic BLOCKED execution requires graceful handling instead of binding exceptions.

5. Added/extended tests for canonicalization/idempotency/negative governance block.

- File: `tools/codex/tracking/tests/RunsRootCanonicalization.Tests.ps1`
- Includes:
  - canonical run-root resolution across worktrees,
  - idempotency across three worktrees / three ensure invocations,
  - broken-junction doctor/tracking governance block (rc=2) and restoration path.

6. Added operator end-to-end wrapper and deterministic evidence generation.

- File: `tools/ops/Validate-CanonicalRuns.ps1`
- Outputs required evidence pack files under canonical shared run evidence directory.

## Repro Commands

### Run tests

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Pester -Path 'tools/codex/tracking/tests/RunsRootCanonicalization.Tests.ps1' -EnableExit"
```

### Run full validation wrapper

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/ops/Validate-CanonicalRuns.ps1
```

## Evidence Location

- Evidence directory:
  - `F:/repos/HITECHOS_SHARED/tools/codex/runs/__tracking_fallback__/evidence`
- Required evidence files:
  - `worktree_list.porcelain.txt`
  - `ensure_runs_root.json`
  - `doctor_summary.json`
  - `tracking_summary.json`
  - `negative_test_broken_junction.json`
  - `notes.md`
