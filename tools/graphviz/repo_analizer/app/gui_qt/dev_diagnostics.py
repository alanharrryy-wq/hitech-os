from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Any, Callable

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtWidgets import QDockWidget, QMainWindow, QToolBar

_DEBUG_TRUE_VALUES = {'1', 'true', 'yes', 'on'}
_ALL_CHILD_PATTERN = QRegularExpression('.*')


def _coerce_text(value: object) -> str:
    if value is None:
        return ''
    try:
        return str(value).strip()
    except Exception:
        return ''


def _coerce_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _coerce_text(value).lower()
    if not text:
        return False
    return text in _DEBUG_TRUE_VALUES


def resolve_developer_debug_mode(settings: object | None = None) -> bool:
    env_value = os.environ.get('HITECH_QT_DEV_TRACE', '').strip().lower()
    if env_value in _DEBUG_TRUE_VALUES:
        return True

    if settings is not None:
        try:
            raw = settings.value('developer_debug_mode', False)
            if _coerce_bool(raw):
                return True
        except Exception:
            pass

    return False


@dataclass(slots=True)
class StartupStep:
    name: str
    ok: bool = True
    detail: str = ''


@dataclass(slots=True)
class RuntimeWarning:
    channel: str
    message: str
    detail: str = ''


@dataclass(slots=True)
class RuntimeTrace:
    channel: str
    message: str
    detail: str = ''


class RuntimeDiagnostics:
    """Lightweight startup/runtime diagnostics helper for developer velocity."""

    def __init__(
        self,
        *,
        settings: object | None = None,
        logger: Callable[[str], None] | None = None,
    ) -> None:
        self._settings = settings
        self._logger = logger
        self.debug_enabled = resolve_developer_debug_mode(settings)
        self._startup_steps: list[StartupStep] = []
        self._warnings: list[RuntimeWarning] = []
        self._trace_events: list[RuntimeTrace] = []

    def set_debug_mode(self, enabled: bool) -> None:
        self.debug_enabled = bool(enabled)

    def trace(self, channel: str, message: str, **payload: object) -> None:
        detail = ', '.join(
            f'{key}={_coerce_text(value)}'
            for key, value in payload.items()
            if _coerce_text(value)
        )
        self._trace_events.append(RuntimeTrace(channel=channel, message=message, detail=detail))
        if len(self._trace_events) > 500:
            self._trace_events = self._trace_events[-500:]

        if self.debug_enabled:
            text = self._build_message(channel, message, payload)
            self._emit(f'[dev-trace] {text}')

    def warning(self, channel: str, message: str, **payload: object) -> None:
        detail = ', '.join(
            f'{key}={_coerce_text(value)}'
            for key, value in payload.items()
            if _coerce_text(value)
        )
        self._warnings.append(RuntimeWarning(channel=channel, message=message, detail=detail))
        if self.debug_enabled:
            text = self._build_message(channel, message, payload)
            self._emit(f'[dev-warn] {text}')

    def startup_step(self, name: str, *, ok: bool = True, detail: str = '') -> None:
        step = StartupStep(name=name, ok=bool(ok), detail=_coerce_text(detail))
        self._startup_steps.append(step)
        if self.debug_enabled or not step.ok:
            state = 'ok' if step.ok else 'fail'
            suffix = f' ({step.detail})' if step.detail else ''
            self._emit(f'[startup] {name}: {state}{suffix}')

    def get_startup_steps(self) -> list[dict[str, object]]:
        return [asdict(step) for step in self._startup_steps]

    def get_warnings(self) -> list[dict[str, object]]:
        return [asdict(item) for item in self._warnings]

    def get_trace_events(self) -> list[dict[str, object]]:
        return [asdict(item) for item in self._trace_events]

    def build_startup_summary(
        self,
        main_window: QMainWindow,
        *,
        plugin_report: dict[str, object] | None = None,
        integration_report: dict[str, object] | None = None,
    ) -> dict[str, object]:
        state = collect_runtime_state(main_window)
        ok_steps = sum(1 for step in self._startup_steps if step.ok)
        failed_steps = len(self._startup_steps) - ok_steps

        plugin_load_failures = int((plugin_report or {}).get('load_failures_count', 0))
        plugin_init_failures = int((plugin_report or {}).get('init_failures_count', 0))
        integration_failures = int((integration_report or {}).get('failed_total', 0))

        status = 'ok'
        if failed_steps > 0 or plugin_load_failures > 0 or plugin_init_failures > 0 or integration_failures > 0:
            status = 'degraded'

        return {
            'status': status,
            'debug_mode': self.debug_enabled,
            'startup_steps_total': len(self._startup_steps),
            'startup_steps_ok': ok_steps,
            'startup_steps_failed': failed_steps,
            'warnings_total': len(self._warnings),
            'traces_total': len(self._trace_events),
            'runtime_state': state,
            'plugin_report': plugin_report or {},
            'integration_report': integration_report or {},
        }

    def summary_line(self, summary: dict[str, object]) -> str:
        runtime_state = summary.get('runtime_state', {})
        if not isinstance(runtime_state, dict):
            runtime_state = {}
        return (
            f"startup={summary.get('status', 'unknown')} | "
            f"docks={runtime_state.get('dock_count', 0)} | "
            f"plugins={runtime_state.get('plugin_count', 0)} | "
            f"warnings={summary.get('warnings_total', 0)}"
        )

    def _build_message(
        self,
        channel: str,
        message: str,
        payload: dict[str, object],
    ) -> str:
        detail = ', '.join(
            f'{key}={_coerce_text(value)}'
            for key, value in payload.items()
            if _coerce_text(value)
        )
        if detail:
            return f'[{channel}] {message} ({detail})'
        return f'[{channel}] {message}'

    def _emit(self, message: str) -> None:
        if callable(self._logger):
            try:
                self._logger(message)
                return
            except Exception:
                pass
        print(message)


def collect_runtime_state(main_window: QMainWindow) -> dict[str, object]:
    dock_widgets = main_window.findChildren(
        QDockWidget,
        _ALL_CHILD_PATTERN,
        Qt.FindDirectChildrenOnly,
    )
    plugin_dock_count = sum(
        1
        for dock in dock_widgets
        if _coerce_text(dock.objectName()).startswith('plugin_dock_')
    )

    toolbars = main_window.findChildren(
        QToolBar,
        _ALL_CHILD_PATTERN,
        Qt.FindDirectChildrenOnly,
    )

    plugin_count = 0
    plugin_manager = getattr(main_window, 'plugin_manager', None)
    if plugin_manager is not None and hasattr(plugin_manager, 'get_all_plugins'):
        try:
            plugin_count = len(plugin_manager.get_all_plugins())
        except Exception:
            plugin_count = 0

    return {
        'central_widget_ready': main_window.centralWidget() is not None,
        'status_bar_ready': main_window.statusBar() is not None,
        'dock_count': len(dock_widgets),
        'plugin_dock_count': plugin_dock_count,
        'toolbar_count': len(toolbars),
        'plugin_count': plugin_count,
        'has_visual_runtime': hasattr(main_window, 'visual_runtime'),
        'has_shell_bridge': hasattr(main_window, 'shell_contribution_bridge'),
        'has_command_dispatcher': hasattr(main_window, 'command_dispatcher'),
        'has_event_bus': hasattr(main_window, 'event_bus'),
    }
