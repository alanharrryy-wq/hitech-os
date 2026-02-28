# HOS Factory Launcher

Launch command:

```powershell
pwsh -File scripts/OPEN_HOS_FACTORY.ps1 -RunId "20260227_3"
```

Validation command:

```powershell
python -m tools.hos.launcher.hos_factory_launcher --run-id 20260227_3 --validate
```

Example JSON summary output:

```json
{
  "ok": true,
  "run_id": "20260227_3",
  "repo_root": "F:\\repos\\hitech-os",
  "worktrees": {
    "A_core": "F:\\repos\\hitech-os\\tools\\codex\\worktrees\\A_core",
    "B_tooling": "F:\\repos\\hitech-os\\tools\\codex\\worktrees\\B_tooling",
    "C_features": "F:\\repos\\hitech-os\\tools\\codex\\worktrees\\C_features",
    "D_validation": "F:\\repos\\hitech-os\\tools\\codex\\worktrees\\D_validation",
    "Z_aggregator": "F:\\repos\\hitech-os\\tools\\codex\\worktrees\\Z_aggregator"
  },
  "opened": ["A_core", "B_tooling", "C_features", "D_validation", "Z_aggregator"],
  "warnings": [],
  "errors": []
}
```
