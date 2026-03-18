# Install Guide

## Primary flow

Use the zip-runner when working from a downloaded bundle:

```powershell
powershell -ExecutionPolicy Bypass -File "F:\OneDrive\Descargasun_live_scene_composer_selection_store_inspector_target_wiring_v1_from_zip.ps1"
```

## What the installer does

1. resolves the repo root
2. validates `docs/live-scene-composer`
3. installs the canonical docs
4. stages the source pack under `tools/live-scene-composer/selection-store-inspector-target-wiring-v1`
5. tries to infer a composer source root
6. if exactly one confident candidate exists, mirrors the `selection/` source files there
7. writes summaries into `F:\OneDrive\Descargas`
8. runs the docs architecture guard when available

## Safety behavior

- existing files are backed up before overwrite
- uncertain source-root detection falls back to staging only
- install summaries are written in both `.txt` and `.json`
- no use of `ProcessStartInfo.ArgumentList`

## Important note

The auto-install step for TypeScript sources is intentionally conservative.
If the repo layout is ambiguous, the source files are staged but not forced into a guessed path.
That avoids creating architecture drift through a bad path assumption.
