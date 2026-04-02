# Glass Workbench and Examples

This folder contains the framework showcase layer for `pyside6_glass`.

## What changed

The old hardcoded tab demo host has been upgraded to a **registry-driven Glass Workbench**.

Main pieces:

- `catalog_shell.py`: interactive workbench UI (`GlassCatalogShell`)
- `catalog_builtin.py`: predefined built-in catalog registration
- `compositions.py`: reusable composition builders + backward-compatible `GlassExampleCatalog`
- `demo_app.py`: launches workbench experience
- `integration_demo.py`: neutral integration contracts demo

Workbench discovery now supports a workspace-first flow:

- clean central workspace by default
- `Add / Browse` content picker (or `Ctrl+K` / `Cmd+K`)
- searchable entry list + category filter + actionable entry details
- immediate preview on selection
- explicit actions:
  - `Add to Current Tab`
  - `Open in New Tab`
- advanced inspection tabs (on-demand tools surface):
  - `Entry`: metadata, related entries, entry kind, source builder reference
  - `Data`: selected provider/query binding, provider diagnostics, live query probe
  - `Runtime`: architecture boundaries + integration/runtime diagnostics summary

## Built-in catalog groups

- **Compositions**: Form, Dashboard, Inspector, Workspace, Alternate preset, Runtime orchestration
- **Presets**: `neutral`, `form_console`, `dashboard`, `inspector`, `tabbed_workspace`, `compact_operator`, `presentation`
- **Themes**: `silver_frost_cyan`, `obsidian_ice`
- **Primitives**: stat cards, quick actions strip, panel header, form section shell, state cards, dashboard widget shell
- **Runtime & Integration**: orchestration showcase, integration contracts showcase
- **Data Dashboards**: Live Metrics Board, Service Health Monitor, Alerts/Incidents, Queue Monitor, Table+Detail Inspector, Time-Series Placeholder, Operational Overview, Data Source Diagnostics, Refreshable KPI Surface (loading/empty/error/stale simulation), Event Feed, Filterable Control Center, Split View Operations Console
- **Controls & Assets**: buttons, icon buttons, segmented/toggle controls, chips/badges, enhanced sliders, search+toolbar shell, stat pills, control cards, collapsible sections, parameter panel, hero panel

## Launch workbench demo

```bash
python -m forgeos.shared.pyside6_glass.examples
```

Optional modes:

```bash
python -m forgeos.shared.pyside6_glass.examples --mode integration
python -m forgeos.shared.pyside6_glass.examples --mode smoke
python -m forgeos.shared.pyside6_glass.examples --mode proof
```

## Workbench inspection flow

1. Open picker with `Add / Browse` or `Ctrl+K`.
2. Search or filter by category.
3. Select an entry (preview updates immediately).
4. Choose `Add to Current Tab` or `Open in New Tab`.
5. Use `Tools` for advanced tabs:
   - `Entry` for metadata and related capabilities.
   - `Data` for provider-backed entries:
   - inspect provider/query identity
   - inspect registered provider metadata/diagnostics
   - run `Probe Selected Query` for a live result envelope
   - `Runtime` to inspect boundaries and integration contract diagnostics.

## Visual Editor / Composer Mode

The `Compose` tab now provides a non-destructive visual editor on top of the live preview/workspace context.

### Insert palette

- searchable object palette with categories (`layout`, `content`, `input`, `action`, `data`, `diagnostic`, `state`, `utility`)
- icon + description per insertable object type
- insertion target and position controls (`append`, `before selected`, `after selected`)
- recent object usage marker (`★`) for frequently inserted types

### Object categories and insertables

Representative built-ins include:

- layout containers: `empty_panel`, `split_container`, `tabbed_container`, `stacked_container`, `section_shell`
- content surfaces: `text_block`, `title_subtitle_block`, `text_markdown`, `list_view`, `image_svg`
- input/action controls: `form_input`, `form_section`, `selector_list`, `button_control`, `action_buttons`, `toolbar_controls`, `search_filter_bar`
- data widgets: `table_grid`, `chart_graph`, `metrics_kpi`, `metric_card`, `feed_log`, `timeline_activity`, `dashboard_widget`
- diagnostics: `inspector_panel`, `property_grid`, `json_diag`, `code_panel`
- state/utility: `empty_state_shell`, `loading_state_shell`, `error_state_shell`, `status_badge_group`, `divider_utility`, `spacer_utility`

### Structured inspector editing

For selected objects, the inspector exposes structured controls for:

- panel metadata: title, subtitle, icon, type, slot, role, state, visibility
- visual policy: variant, density, width policy, padding, height policy
- data/query hints: provider id, query id, chart mode, chart style/palette, options list
- chart tuning: grid, glow, markers, smoothing, stroke width, fill alpha
- layout controls: split proportions
- actions: apply, duplicate, remove, reorder, move left/right

### Lifecycle and budget policies

Composer enforces guardrails to prevent overload:

- only active workspace tab is mounted/live by default
- inactive tabs are lazy/unmounted
- heavy panel budget per tab (`heavy_panels_per_tab = 3`)
- live data widget budget per tab (`live_data_widgets_per_tab = 4`)
- per-slot capacity policy (`main=14`, `side=10`, `status=8`)
- overflow widgets are downgraded to `hold` or `background` automatically

State semantics used in composer:

- `visible`: active and rendered
- `deferred`: placeholder only, not fully active yet
- `hold`: paused due to budget policy
- `background`: inactive/off-budget but still present in session model
- `hidden`: explicitly hidden

### Non-destructive guarantees

- original catalog examples are never overwritten
- close without `Save Clone` discards unsaved session edits
- `Reset Changes` restores the pristine active source baseline immediately
- `Save Clone` writes to `tools/_local/pyside6_glass/workbench_clones/*.json`
- after `Save Clone`, session source switches to that clone and editing continues there

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

## UX release proof ownership

- Golden sessions spec: `forgeos/shared/pyside6_glass/golden_sessions/golden_sessions_v1.json`
- Semantic baseline: `forgeos/shared/pyside6_glass/baselines/ux_release_proof/v1/semantic_baseline.json`
- Visual baseline manifest: `forgeos/shared/pyside6_glass/baselines/ux_release_proof/v1/visual_baseline_manifest.json`
- Proof artifacts: `forgeos/shared/pyside6_glass/artifacts/ux_release_proof/<timestamp>/`

Baseline refresh is explicit only:

```bash
python -m forgeos.shared.pyside6_glass.ux_flight_recorder.runner --refresh-baseline --no-screenshots
```

Nightly visual proof (non-blocking, screenshot-enabled):

```bash
python forgeos/shared/pyside6_glass/release_gate.py --ci --nightly-visual-proof
```

Exercises:

- in-process adapter
- local HTTP adapter
- contracts discovery
- event polling + stream-frame scaffold
