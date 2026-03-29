# 109_SINGLE_SCRIPT_OPERATION_MODES

Main script: apply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1

Modes:
- Install: cleanup legacy wave clutter, stage v3, verify, and write reports
- Verify: inspect repo state and write verification report only
- Cleanup: remove v3-owned state and legacy v1/v2 UI wiring clutter, then write cleanup report
- Report: print manifest and path expectations without changing the repo

Important defaults:
- package docs install to staging only
- legacy cleanup runs during install unless explicitly skipped
- summary directory is created automatically
