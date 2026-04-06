# SYNAPSE-X Backend Engine + Glass UI Host
Operational memory engine with a mounted PySide6 glass host for live metrics, search, and detail inspection.

## What it includes
- incremental-ish file ingestion based on file state
- parser registry for JSON, JSONL, log, txt, md, report
- canonical normalization
- SQLite persistence
- optional FTS5 search with LIKE fallback
- session detail and timeline retrieval
- metrics aggregation
- repair and index rebuild
- CLI entry points
- clear service-layer API for a future UI

## Public API
Main class: `synapse_x.engine.SynapseEngine`

Useful methods:
- `init_storage()`
- `ingest(paths=None, full=False)`
- `search(query, record_type=None, date_from=None, date_to=None, limit=50)`
- `get_session_detail(session_id)`
- `get_metrics(days=7)`
- `repair()`

## PySide6 mounting idea
Your future UI should call service methods, not parse files directly.

Example:
```python
from synapse_x.engine import SynapseEngine

engine = SynapseEngine()
engine.init_storage()
result = engine.ingest()
rows = engine.search("pyside6 failure")
detail = engine.get_session_detail("rollout-2026-04-05")
metrics = engine.get_metrics()
```

## Quick start
```powershell
python run_engine.py init-db
python run_engine.py ingest --path F:\some\folder
python run_engine.py search --query "error"
python run_engine.py metrics
```


## Glass UI host
The repo now includes a real UI entrypoint built on top of the reusable glass shell.

### Main entrypoint
```powershell
python run_ui.py
```

### Dev helper
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\run-ui.ps1
```

### What the UI includes right now
- reusable glass shell mounted as the main app host
- operator controls in the sidebar
- recent/search results in the main workspace
- live detail inspector under the results deck
- metrics surface in the aux slot with graceful fallback when optional chart deps are missing
- keyboard shortcuts for refresh, focus search, repair, demo load, and chart visibility


## UI quick start
```powershell
pip install -r requirements.txt
python run_ui.py
```

## Root cleanup and launcher behavior

The repository keeps the visible root intentionally minimal.

- `starter.py` is now the human-friendly launcher for the UI and is the recommended file to run or double-click.
- internal root entrypoints were rehomed under `.synapse_hidden/entrypoints/`
- developer helpers remain under `scripts/dev/`

### Recommended launch
```powershell
python starter.py
```

### Engine helper
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev\run-engine.ps1 metrics
```

## Visible launcher

- `starter.py` is the human-friendly launcher for the UI.
- internal entrypoints live under `.synapse_hidden/entrypoints/`
- developer helpers remain under `scripts/dev/`

### Launch
```powershell
python starter.py
```
