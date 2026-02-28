# RUN_ID Prompt ZIP System and 5-Codex Dispatcher

## Purpose

Standardize each iteration around one deterministic `RUN_ID` (`YYYYMMDD_N`) used across:

- prompt zip name
- prompt folder name
- factory launch/run-id
- worktree paths
- run output paths
- prompt file contents

## Worker Set (Fixed)

The dispatcher always uses exactly these workers:

- `A_core`
- `B_tooling`
- `C_features`
- `D_validation`
- `Z_aggregator`

## Path Contract

- Prompt zip input: `tools/codex/prompt_zips/<RUN_ID>.zip`
- Extracted prompts: `tools/codex/prompts/<RUN_ID>/`
- Worktrees: `tools/codex/worktrees/<WORKER>`
- Run output: `tools/codex/runs/<RUN_ID>/`
- Dispatcher code: `tools/codex/dispatch/`
- Dispatcher logs/report: `tools/codex/prompts/<RUN_ID>/logs/`

## Required Prompt Files

`tools/codex/prompts/<RUN_ID>/` must contain exactly:

- `A_core_<RUN_ID>.txt`
- `B_tooling_<RUN_ID>.txt`
- `C_features_<RUN_ID>.txt`
- `D_validation_<RUN_ID>.txt`
- `Z_aggregator_<RUN_ID>.txt`

Each prompt file must include near the top:

- `RUN_ID: <RUN_ID>`
- `CODEX_ID: <WORKER>`

Each prompt file must instruct completion marker creation:

- file path: `tools/codex/runs/<RUN_ID>/<WORKER>/DONE.marker`
- content token: `DONE <RUN_ID> <WORKER>`

## One-Command Run

```powershell
powershell -ExecutionPolicy Bypass -File tools/codex/dispatch/run_iter.ps1 -RunId <RUN_ID>
```

## Dispatcher Flow

`tools/codex/dispatch/run_iter.ps1` performs:

1. Validate `RUN_ID` format.
2. Confirm `tools/codex/prompt_zips/<RUN_ID>.zip` exists.
3. Extract zip into `tools/codex/prompts/<RUN_ID>/` if prompt folder was not already present.
4. Validate prompt shape and prompt content contracts.
5. Run `python -m tools.codex.factory launch --run-id <RUN_ID> --workers A_core,B_tooling,C_features,D_validation,Z_aggregator`
6. Run `python -m tools.codex.factory worktrees open --run-id <RUN_ID> --workers ...`
7. Ensure AutoHotkey exists (attempt winget install if needed).
8. Dispatch prompts by UI automation to window titles:
   - `HITECHOS_A_core_<RUN_ID>`
   - `HITECHOS_B_tooling_<RUN_ID>`
   - `HITECHOS_C_features_<RUN_ID>`
   - `HITECHOS_D_validation_<RUN_ID>`
   - `HITECHOS_Z_aggregator_<RUN_ID>`
9. Wait for all 5 `DONE.marker` files.
10. Run `python -m tools.codex.factory bundle-validate --run-id <RUN_ID> --workers ...`
11. Run `python -m tools.codex.factory integrate --run-id <RUN_ID> --workers ...`
12. Write `tools/codex/prompts/<RUN_ID>/logs/DISPATCH_REPORT.md`

## Configuration

Command flags on `run_iter.ps1`:

- `-SendMode enter|ctrl_enter|both`
- `-WindowReadyTimeout <seconds>`
- `-WorkerDoneTimeout <seconds>`
- `-BetweenWorkersDelayMs <milliseconds>`

Environment overrides (`FACTORY_` compatible):

- `FACTORY_SEND_MODE`
- `FACTORY_WINDOW_READY_TIMEOUT`
- `FACTORY_WORKER_DONE_TIMEOUT`
- `FACTORY_BETWEEN_WORKERS_DELAY_MS`
- `FACTORY_DISPATCH__SEND_MODE`
- `FACTORY_DISPATCH__WINDOW_READY_TIMEOUT`
- `FACTORY_DISPATCH__WORKER_DONE_TIMEOUT`
- `FACTORY_DISPATCH__BETWEEN_WORKERS_DELAY_MS`
- `FACTORY_AHK_EXE` (optional explicit AutoHotkey path)
- `FACTORY_DISPATCH__AHK_EXE` (same purpose)

Dispatcher internals also support:

- `FACTORY_WINDOW_MATCH_RETRIES`
- `FACTORY_FOCUS_RETRIES`
- `FACTORY_DISPATCH__WINDOW_MATCH_RETRIES`
- `FACTORY_DISPATCH__FOCUS_RETRIES`

## AutoHotkey Runtime

- Template: `tools/codex/dispatch/ahk_template.ahk`
- Per-run generated script: `tools/codex/prompts/<RUN_ID>/logs/DISPATCH_RUNTIME.ahk`
- Per-run AHK logs:
  - `AHK_DISPATCH.log`
  - `AHK_WORKER_RESULTS.log`
  - `AHK_STDOUT.log`
  - `AHK_STDERR.log`

If AutoHotkey is missing:

- `run_iter.ps1` attempts `winget install --id AutoHotkey.AutoHotkey -e ...`
- If winget is unavailable or install fails, execution is blocked explicitly.

## Validation Rules

Hard fail conditions:

- Missing worker prompt file.
- Prompt filename mismatch with worker set.
- `RUN_ID` mismatch in prompt content.
- `CODEX_ID` mismatch in prompt content.
- Missing or invalid `DONE.marker` token within timeout.
- Any non-zero factory stage (`launch`, `bundle-validate`, `integrate`).
- Meaningful gate fail/block (enforced via `integrate`).

No partial success is reported.

## Stop Conditions and Recovery

Stop conditions:

- Window title cannot be matched within configured retry budget.
- Chat focus cannot be established by automation sequence.
- `DONE.marker` timeout.

Recovery:

1. Fix prompt contract issues and rerun same command.
2. Confirm each window title includes `HITECHOS_<CODEX_ID>_<RUN_ID>`.
3. Increase `-WindowReadyTimeout` and/or window/focus retry env values.
4. Adjust `-SendMode` (`enter`, `ctrl_enter`, `both`) for the local Codex UI behavior.
5. If blocked at validation/integration, inspect run artifacts in `tools/codex/runs/<RUN_ID>/` and rerun.
