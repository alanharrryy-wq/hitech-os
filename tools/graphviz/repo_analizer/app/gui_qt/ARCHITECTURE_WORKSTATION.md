# Workstation Pre-Visual Mechanics Architecture

This note documents ownership boundaries and runtime contracts after the pre-visual hardening pass.
The goal is structural correctness before any premium visual redesign.

## 1) Product Runtime Model

- Product language: `Tools` (plugin remains internal).
- Host model: fixed workstation shell + flexible tool interiors.
- Runtime invariant: exactly one active tool workspace at a time.
- Tool close semantics: non-destructive (`close -> hide/suspend`, not destroy).
- Startup policy: calm progressive disclosure; secondary shell surfaces start hidden.

## 2) Ownership Boundaries

### Shell-owned infrastructure
- `main_window.py`
  - boot orchestration
  - service registration
  - runtime diagnostics subscriptions
  - preferences/runtime policy application
  - canonical launcher focus entrypoint (`focus_tools_launcher`)
- `toolbar_controller.py`
  - compact top shell rail
  - canonical tool switch combo + launcher button
  - hidden compatibility toolbar for legacy toolbar contributions
- `shell/menu_shell.py`
  - product menus (`Tools`, `Search`, `Inspect`, `Graph`, `Run`, `Settings`)
  - no `View` junk drawer
  - plugin menu path normalization (`Plugins/* -> Tools/Extensions/*`)
- `shell/tool_workspace.py`
  - canonical tool lifecycle runtime
  - single-active-tool invariant enforcement
  - non-destructive close/reopen semantics
  - tool context envelope propagation
- `shell/context_bridge.py`
  - event-to-context synchronization
  - active tool local-context updates
- `shell/status_strip.py`
  - structured operational status strip (activity/tool/repo/scope/results)
- `dock_manager.py` + `layout_manager.py`
  - host dock policy defaults (non-movable/non-floatable for core shell surfaces)
  - startup progressive disclosure behavior

### Tool-owned internals
- Cloudflare Guardian Diagnostics
  - `plugins/cloudflare_guardian/deck_shell.py` (composition)
  - `plugins/cloudflare_guardian/deck_runtime.py` (tab/session orchestration)
  - `plugins/cloudflare_guardian/deck_host_runtime.py` (non-visual host mechanics)
  - `plugins/cloudflare_guardian/snapshot_model.py` + `spec_factory.py` (runtime contracts)
- Orchestrator Bridge
  - `plugins/orchestrator_bridge/plugin.py` (tool shell)
  - `plugins/orchestrator_bridge/process_session_controller.py` (process/session state machine)
  - `bridge_config.py`, `bridge_contract.py`, `bridge_output.py`, `bridge_history.py` (runtime contracts)

## 3) Tool Lifecycle Contract

Canonical operations in `ToolWorkspaceCoordinator`:
- `activate`
- `deactivate`
- `hide`
- `close` (non-destructive)
- `unload`
- `destroy`
- `reopen_last_active_tool`
- `set_tool_enabled`

Events:
- `Events.TOOL_LIFECYCLE_TRANSITION`
- `Events.TOOL_INVARIANT_CORRECTED`
- `Events.TOOL_ACTIVATED`
- `Events.TOOL_DEACTIVATED`

Invariant guard:
- single-active enforcement runs in runtime (not only menu/launcher flow)
- visibility and active-tool state are corrected when edge cases diverge

## 4) Launcher/Switcher Contract

Canonical user entrypoints:
- `Tools -> Open Tools Launcher`
- `Tools -> Switch Active Tool`
- compact top rail tool switch combo

Compatibility:
- plugin toolbar contributions remain supported
- plugin toolbar actions route through hidden compatibility toolbar by default

## 5) Context and Command Contracts

Global context:
- `WorkstationContextRuntime` is the app-wide context source

Bridge:
- `WorkstationContextBridge` maps index/search/preview/tool/command events to context updates
- bridge also pushes active tool local context deltas

Command routing:
- `shell/command_runtime.py` emits dispatch/will-execute/executed/failed events for global command telemetry

## 6) Preferences and Runtime Policy Contracts

Preferences runtime:
- `preferences/runtime.py`
  - normalized persistence model
  - schema version check
  - persistence contract validation
  - settings-center hook payload

Policy derivation:
- `preferences/policy.py`
  - density/motion/performance/high-contrast
  - typography scale
  - spacing scale
  - minimum readable font point size

Policy application:
- `preferences/applicator.py`
  - safe applicator with explicit `RuntimePolicyApplyReport`
  - applies runtime properties to shell and available surfaces without unsafe assumptions

## 7) Startup Shell Structure

Default startup (when tools exist):
- visible:
  - active tool surface
  - tools launcher
  - compact top rail
  - status strip
- hidden/contextual:
  - repository summary
  - preview
  - context inspector
  - explorer/inspector/results/bookmarks rails
  - compatibility toolbar

Fallback startup (no tools available):
- legacy core workspace surfaces are shown

## 8) Technical Debt Reduced in This Pass

- hardcoded orchestrator bridge paths replaced by repo/user-derived defaults
- `bridge_config.json` no longer pins machine-specific absolute paths
- demo/dev legacy plugin load remains hidden by default; skipped noise is no longer logged in normal mode
- host shell no longer exposes free dock-playground defaults for core surfaces
- pycache/pyc cleanup applied under `app/gui_qt`
- tiny typography defaults raised to practical baseline in runtime + base stylesheet tokens

## 9) Remaining Risks Before Beauty Pass

- `plugins/cloudflare_guardian/deck_shell.py` remains large; host/runtime seams exist but visual composition is still concentrated
- `plugins/orchestrator_bridge/plugin.py` remains large; process/session mechanics are separated but UI shell is still dense
- legacy import-mode constraints still affect broad `unittest discover` across `app/gui_qt` package root; targeted suites remain the stable validation path
- broad language normalization is improved in shell surfaces, but some legacy inner-surface strings still need final harmonization

## 10) Future UX Hook Points

- shell redesign:
  - `toolbar_controller.py`
  - `shell/menu_shell.py`
  - `layout_manager.py`
- launcher redesign:
  - `shell/tool_launcher.py`
  - `tools/catalog.py`
- settings center redesign:
  - `preferences/dialog.py` (replaceable UI shell)
  - `preferences/runtime.py` (stable persistence/policy core)
- theme/typography/density redesign:
  - `preferences/policy.py`
  - `preferences/applicator.py`
  - runtime properties (`runtimeTypographyScale`, `runtimeSpacingScale`, `runtimeMinReadableFontPt`)
- telemetry/health:
  - lifecycle/process events in `event_bus.py`
- persistence upgrades:
  - `tools/catalog.py` (tool recents/enabled state)
  - `shell/tool_workspace.py` (active/reopen lifecycle state)
  - orchestrator session history in `bridge_history.py`

