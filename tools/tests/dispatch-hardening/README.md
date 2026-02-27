# Dispatch Hardening Tests

This folder validates dispatcher window-hardening invariants using deterministic log parsing.

## Scope

- Parses `AHK_DISPATCH.log` and `AHK_WORKER_RESULTS.log`.
- Verifies fallback logging after `new_hwnd_timeout`.
- Verifies guarded keystroke markers (`|true`) for:
  - `open_codex_sidebar`
  - `paste_prompt`
  - `submit_prompt`
- Verifies `single_enter_submission`.
- Verifies at-most-one result line per worker.
- In strict mode, requires exactly one result line for `A_core`, `B_tooling`, `C_features`, `D_validation`.

## Environment Variables

- `HOS_RUN_ID`: pin validation to a specific run (for example `20260227_2`).
- `HOS_STRICT=1`: enable strict result-count requirement for A/B/C/D.
- `HOS_NO_RUN=1`: used by wrapper script to generate files without executing Pester.

## Run Tests Directly

```powershell
Invoke-Pester -Path tools/tests/dispatch-hardening/DispatchHardening.Tests.ps1 -Output Detailed
```

Pinned run:

```powershell
$env:HOS_RUN_ID = "20260227_2"
Invoke-Pester -Path tools/tests/dispatch-hardening/DispatchHardening.Tests.ps1 -Output Detailed
```

Strict mode:

```powershell
$env:HOS_RUN_ID = "20260227_2"
$env:HOS_STRICT = "1"
Invoke-Pester -Path tools/tests/dispatch-hardening/DispatchHardening.Tests.ps1 -Output Detailed
```

Use wrapper:

```powershell
pwsh -NoProfile -File tools/tests/dispatch-hardening/Generate_DispatchHardening_Test.ps1
```
