# Install Guide

## Default flow
1. Copy the zip into `F:\OneDrive\Descargas`.
2. Run the wrapper script from PowerShell.
3. Let the installer stage docs under `docs\live-scene-composer`.
4. Review the generated summary under `F:\OneDrive\Descargas`.

## Suggested command

```powershell
powershell -ExecutionPolicy Bypass -File "F:\OneDrive\Descargas\run_live_scene_composer_mutation_client_bridge_preview_commit_v2_fixed_from_zip.ps1" -AllowInferredPaths
```

## Optional flags
- `-InstallIntoComposerSrc`: mirrors the reference seam into a uniquely detected composer source root
- `-SkipGuard`: skips the docs architecture guard if the repo lacks the validator or Python


This package supersedes the previous installer generation that failed with `MissingExpressionAfterToken`.
