# Glass Framework Demos

These examples are framework demos, not DeltaForge adapters.

## Included compositions

- `build_form_example`: form/capture layout.
- `build_dashboard_example`: metric/dashboard layout.
- `build_inspector_example`: inspect/detail layout.
- `build_tabbed_workspace_example`: tab states + collapsible workspace.
- `build_alternate_preset_example`: alternate theme/density preset.
- `build_orchestration_example`: runtime orchestration (preset/layout/visibility/persistence).
- `GlassExampleCatalog`: single widget that hosts all examples.
- `integration_demo.py`: neutral command/query/snapshot/event flow through integration contracts.

## Purpose

- Prove framework neutrality.
- Provide copy-ready compositions for future apps.
- Keep app-specific logic out of framework core.

## Run integration demo

```bash
python forgeos/shared/pyside6_glass/examples/integration_demo.py
```

This demo exercises:

- in-process adapter
- local HTTP adapter
- contracts discovery route
- event stream single-frame scaffold route
- capability-aware command handling
- structured query/snapshot responses
- event polling
