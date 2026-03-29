
# Install Guide

## Normal path

1. Copy the zip to `F:\OneDrive\Descargas`.
2. Run the zip wrapper PowerShell script.
3. Let the installer stage the pack into `tools/live-scene-composer` and copy docs into `docs/live-scene-composer`.
4. Use `-AllowInferredPaths` if you want the installer to detect a composer source root.
5. Use `-InstallIntoComposerSrc` only if you want the source seam mirrored into the inferred composer source path.

## Safety posture

- docs are copied as complete files
- source seam is staged first into tooling, not hidden in random product paths
- direct runtime write paths are not introduced by this pack
- mutation requests remain expressed as intents, not uncontrolled runtime calls

## Suggested command

```powershell
powershell -ExecutionPolicy Bypass -File "F:\OneDrive\Descargasun_live_scene_composer_structure_tree_canvas_sync_over_selection_store_v1_from_zip.ps1" -AllowInferredPaths
```
