# PySide6 Integration Notes

## Principle
Do not put file scanning, parsing or SQLite logic into widgets.

## Recommended adapter layer
Create a thin adapter or controller around `SynapseEngine` and call it from slots or worker threads.

## Worker-thread rule
Long operations like ingest and repair should run off the UI thread.

## Example shape
```python
engine = SynapseEngine()

def on_ingest_clicked():
    result = engine.ingest()

def on_search_changed(text: str):
    rows = engine.search(text)

def on_result_selected(session_id: str):
    detail = engine.get_session_detail(session_id)
```
