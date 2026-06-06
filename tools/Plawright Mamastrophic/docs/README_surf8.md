# playmam arr5

Centralized PRISMA Playwright Surfaces runner.

arr4 keeps the Mamastrophic folder as the official motor and restores the ergonomic flow that was missing:

- surface selector via `-Surface`;
- honest `PASS` / `PARTIAL_PASS` / `FAIL` result semantics;
- explicit discovery reports that show selected, filtered and dynamic-skipped targets;
- no process kill, no process start, no DB, no deploy.

## Common usage

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode discovery -Surface all
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode quick -Surface pc -Workers 6
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode full -Surface all -Workers 6
```

If an offline macro is skipped and everything online captures correctly, the run returns `PARTIAL_PASS` and exits `0`. Use `-Strict` only when skipped/offline targets must make the run fail.

## arr5 GPU phases

GPU is optional and governed. The default remains stable:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode quick -Surface pc -Workers 6 -GpuMode off
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode quick -Surface pc -Workers 6 -GpuMode auto
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode quick -Surface pc -Workers 6 -GpuMode on
```

- `off`: reproducible baseline.
- `auto`: safe GPU/WebGL/canvas acceleration attempt with Chromium fallback.
- `on`: aggressive GPU flags; compare after `auto`, especially for Cloudglass/WebGL-heavy routes.

Each run writes GPU evidence under `reports/gpu-profile.*` and `screens/gpu-runtime.json`.


## arr5 fix2 GPU parser repair

This fix repairs the GPU profile markdown string quoting in `core/run-surf8-capture.ps1`.
The bug appeared before Playwright execution, so `-GpuMode off`, `auto`, and `on` all failed at PowerShell parse time.
The installer now validates PowerShell parseability before reporting PASS.


## arr5 fix2 validator repair

- Fixes the installer validator itself: PowerShell parse validation now runs through a temporary `-File` validator instead of passing target paths with spaces after `-Command`.
- This prevents false install failure on `F:epos\hitech-os	ools\Plawright Mamastrophic\...`.
- Keeps the arr5 fix1 GPU string repairs and GPU modes `off|auto|on`.
