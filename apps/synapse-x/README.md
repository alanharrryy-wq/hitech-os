# SYNAPSE-X Backend Engine

Backend-only operational memory engine, ready to be mounted into a PySide6 interface later.

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
