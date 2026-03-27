# Engine Guardian Privileged Activation Runbook

## What is already done
- `git_sentinel_modular` is already applied and validated.
- `engine_guardian` code/runtime/reporting is already applied and validated in non-privileged mode.
- Scheduler contract generation is correct (`AtStartup`, `75s`, `SYSTEM`, `HighestAvailable`, canonical python + canonical CLI path).

## What is blocked only by Windows elevation
- Real registration of `SYSTEM` scheduled tasks fails in non-elevated context with `Register-ScheduledTask: Acceso denegado.`

## Script to run (single privileged phase)
- Script path: `F:\repos\hitech-os\engine_guardian\activate_engine_guardian_privileged.ps1`

## Exact command to run
Run this from an elevated PowerShell session (Run as Administrator):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\engine_guardian\activate_engine_guardian_privileged.ps1"
```

## What success should look like
- `HITECH-EngineGuardian-Boot` exists and is queryable.
- `HITECH-EngineGuardian-Pulse` exists and is queryable.
- Both tasks satisfy:
  - trigger `AtStartup`
  - delay `75 seconds`
  - principal `SYSTEM`
  - run level `HighestAvailable`
  - action uses canonical Python + `F:\repos\hitech-os\engine_guardian\cli.py`
- Legacy cutover runs only after successful scheduler install:
  - legacy tasks exported/backed up first
  - legacy tasks disabled if present
  - no deletion
  - `HITECH-OS-GitSentinel-Guardian` untouched

## Evidence to inspect afterward
All evidence is written under:
- `F:\OneDrive\Descargas\engine_guardian\install`

Primary files from a privileged run:
- `privileged_activation_<timestamp>\activation.log`
- `privileged_activation_<timestamp>\activation_summary.json`
- `privileged_activation_<timestamp>\scheduler_install_latest.json`
- `privileged_activation_<timestamp>\legacy_cloudflare_task_cutover_latest.json` (if cutover executed)
