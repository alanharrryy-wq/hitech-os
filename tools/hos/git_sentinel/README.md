# Git Sentinel

Autonomous repository hygiene system for HITECH OS.

## Capabilities

- repository scanner (new files, nested git markers, binaries, large files, duplicates)
- artifact classifier + learning database (SQLite)
- managed `.gitignore` block auto-generation
- managed `.gitignore` block version history
- cleanup engine with safe-prefix validation
- reversible cleanup via quarantine when possible
- repair engine with stop conditions and dry-run default
- security scanner (secrets + dangerous scripts)
- telemetry, prediction, and dashboard data generation
- visualization data export (dependency graph, heatmap, timeline, module interactions)
- guardian mode scheduler

## Commands

```powershell
python tools/hos/git_sentinel/cli_sentinel.py scan --json
python tools/hos/git_sentinel/cli_sentinel.py once
python tools/hos/git_sentinel/cli_sentinel.py once --apply
python tools/hos/git_sentinel/cli_sentinel.py guardian --apply --interval-sec 600
```

## Persistent guardian (Windows)

Register an idempotent scheduled task that runs guardian cycles continuously:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/git_sentinel/manage_guardian_task.ps1 -Action install -Apply -IntervalSec 600 -RunNow
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/git_sentinel/manage_guardian_task.ps1 -Action status
```

By default the scheduled task runs with `--no-ignore-update` to avoid dirtying tracked files during background cycles.

## Runtime output

All runtime files are written under:

```text
tools/_local/git_sentinel/
```

Key outputs:

- `reports/git_sentinel_report_latest.json`
- `dashboard/dashboard_data.json`
- `telemetry/telemetry_latest.json`
- `visualization/repository_dependency_graph.json`
- `visualization/file_modification_heatmap.json`
- `visualization/repository_growth_timeline.json`
- `visualization/module_interaction_graph.json`

## Safety model

- default mode is dry-run (`--apply` required for mutations)
- tracked files are never deleted by cleanup
- destructive actions are restricted to safe prefixes
- repair stop condition blocks execution if source code could be affected
