# Extraction Report

## Scope

Extraction source:

- `F:\repos\hitech-os\tools\graphviz\repo_analizer`

Extraction target:

- `F:\repos\hitech-os\tools\live-scene-composer\composer-workbench-seed`

## Copied Reference Files (Verbatim)

All files below were copied unchanged into `reference/repo-analyzer-plugin-kernel`:

1. `plugin_base.py`
2. `plugin_manager.py`
3. `plugin_manifest.py`
4. `service_container.py`
5. `event_bus.py`
6. `command_dispatcher.py`

## Newly Created Files

### Seed source

1. `src/core/service-container.ts`
2. `src/core/event-bus.ts`
3. `src/core/command-dispatcher.ts`
4. `src/modules/module-manifest.ts`
5. `src/modules/module-base.ts`
6. `src/modules/module-context.ts`
7. `src/modules/module-loader.ts`
8. `src/modules/module-registry.ts`
9. `src/providers/composer-workbench-provider.tsx`
10. `src/providers/selection-provider.tsx`
11. `src/providers/mutation-provider.tsx`
12. `src/adapters/runtime-mutation-bridge-adapter.ts`
13. `src/workbench/composer-workbench.tsx`
14. `src/workbench/workbench-layout.tsx`
15. `src/workbench/surfaces/module-board.tsx`
16. `src/contracts.ts`
17. `src/index.ts`

### Seed docs

1. `README.md`
2. `EXTRACTION_REPORT.md`
3. `ARCHITECTURE_NOTES.md`

## Architecture Decisions Applied

1. Replaced plugin naming with module naming to align with Composer semantics.
2. Enforced explicit registration (`ModuleRegistry.register`) instead of filesystem discovery.
3. Kept dependency-aware initialization (`ModuleLoader`) with cycle and missing-dependency handling.
4. Preserved lightweight primitives (`ServiceContainer`, `EventBus`, `CommandDispatcher`) without host UI coupling.
5. Restricted mutation path to adapter-only access through `MutationProvider` and `RuntimeMutationBridgeAdapter`.
6. Implemented safe-mode stub behavior for commit operations to avoid direct runtime writes.
7. Built a minimal workbench seam with top strip + left/center/right columns and placeholder surfaces.

## Rejected Source Files and Why

1. `app/gui_qt/ui_contribution_registry.py`
- Rejected: encodes host-specific dock/menu/toolbar contribution contracts.

2. `app/gui_qt/shell/contribution_bridge.py`
- Rejected: shell bridge is coupled to Repo Analyzer main-window composition.

3. `app/gui_qt/main_window.py`
- Rejected: contains application shell integration not reusable for Composer seed.

4. `app/gui_qt/dock_manager.py`
- Rejected: dock manager is specific to Qt host layout behavior.

5. `app/gui_qt/toolbar_controller.py`
- Rejected: toolbar action model is host-specific and out of seed scope.

6. `app/gui_qt/shell/menu_shell.py`
- Rejected: menu shell integration is host-owned infrastructure.

7. `app/gui_qt/plugins/aegis_deck/**`
- Rejected: Repo Analyzer plugin implementation/demo, not generic kernel.

8. Repo Analyzer demo and product-specific plugins
- Rejected: seed must remain generic and architecture-boundary-safe.
