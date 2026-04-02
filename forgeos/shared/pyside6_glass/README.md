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

Read full details in [INTEGRATION.md](F:/repos/hitech-os/forgeos/shared/pyside6_glass/INTEGRATION.md).

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

Demo catalog includes form, dashboard, inspector, tabbed workspace, alternate preset, and runtime orchestration examples.

Integration demo:

```bash
python forgeos/shared/pyside6_glass/examples/integration_demo.py
```

## Stable vs Experimental

- Stable: contracts, config dataclasses, top-level template API, theme/icon/preset registration, persistence schema contract, integration envelopes/service boundary.
- Experimental: higher-level composition patterns in demos, optional runtime interaction patterns, and future transport adapters beyond current local HTTP/in-process paths.
