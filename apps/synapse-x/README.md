# SYNAPSE-X Engine + Studio

Operational memory engine with CLI, operations scripts, and an optional PySide6 desktop UI.

## What it includes
- incremental and full ingest
- parser support for JSON, JSONL, log, txt, md, report
- canonical normalization and session correlation
- SQLite persistence with optional FTS5
- ranked search with snippets and filters
- session detail, related sessions, timeline, root-cause hints
- metrics and diagnostics summary
- repair/index rebuild
- session report export (`.md`)
- watch mode (polling ingest)

## Public API
Main class: `synapse_x.engine.SynapseEngine`

Useful methods:
- `init_storage()`
- `ingest(paths=None, full=False)`
- `search(query, record_type=None, date_from=None, date_to=None, limit=50)`
- `get_session_detail(session_id)`
- `get_metrics(days=7)`
- `repair()`
- `get_status()`
- `export_session_report(session_id, output_path=None)`

## Quick start (CLI)
```powershell
python run_engine.py init-db
python run_engine.py ingest --path F:\some\folder
python run_engine.py search --query "error"
python run_engine.py session-detail --session-id run-abc-42
python run_engine.py metrics --days 14
python run_engine.py status
python run_engine.py export-session --session-id run-abc-42
```

## Operations scripts
```powershell
.\scripts\ops\ingest-now.ps1 -Path F:\some\folder
.\scripts\ops\full-ingest.ps1 -Path F:\some\folder
.\scripts\ops\repair.ps1
.\scripts\ops\watch-on.ps1 -Interval 30
.\scripts\ops\watch-off.ps1
```

Watcher PID/stop/log files are written under `F:\repos\hitech-os\tools\_local`.

## Desktop UI (optional)
If `PySide6` is installed in your environment:
```powershell
python run_engine.py ui
```
