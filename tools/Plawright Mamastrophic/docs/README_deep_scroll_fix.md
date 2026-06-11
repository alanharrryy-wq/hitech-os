# PRISMA Plawright Mamastrophic deep-scroll fix

This package replaces the whole `Plawright Mamastrophic` tool folder with complete files, not patches/diffs.

## What changed

- `MENU.ps1` now resolves its own folder through `$PSScriptRoot`, so it no longer jumps to a stale hardcoded install by accident.
- `RUN.ps1` and `core/run-surf8-capture.ps1` expose `DeepScroll auto/on/off`.
- `DeepScroll auto` is ON by default when screenshots are enabled.
- `FullPage` becomes effective automatically when deep capture is enabled.
- All regular Surf8 and VisualQA specs now run from the tool folder, not from a stale PC app wrapper.
- Screenshots now include:
  - legacy screenshot path for compatibility;
  - viewport screenshot;
  - fullpage screenshot;
  - page scroll tiles;
  - detected internal scroll-container tiles;
  - per-target `scrollCoverage` metadata.
- Capture manifests now recurse into screenshot subfolders and fail the run if scroll coverage is partial or failed. No fake green.
- VisualQA summary now includes scroll-coverage counts and route-level screenshot coverage fields.

## Runtime policy preserved

- no start
- no kill
- no DB
- no deploy
- no process/port cleanup

## Useful direct command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode visualqa -Surface all -Workers 6 -AllowPartial -DeepScroll auto -SurfaceParallel auto
```

## Escape hatch

For a fast viewport-only smoke, explicitly disable deep scroll:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "F:\repos\hitech-os\tools\Plawright Mamastrophic\RUN.ps1" -Mode quick -Surface pc -Workers 2 -DeepScroll off
```
