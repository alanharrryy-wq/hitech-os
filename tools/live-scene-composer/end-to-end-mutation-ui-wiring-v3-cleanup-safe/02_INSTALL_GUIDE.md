# Install Guide

After extracting the zip, run:

```powershell
powershell -ExecutionPolicy Bypass -File .pply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1 -Mode Install
```

Optional modes:

```powershell
powershell -ExecutionPolicy Bypass -File .pply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1 -Mode Verify
powershell -ExecutionPolicy Bypass -File .pply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1 -Mode Cleanup
powershell -ExecutionPolicy Bypass -File .pply_live_scene_composer_end_to_end_mutation_ui_wiring_v3_cleanup_safe.ps1 -Mode Report
```

Package docs install to staging only unless `-InstallPackageDocsToCanonicalRoot` is explicitly passed.
