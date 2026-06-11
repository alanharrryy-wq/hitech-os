# Plawright Mamastrophic

Centralized PRISMA Playwright Surfaces motor.

## Central root

`F:\repos\hitech-os\tools\Plawright Mamastrophic`

## Main files

| Role | Path |
|---|---|
| Launcher | `F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1` |
| Core wrapper | `F:\repos\hitech-os\tools\Plawright Mamastrophic\core\run-surf8-capture.ps1` |
| Discovery engine | `F:\repos\hitech-os\tools\Plawright Mamastrophic\core\surf8_discovery.py` |
| Central capture engine | `F:\repos\hitech-os\tools\Plawright Mamastrophic\tests\surf8.all-surfaces.engine.cjs` |
| PC Playwright entry bridge | `F:\repos\hitech-os\apps\terminal-de-venta-system\products\pc\app\tests\prisma-surfaces\surf8.all-surfaces.spec.cjs` |

## arr5 fixes

- Adds governed GPU modes: `-GpuMode off|auto|on`.
- Keeps `off` as the reproducible default.
- Writes `gpu-profile.json`, `gpu-profile.md`, and `gpu-runtime.json` into the result ZIP.
- Names GPU comparison runs with `gpu-auto` / `gpu-on` in the result stem.

## arr4 fixes

- Adds `-Surface` selection without returning to the old `F:\PRISMA_CTX` motor.
- Supports aliases/ports: `pc/3130`, `tablet/3120`, `mobile/app/3140`, `web/3110`, `chart-lab/3000`, `control-center/3150`, `all`.
- Makes the final status honest:
  - `PASS`: all selected online targets captured with zero skipped/fail/missing.
  - `PARTIAL_PASS`: no real failures/missing records, but at least one selected macro/port was offline and got skipped.
  - `FAIL`: real capture failure, missing target record, Playwright crash, or zero records.
- Keeps `-Strict` for old red-gate behavior when skipped targets must fail the run.
- Discovery reports now include macro summaries, selected targets, filtered routes, dynamic skipped routes, port state and source files.
- Keeps the policy: no process kill, no process start, no DB, no deploy.

## Commands

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode discovery -Surface all
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode quick -Surface pc -Workers 6
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode full -Surface all -Workers 6
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode full -Surface all -Workers 6 -Strict
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode quick -Surface pc -Workers 6 -GpuMode auto
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode quick -Surface pc -Workers 6 -GpuMode on
```


## arr5 fix2 GPU parser repair

- Repairs PowerShell parser failure in `core/run-surf8-capture.ps1` caused by escaped closing quotes in GPU markdown generation.
- Adds installer validation that parses installed PowerShell scripts through Windows PowerShell when available.
- Keeps GPU modes: `off`, `auto`, `on`; default remains `off`.


## arr5 fix2 validator repair

- Fixes the installer validator itself: PowerShell parse validation now runs through a temporary `-File` validator instead of passing target paths with spaces after `-Command`.
- This prevents false install failure on `F:
epos\hitech-os	ools\Plawright Mamastrophic\...`.
- Keeps the arr5 fix1 GPU string repairs and GPU modes `off|auto|on`.
