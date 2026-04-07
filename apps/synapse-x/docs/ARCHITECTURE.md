# Architecture

## Goal
Keep the backend independent from PySide6 so the UI only orchestrates service calls.

## Core boundary
Use `SynapseEngine` as the single interface between UI and backend.

## UI integration contract
The future PySide6 layer should call:
- `init_storage()`
- `ingest(paths=None, full=False)`
- `search(...)`
- `get_session_detail(session_id)`
- `get_metrics(days=7)`
- `repair()`

## Suggested PySide6 mapping
- Ingest button -> `engine.ingest()`
- Full button -> `engine.ingest(full=True)`
- Search box -> `engine.search(query, ...)`
- Results click -> `engine.get_session_detail(session_id)`
- Metrics panel refresh -> `engine.get_metrics()`
- Repair button -> `engine.repair()`
