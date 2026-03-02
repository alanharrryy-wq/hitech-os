# UI Map Queries

Deterministic query set exposed by `tools/ui_map/query_engine.py`.

## Available Queries
- `assets_used_by_screen(screen_id)`
- `changeset_hint(file_or_component)`
- `component_tree(screen_id)`
- `dependents_of_file(file)`
- `files_touched_by_screen(screen_id)`
- `hotspots_by_risk(level)`
- `imports_of_file(file)`
- `routes_index()`
- `screens_using_component(component_id)`
- `state_readers(state_id)`
- `state_writers(state_id)`
- `styles_used_by_screen(screen_id)`

See `samples.md` for sample calls and expected output shapes.
