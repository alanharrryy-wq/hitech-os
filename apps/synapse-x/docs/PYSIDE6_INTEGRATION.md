# PySide6 Integration Notes

## Principle
Do not put file scanning, parsing, normalization, or SQLite persistence into widgets.

## Current mounted shape
The UI now mounts the reusable glass shell as the product host.

```text
run_ui.py
  -> synapse_x.ui.app.main()
      -> SynapseXMainWindow
          -> TemplateConsoleWindow
              -> sidebar slot: ControlsPanel
              -> main slot: ResultsPanel + DetailPanel
              -> aux slot: MetricsPanel
```

## UI responsibilities
- host reusable shell chrome, theme switching, scale controls, and slot composition
- render recent/search results
- render session detail and raw payload inspection
- render metrics and charts when optional chart extras are available
- degrade gracefully when chart extras are missing

## Engine responsibilities
- init storage
- ingest files
- search indexed content
- return session detail
- aggregate metrics
- repair indexes and integrity

## Worker-thread rule
Long operations like ingest and repair should run off the UI thread once the next controller/worker layer is mounted. For now, fast search/metrics calls are allowed directly from the host.

## Recommended next layer
Create a thin adapter/controller around `SynapseEngine` and move long-running actions into worker threads.

## Entry points
```powershell
python run_ui.py
python run_engine.py metrics
```
