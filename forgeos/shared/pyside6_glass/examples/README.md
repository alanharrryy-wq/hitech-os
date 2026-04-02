# Glass Catalog and Examples

This folder contains the framework showcase layer for `pyside6_glass`.

## What changed

The old hardcoded tab demo host has been upgraded to a **registry-driven Glass Catalog**.

Main pieces:

- `catalog_shell.py`: polished catalog browser UI (`GlassCatalogShell`)
- `catalog_builtin.py`: predefined built-in catalog registration
- `compositions.py`: reusable composition builders + backward-compatible `GlassExampleCatalog`
- `demo_app.py`: launches catalog experience
- `integration_demo.py`: neutral integration contracts demo

Catalog discovery supports:

- category rail
- free-text query
- optional comma-separated tag filter
- related-entry navigation in detail pane

## Built-in catalog groups

- **Compositions**: Form, Dashboard, Inspector, Workspace, Alternate preset, Runtime orchestration
- **Presets**: `neutral`, `form_console`, `dashboard`, `inspector`, `tabbed_workspace`, `compact_operator`, `presentation`
- **Themes**: `silver_frost_cyan`, `obsidian_ice`
- **Primitives**: stat cards, quick actions strip, panel header, form section shell, state cards, dashboard widget shell
- **Runtime & Integration**: orchestration showcase, integration contracts showcase
- **Data Dashboards**: Live Metrics Board, Service Health Monitor, Alerts/Incidents, Queue Monitor, Table+Detail Inspector, Time-Series Placeholder, Operational Overview, Data Source Diagnostics, Refreshable KPI Surface (loading/empty/error/stale simulation), Event Feed, Filterable Control Center, Split View Operations Console
- **Controls & Assets**: buttons, icon buttons, segmented/toggle controls, chips/badges, enhanced sliders, search+toolbar shell, stat pills, control cards, collapsible sections, parameter panel, hero panel

## Launch catalog demo

```bash
python -m forgeos.shared.pyside6_glass.examples
```

Optional modes:

```bash
python -m forgeos.shared.pyside6_glass.examples --mode integration
python -m forgeos.shared.pyside6_glass.examples --mode smoke
```

## Register new entries

Use the public registry API:

```python
from forgeos.shared.pyside6_glass import register_catalog_entry

register_catalog_entry(
    entry_id="custom.new_surface",
    title="Custom Surface",
    subtitle="My extension entry",
    description="Preview for a custom framework extension.",
    category="Custom",
    tags=("custom", "extension"),
    builder=lambda parent: CustomSurface(parent),
)
```

No changes to `GlassCatalogShell` are required for new entries.

Optional discoverability helpers:

- `list_catalog_categories(...)`
- `list_catalog_tags(...)`
- `list_catalog_entries(tags=(...))`

## Provider-backed dashboard extension flow

1. Register your provider in `data.py` registry APIs:

```python
from forgeos.shared.pyside6_glass import DataProviderMeta, FunctionDataProvider, DataResult, register_data_provider

register_data_provider(
    FunctionDataProvider(
        meta=DataProviderMeta(provider_id="custom.provider", title="Custom Provider"),
        handler=lambda query: DataResult.success(query, metrics={"sample": 1}),
    )
)
```

2. Build a provider-bound surface with `DashboardDataSurface`:

```python
from forgeos.shared.pyside6_glass import DashboardDataSurface, DashboardQuerySpec

surface = DashboardDataSurface(
    DashboardQuerySpec(
        provider_id="custom.provider",
        query_id="live_metrics",
        title="Custom Data Surface",
    )
)
```

3. Register a catalog entry that returns a `GlassPanelTemplate` embedding this surface.

## Reusable controls/assets extension flow

1. Compose controls from `assets.py`:

```python
from forgeos.shared.pyside6_glass import (
    CompactToolbar,
    FilterChipBar,
    GlassSegmentedControl,
    ParameterPanel,
)
```

2. Embed in a template:

```python
template = GlassPanelTemplate(...)
template.slots.main_slot.addWidget(CompactToolbar(\"Actions\"))
template.slots.side_slot.addWidget(ParameterPanel(\"Parameters\"))
```

3. Register the composition via `register_catalog_entry(...)`.

## Integration demo

```bash
python forgeos/shared/pyside6_glass/examples/integration_demo.py
```

Exercises:

- in-process adapter
- local HTTP adapter
- contracts discovery
- event polling + stream-frame scaffold
