# Install guide

## Preferred path

Use the runner from the zip:

```powershell
powershell -ExecutionPolicy Bypass -File "F:\OneDrive\Descargas
un_live_scene_composer_end_to_end_mutation_ui_wiring_v2_fixed_from_zip.ps1" -AllowInferredPaths
```

## What the installer does

- validates the package layout
- stages the bundle under `tools/live-scene-composer/end-to-end-mutation-ui-wiring-v2-fixed`
- copies top-level markdown docs into `docs/live-scene-composer`
- optionally mirrors source into a detected composer source root
- runs verification and smoke checks unless explicitly skipped
- writes summaries to `F:\OneDrive\Descargas`

## Verification output

Expect a summary folder named like:

`F:\OneDrive\Descargas\end_to_end_mutation_ui_wiring_v2_fixed_YYYYMMDD_HHMMSS`
