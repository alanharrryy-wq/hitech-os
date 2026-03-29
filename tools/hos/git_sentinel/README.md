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
- profile-based operation (`safe`, `strict`, `aggressive`)
- anti-overlap guardian lock (stale-lock protection)
- retention policy for reports/telemetry/logs/quarantine
- health/stop/security alert dispatch (webhook optional)
- false-positive feedback filtering + metrics export
- security scanner (secrets + dangerous scripts)
- detector quality evaluation (precision/recall/F1) with golden dataset
- CI incremental security gate (diff-scoped findings + quality thresholds)
- telemetry, prediction, and dashboard data generation
- visualization data export (dependency graph, heatmap, timeline, module interactions)
- guardian mode scheduler

## Commands

```powershell
python tools/hos/git_sentinel/cli_sentinel.py scan --json
python tools/hos/git_sentinel/cli_sentinel.py once
python tools/hos/git_sentinel/cli_sentinel.py once --apply
python tools/hos/git_sentinel/cli_sentinel.py once --apply-cleanup
python tools/hos/git_sentinel/cli_sentinel.py once --apply-repair
python tools/hos/git_sentinel/cli_sentinel.py guardian --profile strict --apply --interval-sec 0
python tools/hos/git_sentinel/cli_sentinel.py security-eval
python tools/hos/git_sentinel/cli_sentinel.py ci-gate --base-ref origin/main
python tools/hos/git_sentinel/dashboard_app.py --profile strict --port 8787 --open-browser
```

`ci-gate` scopes findings to `base_ref...HEAD` and also includes local/staged pending changes.

## Persistent guardian (Windows)

Register an idempotent scheduled task that runs guardian cycles continuously:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/git_sentinel/manage_guardian_task.ps1 -Action install -Apply -IntervalSec 600 -RunNow
pwsh -NoProfile -ExecutionPolicy Bypass -File tools/hos/git_sentinel/manage_guardian_task.ps1 -Action status
```

By default the scheduled task runs with `--no-ignore-update` to avoid dirtying tracked files during background cycles.
Use `-Profile strict` or `-Profile aggressive` when you need tighter hygiene cadence.
The installer defaults to hidden window execution (`pythonw.exe` if available).

## Runtime output

All runtime files are written under:

```text
tools/_local/git_sentinel/
```

Key outputs:

- `reports/git_sentinel_report_latest.json`
- `dashboard/dashboard_data.json`
- `telemetry/telemetry_latest.json`
- `telemetry/false_positive_metrics_latest.json`
- `telemetry/security_eval_latest.json`
- `telemetry/ci_gate_latest.json`
- `visualization/repository_dependency_graph.json`
- `visualization/file_modification_heatmap.json`
- `visualization/repository_growth_timeline.json`
- `visualization/module_interaction_graph.json`

## Dashboard (Local Web)

Run a simple local operations dashboard (no extra dependencies):

```powershell
python tools/hos/git_sentinel/dashboard_app.py --profile strict --port 8787
```

Then open `http://127.0.0.1:8787/`.

## Safety model

- default mode is dry-run (`--apply` required for mutations)
- granular mutation controls are available via `--apply-cleanup` and `--apply-repair`
- tracked files are never deleted by cleanup
- destructive actions are restricted to safe prefixes
- repair stop condition blocks execution if source code could be affected

## Security Quality

- golden dataset path: `tools/hos/git_sentinel/golden/security_eval_dataset.json`
- metrics exported per cycle: `precision`, `recall`, `f1`, `tp`, `fp`, `fn`
- quality thresholds are profile-aware via:
  - `security_eval_min_precision`
  - `security_eval_min_recall`
  - `security_eval_min_f1`

## Feedback + Alerts

- false-positive feedback file: `tools/_local/git_sentinel/state/false_positive_feedback.json`
- false-positive audit file: `tools/_local/git_sentinel/state/false_positive_audit.json`
- alert webhook env var: `GIT_SENTINEL_ALERT_WEBHOOK`
- alert log output: `tools/_local/git_sentinel/logs/alert_*.json`

Suppression entries are governed with `owner`, `reason`, and `expiresAt` (TTL). Expired suppressions are ignored and audited.

## Guardian Task Tests (Pester)

```powershell
Invoke-Pester -Path tools/tests/git-sentinel/GuardianTaskManager.Tests.ps1
python -m unittest discover -s tools/tests/git-sentinel -p "test_*.py"
```
