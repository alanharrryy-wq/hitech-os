# 112_OPERATOR_CLEANUP_RUNBOOK

Recommended operator flow:
1. Extract the zip to a temp folder under Downloads.
2. Run the main script in Install mode.
3. Review the summary txt and json files in Downloads.
4. If the repo shows wave-specific clutter you do not want, run Cleanup mode.
5. Keep the summary folder as evidence.

Suggested commands after extraction:
- .\apply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1 -Mode Install
- .\apply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1 -Mode Verify
- .\apply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1 -Mode Cleanup
