# GIT_SENTINEL

## Purpose

Git Sentinel is the autonomous hygiene subsystem for this repository.  
It continuously scans, learns, repairs, and reports repository health while preserving deterministic behavior.

## Architecture

Implementation path:

- `tools/hos/git_sentinel/`

Modules:

- `scanner.py`: repository state map, nested git detection, binaries, large files, duplicates, runtime zones
- `artifact_detector.py`: artifact categorization and learnable pattern extraction
- `ignore_manager.py`: safe auto-generation of managed `.gitignore` rules
- `cleanup_engine.py`: cleanup plan + execution (untracked artifacts only, safe prefixes)
- `repair_engine.py`: nested git repairs, broken symlink repair, git config normalization, optional tracked restore
- `security_scanner.py`: secret/token/private-key and dangerous-script detection
- `learning_engine.py`: SQLite learning database + telemetry/prediction history
- `telemetry.py`: metric payload build + persistence
- `prediction_engine.py`: bloat/conflict/artifact/disk/problem-file risk signals
- `visualization.py`: dependency graph, modification heatmap, growth timeline, module interaction graph
- `report_generator.py`: health score, reports, dashboard-ready JSON
- `scheduler.py`: guardian loop (continuous automation)
- `sentinel.py`: end-to-end orchestration
- `cli_sentinel.py`: local execution interface

## Safety and Stop Conditions

- Dry-run by default (`--apply` required for mutations)
- Tracked files are never removed by cleanup
- Cleanup and repair are restricted to explicit safe prefixes
- If repair actions could affect legitimate source code, execution stops with `stop_condition_triggered`
- No nested unmanaged git repositories are tolerated

## Guardian Mode

Continuous mode:

```powershell
python tools/hos/git_sentinel/cli_sentinel.py guardian --apply --interval-sec 300
```

Single cycle:

```powershell
python tools/hos/git_sentinel/cli_sentinel.py once
python tools/hos/git_sentinel/cli_sentinel.py once --apply
```

Task scheduler activation (Windows, persistent):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/git_sentinel/manage_guardian_task.ps1 -Action install -Apply -IntervalSec 600 -RunNow
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/git_sentinel/manage_guardian_task.ps1 -Action status
```

The managed task defaults to `--no-ignore-update` so background runs stay deterministic without modifying tracked `.gitignore`.

## Runtime Artifacts

All sentinel runtime artifacts are written to:

```text
tools/_local/git_sentinel/
```

Includes:

- reports
- telemetry snapshots
- dashboard JSON
- visualization JSON
- state database (`SQLite`)

## Dashboard Data Layer

Dashboard payload:

- `tools/_local/git_sentinel/dashboard/dashboard_data.json`

Contains:

- metrics
- alerts
- cleanup actions
- health score and factors
- prediction signals
