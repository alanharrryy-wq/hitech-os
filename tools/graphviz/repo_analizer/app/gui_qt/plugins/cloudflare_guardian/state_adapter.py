from __future__ import annotations

from dataclasses import asdict, dataclass, field, fields, replace
from pathlib import Path
from typing import Any, Mapping

from PySide6.QtCore import QObject


@dataclass(frozen=True, slots=True)
class CloudflareGuardianDeckSnapshot:
    repo_root: str = ''
    repo_name: str = ''
    repo_ready: bool = False
    index_file_count: int = 0
    index_ext_count: int = 0
    index_elapsed_sec: float = 0.0
    active_scope: str = ''
    active_extension: str = ''
    query_text: str = ''
    results_count: int = 0
    current_preview_relpath: str = ''
    current_preview_path: str = ''
    current_preview_kind: str = ''
    nav_can_go_back: bool = False
    nav_can_go_forward: bool = False
    bookmarks_count: int = 0
    startup_status: str = ''
    warning_count: int = 0
    plugin_count: int = 0
    status_text: str = ''
    subtitle: str = ''
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    hotspots: list[dict[str, Any]] = field(default_factory=list)
    focus_node_id: str = ''


_SNAPSHOT_FIELDS = tuple(item.name for item in fields(CloudflareGuardianDeckSnapshot))
_LIST_FIELDS = {'nodes', 'edges', 'hotspots'}
_BOOL_FIELDS = {'repo_ready', 'nav_can_go_back', 'nav_can_go_forward'}
_INT_FIELDS = {'index_file_count', 'index_ext_count', 'results_count', 'bookmarks_count', 'warning_count', 'plugin_count'}
_FLOAT_FIELDS = {'index_elapsed_sec'}
_EMPTY_SNAPSHOT = CloudflareGuardianDeckSnapshot()
_EMPTY_PAYLOAD = asdict(_EMPTY_SNAPSHOT)
_IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'}
_TEXT_SUFFIXES = {
    '.py', '.pyi', '.js', '.ts', '.tsx', '.jsx', '.json', '.yaml', '.yml', '.toml',
    '.ini', '.cfg', '.conf', '.md', '.txt', '.html', '.css', '.scss', '.xml', '.svg',
    '.ps1', '.sh', '.bat', '.cmd', '.java', '.kt', '.go', '.rs', '.cpp', '.c', '.h', '.hpp',
    '.cs', '.php', '.rb', '.lua', '.sql', '.csv', '.tsv', '.lock', '.gitignore', '.env',
}


class CloudflareGuardianStateAdapter(QObject):
    """Conservative host reader that emits canonical empty-valid snapshots."""

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._main_window: object | None = None
        self._container: object | None = None
        self._event_bus: object | None = None
        self._last_snapshot = CloudflareGuardianDeckSnapshot()

    def attach_context(
        self,
        main_window: object | None = None,
        *,
        container: object | None = None,
        event_bus: object | None = None,
        **_: object,
    ) -> None:
        if main_window is not None:
            self._main_window = main_window
        if container is not None:
            self._container = container
        if event_bus is not None:
            self._event_bus = event_bus

    def build_snapshot(self) -> CloudflareGuardianDeckSnapshot:
        main_window = self._resolve_main_window()
        index_data = self._mapping_attr(main_window, 'index_data')
        startup_summary = self._startup_summary(main_window)
        plugin_report = self._plugin_report(main_window, startup_summary)
        runtime_warnings = self._runtime_warnings(main_window)

        repo_root = self._resolve_repo_root(main_window, index_data)
        repo_name = Path(repo_root).name if repo_root else ''
        index_file_count = self._safe_len(index_data.get('files'))
        index_ext_count = self._safe_len(index_data.get('ext_counts'))
        index_elapsed_sec = self._float_from_mapping(index_data.get('stats'), 'elapsed_sec')
        active_scope = self._combo_text(main_window, 'folder_combo')
        active_extension = self._combo_text(main_window, 'ext_combo')
        query_text = self._line_text(main_window, 'search_box')
        results_count = self._resolve_results_count(main_window)
        current_preview_relpath = self._text_attr(main_window, 'current_preview_rel')
        current_preview_path = self._text_attr(main_window, 'current_preview_path')
        current_preview_kind = self._preview_kind(current_preview_path, current_preview_relpath)
        nav_can_go_back = self._resolve_nav_flag(main_window, direction='back')
        nav_can_go_forward = self._resolve_nav_flag(main_window, direction='forward')
        bookmarks_count = self._resolve_bookmarks_count(main_window)
        startup_status = self._resolve_startup_status(startup_summary, plugin_report)
        warning_count = self._resolve_warning_count(runtime_warnings, startup_summary, plugin_report)
        plugin_count = self._resolve_plugin_count(main_window, startup_summary, plugin_report)
        repo_ready = bool(index_data.get('root') or index_file_count or repo_root)

        snapshot = CloudflareGuardianDeckSnapshot(
            repo_root=repo_root,
            repo_name=repo_name,
            repo_ready=repo_ready,
            index_file_count=index_file_count,
            index_ext_count=index_ext_count,
            index_elapsed_sec=index_elapsed_sec,
            active_scope=active_scope,
            active_extension=active_extension,
            query_text=query_text,
            results_count=results_count,
            current_preview_relpath=current_preview_relpath,
            current_preview_path=current_preview_path,
            current_preview_kind=current_preview_kind,
            nav_can_go_back=nav_can_go_back,
            nav_can_go_forward=nav_can_go_forward,
            bookmarks_count=bookmarks_count,
            startup_status=startup_status,
            warning_count=warning_count,
            plugin_count=plugin_count,
            status_text='',
            subtitle='',
            nodes=[],
            edges=[],
            hotspots=[],
            focus_node_id='',
        )
        payload = snapshot_payload(snapshot)
        status_text = self._resolve_status_text(main_window, payload)
        subtitle = self._resolve_subtitle(main_window, payload)
        return replace(snapshot, status_text=status_text, subtitle=subtitle)

    def refresh_snapshot(self) -> CloudflareGuardianDeckSnapshot:
        self._last_snapshot = self.build_snapshot()
        return self._last_snapshot

    def get_last_snapshot(self) -> CloudflareGuardianDeckSnapshot:
        return self._last_snapshot

    def snapshot_payload(self) -> dict[str, Any]:
        return snapshot_payload(self._last_snapshot)

    def shutdown(self) -> None:
        self._main_window = None
        self._container = None
        self._event_bus = None
        self._last_snapshot = CloudflareGuardianDeckSnapshot()

    def _resolve_main_window(self) -> object | None:
        if self._main_window is not None:
            return self._main_window
        container = self._container
        getter = getattr(container, 'get', None)
        if callable(getter):
            try:
                resolved = getter('main_window')
            except Exception:
                resolved = None
            if resolved is not None:
                self._main_window = resolved
                return resolved
        return None

    @staticmethod
    def _mapping_attr(target: object | None, name: str) -> Mapping[str, Any]:
        value = getattr(target, name, None)
        return value if isinstance(value, Mapping) else {}

    @staticmethod
    def _text_attr(target: object | None, name: str) -> str:
        return _coerce_text(getattr(target, name, ''))

    def _startup_summary(self, main_window: object | None) -> Mapping[str, Any]:
        summary = getattr(main_window, '_startup_health_summary', None)
        if isinstance(summary, Mapping) and summary:
            return summary
        snapshot_getter = getattr(main_window, 'get_developer_diagnostics_snapshot', None)
        if callable(snapshot_getter):
            try:
                snapshot = snapshot_getter()
            except Exception:
                snapshot = {}
            if isinstance(snapshot, Mapping):
                summary = snapshot.get('startup_summary', {})
                if isinstance(summary, Mapping):
                    return summary
        return {}

    def _plugin_report(
        self,
        main_window: object | None,
        startup_summary: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        summary_report = startup_summary.get('plugin_report', {})
        if isinstance(summary_report, Mapping) and summary_report:
            return summary_report
        plugin_manager = getattr(main_window, 'plugin_manager', None)
        getter = getattr(plugin_manager, 'get_diagnostics_report', None)
        if callable(getter):
            try:
                report = getter()
            except Exception:
                report = {}
            if isinstance(report, Mapping):
                return report
        return {}

    def _resolve_repo_root(
        self,
        main_window: object | None,
        index_data: Mapping[str, Any],
    ) -> str:
        indexed_root = _coerce_text(index_data.get('root', ''))
        if indexed_root:
            return indexed_root
        repo_combo = getattr(main_window, 'repo_combo', None)
        if repo_combo is not None and hasattr(repo_combo, 'currentText'):
            try:
                repo_text = _coerce_text(repo_combo.currentText())
            except Exception:
                repo_text = ''
            if repo_text:
                return repo_text
        return self._text_attr(main_window, '_repo_path')

    def _combo_text(self, main_window: object | None, name: str) -> str:
        widget = getattr(main_window, name, None)
        if widget is None or not hasattr(widget, 'currentText'):
            return ''
        try:
            return _coerce_text(widget.currentText())
        except Exception:
            return ''

    def _line_text(self, main_window: object | None, name: str) -> str:
        widget = getattr(main_window, name, None)
        if widget is None or not hasattr(widget, 'text'):
            return ''
        try:
            return _coerce_text(widget.text())
        except Exception:
            return ''

    @staticmethod
    def _safe_len(value: object) -> int:
        try:
            return len(value) if value is not None else 0
        except Exception:
            return 0

    @staticmethod
    def _float_from_mapping(mapping_value: object, key: str) -> float:
        if isinstance(mapping_value, Mapping):
            return _coerce_float(mapping_value.get(key, 0.0))
        return 0.0

    def _resolve_results_count(self, main_window: object | None) -> int:
        direct_results = getattr(main_window, 'search_results', None)
        count = self._safe_len(direct_results)
        if count:
            return count
        results_model = getattr(main_window, 'results_model', None)
        if results_model is not None and hasattr(results_model, 'rowCount'):
            try:
                return _coerce_int(results_model.rowCount())
            except Exception:
                return 0
        return 0

    def _resolve_nav_flag(self, main_window: object | None, *, direction: str) -> bool:
        controller = getattr(main_window, 'navigation_controller', None)
        history = getattr(controller, '_preview_history', None)
        index = getattr(controller, '_preview_history_index', -1)
        if not isinstance(history, list):
            history = []
        try:
            index_value = int(index)
        except Exception:
            index_value = -1
        if direction == 'back':
            return bool(index_value > 0 and history)
        return bool(index_value >= 0 and index_value < (len(history) - 1))

    def _resolve_bookmarks_count(self, main_window: object | None) -> int:
        bookmarks_list = getattr(main_window, 'bookmarks_list', None)
        if bookmarks_list is not None and hasattr(bookmarks_list, 'count'):
            try:
                return _coerce_int(bookmarks_list.count())
            except Exception:
                pass

        backend = getattr(main_window, 'backend', None)
        repo_combo = getattr(main_window, 'repo_combo', None)
        getter = getattr(backend, 'get_repo_bookmarks', None)
        if callable(getter) and repo_combo is not None and hasattr(repo_combo, 'currentText'):
            try:
                repo_name = _coerce_text(repo_combo.currentText())
                return self._safe_len(getter(repo_name))
            except Exception:
                return 0
        return 0

    def _runtime_warnings(self, main_window: object | None) -> list[Mapping[str, Any]]:
        diagnostics = getattr(main_window, 'runtime_diagnostics', None)
        getter = getattr(diagnostics, 'get_warnings', None)
        if callable(getter):
            try:
                warnings = getter()
            except Exception:
                warnings = []
            if isinstance(warnings, list):
                return [item for item in warnings if isinstance(item, Mapping)]
        return []

    def _resolve_startup_status(
        self,
        startup_summary: Mapping[str, Any],
        plugin_report: Mapping[str, Any],
    ) -> str:
        status = _coerce_text(startup_summary.get('status', ''))
        if status:
            return status
        failed_steps = _coerce_int(startup_summary.get('startup_steps_failed', 0))
        plugin_failures = (
            _coerce_int(plugin_report.get('load_failures_count', 0))
            + _coerce_int(plugin_report.get('init_failures_count', 0))
            + _coerce_int(plugin_report.get('manifest_validation_failures_count', 0))
        )
        if failed_steps > 0 or plugin_failures > 0:
            return 'degraded'
        if _coerce_int(startup_summary.get('startup_steps_total', 0)) > 0:
            return 'ok'
        return ''

    def _resolve_warning_count(
        self,
        runtime_warnings: list[Mapping[str, Any]],
        startup_summary: Mapping[str, Any],
        plugin_report: Mapping[str, Any],
    ) -> int:
        plugin_issues = (
            _coerce_int(plugin_report.get('load_failures_count', 0))
            + _coerce_int(plugin_report.get('init_failures_count', 0))
            + _coerce_int(plugin_report.get('contract_warnings_count', 0))
            + _coerce_int(plugin_report.get('manifest_validation_failures_count', 0))
        )
        summary_warnings = _coerce_int(startup_summary.get('warnings_total', 0))
        return max(summary_warnings, len(runtime_warnings)) + plugin_issues

    def _resolve_plugin_count(
        self,
        main_window: object | None,
        startup_summary: Mapping[str, Any],
        plugin_report: Mapping[str, Any],
    ) -> int:
        loaded_count = _coerce_int(plugin_report.get('loaded_plugins_count', 0))
        if loaded_count:
            return loaded_count
        runtime_state = startup_summary.get('runtime_state', {})
        if isinstance(runtime_state, Mapping):
            state_count = _coerce_int(runtime_state.get('plugin_count', 0))
            if state_count:
                return state_count
        plugin_manager = getattr(main_window, 'plugin_manager', None)
        getter = getattr(plugin_manager, 'get_all_plugins', None)
        if callable(getter):
            try:
                plugins = getter()
            except Exception:
                plugins = {}
            if isinstance(plugins, Mapping):
                return len(plugins)
        return 0

    def _busy_status_text(self, main_window: object | None) -> str:
        progress_bar = getattr(main_window, 'progress_bar', None)
        visible = False
        if progress_bar is not None and hasattr(progress_bar, 'isVisible'):
            try:
                visible = bool(progress_bar.isVisible())
            except Exception:
                visible = False
        if not visible:
            return ''
        status_bar_text = self._status_bar_message(main_window)
        if status_bar_text:
            return status_bar_text
        return 'Background task running'

    def _status_bar_message(self, main_window: object | None) -> str:
        status_bar_getter = getattr(main_window, 'statusBar', None)
        if not callable(status_bar_getter):
            return ''
        try:
            status_bar = status_bar_getter()
        except Exception:
            return ''
        if status_bar is None or not hasattr(status_bar, 'currentMessage'):
            return ''
        try:
            return _coerce_text(status_bar.currentMessage())
        except Exception:
            return ''

    def _resolve_status_text(self, main_window: object | None, payload: Mapping[str, Any]) -> str:
        if main_window is None:
            return 'Awaiting Cloudflare Guardian Diagnostics host context'

        busy_status = self._busy_status_text(main_window)
        if busy_status:
            return busy_status

        warning_count = _coerce_int(payload.get('warning_count', 0))
        if _coerce_text(payload.get('startup_status', '')) == 'degraded':
            if warning_count > 0:
                return f'Runtime degraded • {warning_count} issues detected'
            return 'Runtime degraded'

        preview_relpath = _coerce_text(payload.get('current_preview_relpath', ''))
        if preview_relpath:
            return f'Preview ready • {Path(preview_relpath).name}'

        query_text = _coerce_text(payload.get('query_text', ''))
        results_count = _coerce_int(payload.get('results_count', 0))
        if query_text:
            if results_count > 0:
                return f'Search ready • {results_count} matches'
            return 'Search ready • no matches'

        file_count = _coerce_int(payload.get('index_file_count', 0))
        if _coerce_bool(payload.get('repo_ready', False)) and file_count > 0:
            return f'Workspace indexed • {file_count} files'

        repo_root = _coerce_text(payload.get('repo_root', ''))
        if repo_root:
            return 'Repository selected • awaiting index'

        scope_label = self._label_text(main_window, 'status_scope_label')
        if scope_label:
            return scope_label

        return 'Awaiting repository selection'

    def _resolve_subtitle(self, main_window: object | None, payload: Mapping[str, Any]) -> str:
        if main_window is None:
            return 'Attach host context or expose container.get("main_window") before requesting snapshots.'

        busy_status = self._busy_status_text(main_window)
        if busy_status:
            parts = [busy_status]
            summary_line = self._label_text(main_window, 'status_summary')
            if summary_line:
                parts.append(summary_line)
            scope_line = self._label_text(main_window, 'status_scope_label')
            if scope_line:
                parts.append(scope_line)
            return _join_parts(parts)

        preview_relpath = _coerce_text(payload.get('current_preview_relpath', ''))
        if preview_relpath:
            parts = [preview_relpath]
            preview_kind = _coerce_text(payload.get('current_preview_kind', ''))
            if preview_kind:
                parts.append(preview_kind)
            if _coerce_bool(payload.get('nav_can_go_back', False)) or _coerce_bool(payload.get('nav_can_go_forward', False)):
                parts.append(
                    f"history b:{_coerce_bool(payload.get('nav_can_go_back', False))} f:{_coerce_bool(payload.get('nav_can_go_forward', False))}"
                )
            if _coerce_text(payload.get('query_text', '')):
                parts.append(f"query {_truncate(_coerce_text(payload.get('query_text', '')), 42)}")
            if _coerce_int(payload.get('warning_count', 0)) > 0:
                parts.append(f"{_coerce_int(payload.get('warning_count', 0))} warnings")
            return _join_parts(parts)

        query_text = _coerce_text(payload.get('query_text', ''))
        if query_text:
            parts = [f"query {_truncate(query_text, 56)}"]
            parts.append(f"{_coerce_int(payload.get('results_count', 0))} results")
            scope = _coerce_text(payload.get('active_scope', ''))
            if scope:
                parts.append(scope)
            extension = _coerce_text(payload.get('active_extension', ''))
            if extension:
                parts.append(f"ext {extension}")
            return _join_parts(parts)

        repo_root = _coerce_text(payload.get('repo_root', ''))
        if repo_root:
            parts = [_coerce_text(payload.get('repo_name', '')) or repo_root]
            file_count = _coerce_int(payload.get('index_file_count', 0))
            ext_count = _coerce_int(payload.get('index_ext_count', 0))
            if file_count > 0:
                parts.append(f"{file_count} files")
            if ext_count > 0:
                parts.append(f"{ext_count} extensions")
            elapsed = _coerce_float(payload.get('index_elapsed_sec', 0.0))
            if elapsed > 0:
                parts.append(f"{elapsed:.2f}s")
            scope = _coerce_text(payload.get('active_scope', ''))
            if scope:
                parts.append(scope)
            extension = _coerce_text(payload.get('active_extension', ''))
            if extension:
                parts.append(f"ext {extension}")
            bookmarks = _coerce_int(payload.get('bookmarks_count', 0))
            if bookmarks > 0:
                parts.append(f"{bookmarks} bookmarks")
            plugins = _coerce_int(payload.get('plugin_count', 0))
            if plugins > 0:
                parts.append(f"{plugins} plugins")
            warnings = _coerce_int(payload.get('warning_count', 0))
            if warnings > 0:
                parts.append(f"{warnings} warnings")
            return _join_parts(parts)

        scope_label = self._label_text(main_window, 'status_scope_label')
        if scope_label:
            return scope_label

        return 'No repository has been indexed yet.'

    def _label_text(self, main_window: object | None, name: str) -> str:
        label = getattr(main_window, name, None)
        if label is None or not hasattr(label, 'text'):
            return ''
        try:
            return _coerce_text(label.text())
        except Exception:
            return ''

    @staticmethod
    def _preview_kind(current_preview_path: str, current_preview_relpath: str) -> str:
        candidate = current_preview_path or current_preview_relpath
        suffix = Path(candidate).suffix.lower() if candidate else ''
        if not suffix:
            return ''
        if suffix == '.svg':
            return 'svg'
        if suffix in _IMAGE_SUFFIXES:
            return 'image'
        if suffix in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}:
            return 'config'
        if suffix in {'.md', '.txt'}:
            return 'document'
        if suffix in {'.csv', '.tsv'}:
            return 'data'
        if suffix in _TEXT_SUFFIXES:
            return 'code'
        return suffix.lstrip('.')



def snapshot_payload(snapshot: CloudflareGuardianDeckSnapshot | Mapping[str, Any] | object) -> dict[str, Any]:
    if isinstance(snapshot, CloudflareGuardianDeckSnapshot):
        source: Mapping[str, Any] = asdict(snapshot)
    elif isinstance(snapshot, Mapping):
        source = snapshot
    else:
        source = {
            field_name: getattr(snapshot, field_name, _EMPTY_PAYLOAD[field_name])
            for field_name in _SNAPSHOT_FIELDS
        }

    payload: dict[str, Any] = {}
    for field_name in _SNAPSHOT_FIELDS:
        value = source.get(field_name, _EMPTY_PAYLOAD[field_name])
        payload[field_name] = _normalize_field(field_name, value)
    return payload



def _normalize_field(field_name: str, value: object) -> Any:
    if field_name in _LIST_FIELDS:
        if isinstance(value, list):
            return list(value)
        if isinstance(value, tuple):
            return list(value)
        return []
    if field_name in _BOOL_FIELDS:
        return _coerce_bool(value)
    if field_name in _INT_FIELDS:
        return _coerce_int(value)
    if field_name in _FLOAT_FIELDS:
        return _coerce_float(value)
    return _coerce_text(value)



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
    return text in {'1', 'true', 'yes', 'on'}



def _coerce_int(value: object) -> int:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    text = _coerce_text(value)
    if not text:
        return 0
    try:
        return int(float(text))
    except Exception:
        return 0



def _coerce_float(value: object) -> float:
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    text = _coerce_text(value)
    if not text:
        return 0.0
    try:
        return float(text)
    except Exception:
        return 0.0



def _join_parts(parts: list[str]) -> str:
    return ' • '.join(part for part in parts if part)



def _truncate(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)].rstrip() + '…'


__all__ = ['CloudflareGuardianDeckSnapshot', 'CloudflareGuardianStateAdapter', 'snapshot_payload']

