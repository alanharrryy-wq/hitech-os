# Live Scene Composer End-to-End Mutation UI Wiring Pack v3 cleanup-safe

This package stacks on the validated mutation path work and adds a cleanup-safe delivery shape.

What is different in v3:
- one main PowerShell script for install, verify, cleanup, and report
- package docs default to staging only to avoid canonical docs clutter
- legacy wave cleanup for end-to-end UI wiring v1 and v2 fixed
- explicit ownership manifest for safe delete behavior
- automatic summary directory creation and evidence output

Main script after extraction:
- `apply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1`

Default install behavior:
- cleans legacy v1/v2 UI wiring wave clutter
- stages v3 under `tools/live-scene-composer/end-to-end-mutation-ui-wiring-v3-cleanup-safe`
- keeps package docs under staging root
- preserves canonical architecture docs
- writes install, verify, and cleanup evidence to `F:\OneDrive\Descargas\live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe_summary`
