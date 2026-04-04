# DeltaForge · Master Architecture

## Veredicto
DeltaForge opera como workstation de una sola ventana donde la unidad real es una sesión sobre un scope.

## Canonical runtime entrypoints
- UI entry: `ui/window/main_window.py`
- Bootstrap entry: `bootstrap/app_bootstrap.py`
- Command surface: `ui/widgets/command_bar.py`
- Session tabs: `ui/widgets/session_tabs.py`
- Settings store: `infrastructure/settings_store.py`

## Estructura fija oficial
```text
apps/deltaforge/
  domain/
    ids.py
    events.py
    session_states.py
    models/
      scope.py
      session.py
      ops_document.py
      plan.py
      diff.py
      results.py
      settings.py

  application/
    contracts/
      engine_adapter.py
      event_bus.py
      session_repository.py
    state_machine.py
    stale_policy.py
    refresh_policy.py
    session_actions.py
    workspace_facade.py
    session_manager.py
    selection_service.py
    controllers/
      command_controller.py
      status_bar_controller.py

  infrastructure/
    engine/
      mock_engine_adapter.py
    persistence/
      settings_store.py          # shim-only
      session_layout_store.py
    system/
      file_dialogs.py
      open_path.py
    event_bus_in_memory.py
    file_watcher_polling.py
    settings_store.py            # canonical

  ui/
    theme/
      tokens.py
      semantic_roles.py
      presets.py
      stylesheet.py
      theme_api.py
    primitives/
      buttons.py
      command_button.py          # shim-only
      chip.py
      chips.py                   # shim-only
      section_card.py
      cards.py                   # shim-only
      hairline_separator.py
      separators.py              # shim-only
    panes/
      command_bar.py             # shim-only
      session_tabs.py            # shim-only
    widgets/
      command_bar.py             # canonical
      session_tabs.py            # canonical
      session_workspace.py
    window/
      main_window.py             # canonical
      main_window_alt.py         # shim-only

  bootstrap/
    app_bootstrap.py

  docs/maestro_handoff/
  tests/
    unit/
    contracts/
    smoke/
```

## Wiring mínimo congelado
- `app_bootstrap.py` integra `SessionManager`, `EventBus`, `FileWatcherService`, `EngineAdapter`, tema y `DeltaForgeMainWindow`.
- `main_window.py` integra widgets y controladores; no decide negocio de sesión.
- `SessionWorkspace` es la verdad visible por sesión.

## Legacy quarantine
Legacy permitido solo como shim temporal:
- `ui/window/main_window_alt.py`
- `ui/panes/command_bar.py`
- `ui/panes/session_tabs.py`
- `infrastructure/persistence/settings_store.py`
- `ui/primitives/chips.py`
- `ui/primitives/cards.py`
- `ui/primitives/separators.py`
- `ui/primitives/command_button.py`

Ningún desarrollo nuevo puede aterrizar en esos archivos.
