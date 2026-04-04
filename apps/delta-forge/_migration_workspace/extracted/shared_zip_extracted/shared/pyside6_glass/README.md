# PySide6 Glass Framework

`forgeos/shared/pyside6_glass` is the reusable UI platform for workstation-style PySide6 apps.

This is framework core, not app logic.

## Layer Boundaries

- Framework Core (`forgeos/shared/pyside6_glass/*`): reusable primitives, contracts, config, runtime, extension APIs.
- App Adapter (example: `apps/deltaforge/ui/adapters/*`): app-specific preset wrappers and asset registration.
- Demo Layer (`forgeos/shared/pyside6_glass/examples/*`): practical compositions and runtime usage patterns.

Hard rule: app-specific behavior must stay in app adapters.

## Stable Public API

Import from top-level package:

```python
from forgeos.shared.pyside6_glass import (
    GlassPanelTemplate,
    GlassWorkspaceRuntime,
    GlassTemplateConfig,
    get_template_preset,
    resolve_template_config_with_provenance,
    register_theme,
    register_template_preset,
    register_icon_pack,
    list_button_variants,
)
```

Core modules:

- `contracts.py`: frozen design/system contracts.
- `config.py`: layered configuration model + preset registry + provenance.
- `theme.py`: theme manifests, inheritance, stylesheet mapping.
- `icons.py`: icon pack registry, aliases, size tokens, accessibility helpers.
- `template.py`: shell, tabs, panels, layout controller.
- `runtime.py`: orchestration (preset activation, layout switching, visibility policy, persistence).
- `extensions.py`: extension registration entry points.
- `integration/`: external integration contracts, service boundary, and transport adapters.
- `persistence.py`: workspace state schema and migrations.
- `primitives.py`: reusable higher-level UI blocks.
- `diagnostics.py`: config/runtime inspection helpers.
- `catalog.py`: registry-based framework catalog API (entries, categories, search).
- `data.py`: neutral data query/result/provider contracts and provider registry.
- `data_providers.py`: built-in mock and local SQLite providers for local dashboard development.
- `dashboard.py`: provider-bound dashboard surface for metrics/table/feed/payload rendering.
- `assets.py`: premium reusable controls/assets for workstation dashboards.

## Configuration Hierarchy

`resolve_template_config_with_provenance(...)` resolves layers in this order:

1. `framework_defaults`
2. `theme_defaults`
3. `preset_defaults`
4. `app_overrides`
5. `workspace_overrides`
6. `runtime_overrides`
7. `explicit_config`

Use `GlassResolvedConfig.field_sources` to inspect where each resolved field came from.

## Presets and Experiences

Built-ins include:

- `neutral`
- `form_console`
- `dashboard`
- `inspector`
- `tabbed_workspace`
- `compact_operator`
- `presentation`

Register new presets with `register_template_preset(...)`.

## Runtime Orchestration

`GlassWorkspaceRuntime` centralizes:

- applying resolved config to a live template
- runtime preset activation
- named layout registration/switching
- visibility policy evaluation (`tab` / `panel` / `action` targets)
- keyboard routing helpers
- workspace state save/load
- diagnostics snapshot

## External Integration Boundary

The framework now includes a neutral ingress/egress contract layer for future lightweight clients.

- contracts: `integration/contracts.py`
- service boundary: `integration/service.py`
- adapters: `integration/adapters.py`
- runtime bridge: `integration/runtime_bridge.py`

Current adapters:

- `InProcessIntegrationAdapter` (fully implemented)
- `LocalHttpIntegrationAdapter` (local-only adapter for lightweight client bridge scenarios)
- `WebSocketIntegrationAdapterScaffold` (prepared)
- `IpcIntegrationAdapterScaffold` (prepared)

Read full details in [INTEGRATION.md](./INTEGRATION.md).

## Glass Workbench

The examples host is now a registry-driven **Glass Workbench** built on top of the catalog system.

It provides:

- predefined built-in entries for compositions, presets, themes, primitives, and runtime/integration showcases
- predefined provider-backed **Data Dashboards** entries for operational-style surfaces
- predefined **Controls & Assets** gallery entries for reusable premium components
- category browsing + search filtering
- optional tag filtering for curated discovery
- metadata-rich item details
- preview and workspace launch actions
- focused inspection tabs:
  - `Entry`: metadata, related entries, layer boundaries, builder reference
  - `Data`: provider list, provider diagnostics, selected query binding, live query probe
  - `Runtime`: architecture boundaries and integration/runtime diagnostics summary

Core catalog APIs:

- `register_catalog_entry(...)`
- `list_catalog_entries(...)`
- `get_catalog_entry(...)`
- `list_catalog_categories(...)`
- `list_catalog_tags(...)`
- `register_builtin_catalog_entries(...)`

Workbench shell widgets:

- `GlassCatalogShell` (new main browser widget)
- `GlassExampleCatalog` (backward-compatible entry point)

### Add a custom catalog entry

```python
from forgeos.shared.pyside6_glass import register_catalog_entry

register_catalog_entry(
    entry_id="custom.my_entry",
    title="My Custom Entry",
    subtitle="Short summary",
    description="What this showcases.",
    category="Custom",
    tags=("custom", "starter"),
    builder=lambda parent: MyCatalogWidget(parent),
    sort_order=900,
)
```

The workbench automatically picks up registered entries.

### Inspecting live preview and runtime/data behavior

1. Run `python -m forgeos.shared.pyside6_glass.examples`.
2. Select an entry in the left rail.
3. Use `Open Preview` to render the selected surface in the central canvas area.
4. Open the `Data` tab to inspect provider/query wiring and run `Probe Selected Query`.
5. Open the `Runtime` tab to inspect architecture boundaries, provider inventory, and integration contract diagnostics.

### Interactive Composer (Workbench `Compose` tab)

The workbench includes a live, non-destructive layout composer layered on top of preview/workspace contexts.

Capabilities:

- searchable insert palette with category filters and icon metadata
- rich insertable object model (layout, content, input, action, data, diagnostic, state, utility)
- structured property inspector (type, slot, state, variant, density, width policy, padding, data/query hints)
- explicit edit actions: insert, duplicate, remove, reorder, move across slots, split adjustments
- clone-aware persistence (`Save Clone`) and instant baseline rollback (`Reset Changes`)

Lifecycle/budget safeguards:

- only active workspace tab is mounted/live (`_LazyMountHost`)
- inactive tabs unmount panel trees by default
- heavy panel cap per tab (`heavy_panels_per_tab`)
- live-data widget cap per tab (`live_data_widgets_per_tab`)
- per-slot panel capacity policy (`main`, `side`, `status`)
- overflow objects automatically move to `hold`/`background` instead of overloading active render paths

Clone storage:

- `tools/_local/pyside6_glass/workbench_clones`

Original catalog entries remain pristine unless explicitly cloned and edited from clone source.

### Sacred Contract and Release Gate

Release blockers are formalized in:

- `forgeos/shared/pyside6_glass/SACRED_CAPABILITIES_CONTRACT.md`
- Full premium capability model (100): `forgeos/shared/pyside6_glass/contracts/premium_capabilities_100.md`
- Operational capability matrix (status baseline + evidence tags): `forgeos/shared/pyside6_glass/contracts/premium_capability_matrix_v1.json`
- Golden sessions spec: `forgeos/shared/pyside6_glass/golden_sessions/golden_sessions_v1.json`

Run the release gate:

```bash
python forgeos/shared/pyside6_glass/release_gate.py
```

Quick mode (contract + compile only):

```bash
python forgeos/shared/pyside6_glass/release_gate.py --skip-tests --skip-proof
```

CI/headless mode:

```bash
python forgeos/shared/pyside6_glass/release_gate.py --ci
```

CI/headless + non-blocking nightly visual proof (screenshots enabled):

```bash
python forgeos/shared/pyside6_glass/release_gate.py --ci --nightly-visual-proof
```

Run UX proof directly:

```bash
python -m forgeos.shared.pyside6_glass.ux_flight_recorder.runner --no-screenshots
```

Refresh proof baseline intentionally (never automatic):

```bash
python -m forgeos.shared.pyside6_glass.ux_flight_recorder.runner --refresh-baseline --no-screenshots
```

Evidence is written to:

- `tools/_local/evidence/pyside6_glass_release_gate_*.json`
- `forgeos/shared/pyside6_glass/artifacts/ux_release_proof/<timestamp>/`
- Operator workflow: `forgeos/shared/pyside6_glass/UX_RELEASE_PROOF.md`

Baseline store ownership:

- Semantic baseline (authoritative comparator source): `forgeos/shared/pyside6_glass/baselines/ux_release_proof/v1/semantic_baseline.json`
- Visual baseline manifest (secondary screenshot metadata): `forgeos/shared/pyside6_glass/baselines/ux_release_proof/v1/visual_baseline_manifest.json`

### Built-in Data Dashboard entries

The catalog includes provider-driven starter entries such as:

- `Live Metrics Board`
- `Service Health Monitor`
- `Alerts and Incidents Surface`
- `Jobs / Queue Monitor`
- `Table + Detail Inspector`
- `Time-Series Placeholder Dashboard`
- `Operational Overview`
- `Data Source Diagnostics`
- `Refreshable KPI Surface` (state simulation: loading/empty/error/stale)
- `Event Stream / Activity Feed`
- `Filterable Control Center`
- `Split View Operations Console`

These entries run through the neutral provider contracts in `data.py`.

### Built-in Controls and Assets entries

The catalog includes a dedicated reusable controls gallery:

- `Buttons Gallery`
- `Icon Buttons`
- `Segmented + Toggle Controls`
- `Filter Chips + Status Badges`
- `Enhanced Sliders`
- `Search + Toolbar Shell`
- `Stat Pills / Micro KPI`
- `Control Cards`
- `Collapsible Sections`
- `Parameter Panel`
- `Hero Header Panel`

## Data and Dashboard Subsystem

`pyside6_glass` now includes a neutral data layer for dashboard-style compositions.

Key contracts:

- `DataQuery`
- `DataResult`
- `DataState`
- `RefreshPolicy`
- `DataProviderMeta`
- `DashboardDataProvider`

Registry and execution APIs:

- `register_data_provider(...)`
- `list_data_providers()`
- `get_data_provider(...)`
- `execute_data_query(...)`
- `data_provider_diagnostics(...)`
- `describe_data_provider(...)`

Built-in providers:

- `InMemoryDashboardProvider` (`builtin.mock_dashboard`)
- `LocalSQLiteDashboardProvider` (`builtin.local_sqlite`)

Registration helper:

- `register_builtin_data_providers(...)`

Detailed reference: [DATA_DASHBOARD.md](./DATA_DASHBOARD.md)

### Reusable dashboard rendering helper

Use `DashboardDataSurface` + `DashboardQuerySpec` to bind provider output into a reusable dashboard panel with:

- loading/empty/error handling
- refresh action and optional polling behavior via `RefreshPolicy`
- metric card rendering
- table rendering
- feed rendering
- payload/diagnostics blocks
- local search/filter chips for rows/feed slices
- compact toolbar actions for refresh/clear filters

## Premium UI Assets Layer

`assets.py` provides reusable workstation controls with neutral semantics:

- action controls: `GlassIconButton`, `CompactToolbar` (`primary`, `secondary`, `subtle`, `ghost`, semantic variants)
- selection controls: `GlassSegmentedControl`, `TogglePill`, `FilterChipBar`
- search/control surfaces: `SearchCommandBar`, `ParameterPanel`, `ControlCard`
- status visualization: `StatusPill`, `StatPill`, `MiniLegend`
- structure/shells: `CollapsibleSection`, `HeroPanel`, `EnhancedSlider`

Consolidation note:

- `QuickActionsStrip` remains available for backward compatibility but now follows the same toolbar asset path as `CompactToolbar` instead of maintaining a separate duplicate behavior surface.

Usage pattern:

1. compose assets in templates (`GlassPanelTemplate`)
2. bind data using `DashboardDataSurface` when needed
3. register final composition in catalog with `register_catalog_entry(...)`

### Register a custom provider

```python
from forgeos.shared.pyside6_glass import (
    DataProviderMeta,
    DataResult,
    FunctionDataProvider,
    register_data_provider,
)

provider = FunctionDataProvider(
    meta=DataProviderMeta(
        provider_id="custom.local",
        title="Custom Local Provider",
        source_kind="in_memory",
    ),
    handler=lambda query: DataResult.success(query, metrics={"value": 42}),
)

register_data_provider(provider)
```

Inspect supported button variants:

```python
from forgeos.shared.pyside6_glass import list_button_variants

print(list_button_variants())
```

### Local-development data source

The local SQLite provider writes to:

- `tools/_local/tmp/pyside6_glass_dashboard.sqlite3`

Override path during registration:

```python
from pathlib import Path
from forgeos.shared.pyside6_glass import register_builtin_data_providers

register_builtin_data_providers(local_sqlite_path=Path("tools/_local/tmp/my_dashboard.sqlite3"))
```

## Tabs and Panels

Tabs support:

- placement (`top`, `bottom`, `left`, `right`)
- density (`compact`, `cozy`, `comfortable`, `extended`)
- variant (`glass`, `segmented`, `pill`, `standard`)
- icon mode (`text_only`, `icon_only`, `icon_text`)
- visibility states (`visible`, `hold`, `hidden`, `disabled`, `pending`, `warning`, `background`)
- tab metadata, badges, pinned tabs, lazy content factories, order snapshot/restore

Panels support:

- semantic roles (`main`, `side`, `inspector`, `summary`, `dashboard`, `form`, etc.)
- states (`visible`, `hidden`, `collapsed`, `deferred`, `disabled`, `background`, `hold`)
- toolbar/footer surfaces
- deferred loading
- min/preferred/max size hints

## Theming and Tokens

Theme system includes:

- `GlassPalette` + `GlassThemeManifest`
- theme registration and inheritance
- selective theme override registration
- semantic status colors (`success`, `warning`, `error`, `pending`)
- component mapping (tabs, panels, controls, states)

Register themes via:

- `register_theme(...)`
- `register_theme_overrides(...)`

## Icons

Use icon pack registration, not ad-hoc file paths:

```python
register_icon_pack("deltaforge", "apps/deltaforge/assets/icons")
set_default_icon_pack("deltaforge")
```

Support includes aliases, pack metadata, and size tokens (`micro`, `small`, `body`, `large`, `xlarge`).

## Persistence and Compatibility

Workspace state schema is versioned.

- Current schema: `2`
- Includes layout, tab states/order, panel state/visibility, visual preferences.
- v1 payloads are migrated on load.

## Extension Points

Use `extensions.py` registration APIs:

- `register_capability(...)`
- `register_preset_extension(...)`
- `register_theme_extension(...)`
- `register_theme_override_extension(...)`
- `register_icon_pack_extension(...)`

These are the supported path for framework augmentation without patching core files.

## Diagnostics

Use:

- `validate_template_config(...)`
- `config_snapshot(...)`
- `resolved_snapshot(...)`
- `template_runtime_snapshot(...)`

## Demo Runner

```bash
python -m forgeos.shared.pyside6_glass.examples
```

Optional example modes:

```bash
python -m forgeos.shared.pyside6_glass.examples --mode integration
python -m forgeos.shared.pyside6_glass.examples --mode smoke
```

Demo catalog includes form, dashboard, inspector, tabbed workspace, alternate preset, and runtime orchestration examples.
It also includes provider-backed data dashboards for metrics, health, incidents, queue, diagnostics and event feed scenarios.
It now includes controls/assets gallery entries as a reusable starter library.

Integration demo:

```bash
python forgeos/shared/pyside6_glass/examples/integration_demo.py
```

## Stable vs Experimental

- Stable: contracts, config dataclasses, top-level template API, theme/icon/preset registration, persistence schema contract, integration envelopes/service boundary.
- Experimental: higher-level composition patterns in demos, optional runtime interaction patterns, and future transport adapters beyond current local HTTP/in-process paths.
