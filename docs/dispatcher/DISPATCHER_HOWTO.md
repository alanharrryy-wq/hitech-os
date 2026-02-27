# HITECH-OS Dispatcher HowTo

## Purpose

This guide explains how to run and validate dispatcher behavior with pinned `RUN_ID`, strict mode checks, and manual fallback handling.

## Prerequisites

- Repository root available locally.
- AutoHotkey v2 installed and resolvable (for example via `FACTORY_AHK_EXE`).
- Prompt artifacts exist for the target run in `tools/codex/prompts/<RUN_ID>/`.

## Auto Mode (Factory run)

Create or run a factory dispatch flow through `run_iter.ps1`.

Run with auto-generated run id:

```powershell
pwsh -NoProfile -File tools/codex/dispatch/run_iter.ps1 -PromptsPackPath .\PROMPTS_PACK_TEST.txt
```

Run with explicit `RUN_ID`:

```powershell
pwsh -NoProfile -File tools/codex/dispatch/run_iter.ps1 -RunId 20260227_2 -PromptsPackPath .\PROMPTS_PACK_TEST.txt
```

## Manual Mode (Pinned RUN_ID)

Dispatch workers directly for a specific run id:

```powershell
python -m tools.codex.dispatch.dispatch_prompts `
  --run-id 20260227_2 `
  --workers A_core,B_tooling,C_features,D_validation `
  --ahk-exe "C:\Users\alanh\AppData\Local\Programs\AutoHotkey\v2\AutoHotkey64.exe"
```

Single-worker smoke:

```powershell
python -m tools.codex.dispatch.dispatch_prompts `
  --run-id 20260227_2 `
  --workers A_core `
  --ahk-exe "C:\Users\alanh\AppData\Local\Programs\AutoHotkey\v2\AutoHotkey64.exe"
```

## Run Pinning + Strict Mode

Pin test analysis to a run:

```powershell
$env:HOS_RUN_ID = "20260227_2"
```

Enable strict result validation for A/B/C/D:

```powershell
$env:HOS_STRICT = "1"
```

Run hardening tests:

```powershell
Invoke-Pester -Path tools/tests/dispatch-hardening/DispatchHardening.Tests.ps1 -Output Detailed
```

Or use wrapper:

```powershell
pwsh -NoProfile -File tools/tests/dispatch-hardening/Generate_DispatchHardening_Test.ps1
```

Generate files only (skip test run):

```powershell
$env:HOS_NO_RUN = "1"
pwsh -NoProfile -File tools/tests/dispatch-hardening/Generate_DispatchHardening_Test.ps1
```

## Where Logs Live

Primary run logs:

- `tools/codex/runs/<RUN_ID>/_debug/AHK_DISPATCH.log`
- `tools/codex/runs/<RUN_ID>/_debug/AHK_WORKER_RESULTS.log`
- `tools/codex/runs/<RUN_ID>/_debug/DISPATCH_HEARTBEAT.json`
- `tools/codex/prompts/<RUN_ID>/logs/AHK_STDOUT.log`
- `tools/codex/prompts/<RUN_ID>/logs/AHK_STDERR.log`

## How to Interpret PASS/FAIL

- `detect_new_hwnd FAIL + new_hwnd_timeout` is acceptable if both fallbacks are logged afterward.
- Each timeout occurrence must be followed by:
  - `fallback_title_scan`
  - `fallback_recent_code_window`
- Guarded keystroke steps should end with `|true`:
  - `open_codex_sidebar`
  - `paste_prompt`
  - `submit_prompt`
- Submission must remain `single_enter_submission`.
- Worker results must not duplicate per worker.
- With `HOS_STRICT=1`, results must include exactly one line for each of:
  - `A_core`, `B_tooling`, `C_features`, `D_validation`.

## Troubleshooting Checklist

1. Confirm `AHK_DISPATCH.log` and `AHK_WORKER_RESULTS.log` exist under `_debug`.
2. Search for `new_hwnd_timeout` and ensure both fallback steps are present after each timeout.
3. Confirm the final log field is `true` for guarded keystroke action lines.
4. Confirm `submit_prompt` detail includes `single_enter_submission`.
5. Confirm no duplicate worker lines in results log.
6. If strict mode is enabled, confirm A/B/C/D each has exactly one result line.
7. Check `AHK_STDERR.log` and `AHK_STDOUT.log` for script runtime errors.
8. Verify target VS Code windows contain expected worktree/run hints in title when possible.

## Manual Fallback Procedure (Operator)

If auto window selection still appears wrong:

1. Bring the intended VS Code window to foreground manually.
2. Confirm it is a real Code window (not browser) by title/process.
3. Re-run dispatcher for the same `RUN_ID` in manual mode.
4. Immediately inspect `AHK_DISPATCH.log`:
   - Ensure timeout fallback steps were logged.
   - Ensure guarded action lines end with `|true`.
5. Verify `AHK_WORKER_RESULTS.log` contains one result line per attempted worker.
6. If strict mode is required, set `HOS_STRICT=1` and rerun validation tests.
