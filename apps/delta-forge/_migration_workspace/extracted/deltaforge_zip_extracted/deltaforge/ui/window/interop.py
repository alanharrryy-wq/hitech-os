from __future__ import annotations

from typing import Any

UNHANDLED = object()

WORKSPACE_FACADE_PROJECTIONS = {
    'session_tabs': ('get_session_tabs_projection', 'session_tabs_projection', []),
    'active_session_id': ('get_active_session_id', 'active_session_id', None),
    'command_bar': ('get_command_bar_projection', 'command_bar_projection', {}),
    'workspace': ('get_workspace_projection', 'workspace_projection', {}),
    'status': ('get_status_projection', 'status_projection', {}),
}

UI_CONTROLLER_ACTIONS = (
    'create_session',
    'close_session',
    'select_session',
    'browse_root_dir',
    'validate_active',
    'plan_active',
    'apply_active',
    'rollback_active',
    'refresh_active',
    'select_op',
    'select_target',
)


class WorkspaceFacadeBridge:
    def __init__(self, facade: Any) -> None:
        self._facade = facade

    def get_session_tabs_projection(self) -> Any:
        return self._read('session_tabs')

    def get_active_session_id(self) -> Any:
        return self._read('active_session_id')

    def get_command_bar_projection(self) -> Any:
        return self._read('command_bar')

    def get_workspace_projection(self) -> Any:
        return self._read('workspace')

    def get_status_projection(self) -> Any:
        return self._read('status')

    def _read(self, slot: str) -> Any:
        method_name, attribute_name, default = WORKSPACE_FACADE_PROJECTIONS[slot]
        member = getattr(self._facade, method_name, None)
        if callable(member):
            return member()
        value = getattr(self._facade, attribute_name, UNHANDLED)
        if value is not UNHANDLED:
            return value
        return default


class ControllerBridge:
    def __init__(self, controller: Any) -> None:
        self._controller = controller

    def dispatch(self, action: str, *args: Any) -> Any:
        callback = getattr(self._controller, action, None)
        if callable(callback):
            return callback(*args)
        bridge = getattr(self._controller, 'dispatch_ui_action', None)
        if callable(bridge):
            return bridge(action, *args)
        return UNHANDLED

    def __getattr__(self, name: str) -> Any:
        if name not in UI_CONTROLLER_ACTIONS:
            raise AttributeError(name)
        return lambda *args: self.dispatch(name, *args)
