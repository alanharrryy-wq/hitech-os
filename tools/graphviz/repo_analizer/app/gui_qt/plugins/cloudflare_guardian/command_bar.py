from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

from PySide6.QtCore import QEvent, QObject, QTimer, Qt, Signal
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .theme_bridge import DeckThemeBridge

_MISSING = object()


@dataclass(frozen=True, slots=True)
class _CommandSpec:
    name: str
    title: str
    description: str
    shortcut: str
    keywords: tuple[str, ...]
    payload: dict[str, Any]
    enabled: bool
    visible: bool


@dataclass(frozen=True, slots=True)
class _CommandMatch:
    spec: _CommandSpec
    index: int
    score: int


class _CommandRowWidget(QFrame):
    def __init__(
        self,
        *,
        select_callback: Callable[[], None],
        activate_callback: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._select_callback = select_callback
        self._activate_callback = activate_callback
        self._enabled = True
        self._hovered = False
        self._theme_bridge = DeckThemeBridge.coerce(None)

        self.setObjectName('cloudflare_guardianCommandRow')
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty('selected', False)
        self.setProperty('hovered', False)
        self.setProperty('enabledState', True)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(6)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        root.addLayout(top)

        self._title_label = QLabel(self)
        self._title_label.setObjectName('cloudflare_guardianCommandRowTitle')
        self._title_label.setTextFormat(Qt.RichText)
        self._title_label.setWordWrap(True)
        self._title_label.setTextInteractionFlags(Qt.NoTextInteraction)
        top.addWidget(self._title_label, 1)

        self._shortcut_label = QLabel(self)
        self._shortcut_label.setObjectName('cloudflare_guardianCommandRowShortcut')
        self._shortcut_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        top.addWidget(self._shortcut_label, 0)

        mid = QHBoxLayout()
        mid.setContentsMargins(0, 0, 0, 0)
        mid.setSpacing(8)
        root.addLayout(mid)

        self._description_label = QLabel(self)
        self._description_label.setObjectName('cloudflare_guardianCommandRowDescription')
        self._description_label.setTextFormat(Qt.RichText)
        self._description_label.setWordWrap(True)
        self._description_label.setTextInteractionFlags(Qt.NoTextInteraction)
        mid.addWidget(self._description_label, 1)

        self._state_label = QLabel(self)
        self._state_label.setObjectName('cloudflare_guardianCommandRowState')
        self._state_label.setAlignment(Qt.AlignCenter)
        self._state_label.setProperty('tone', 'ready')
        mid.addWidget(self._state_label, 0)

        self._keywords_label = QLabel(self)
        self._keywords_label.setObjectName('cloudflare_guardianCommandRowKeywords')
        self._keywords_label.setTextFormat(Qt.RichText)
        self._keywords_label.setWordWrap(True)
        self._keywords_label.setTextInteractionFlags(Qt.NoTextInteraction)
        root.addWidget(self._keywords_label)

    def set_theme_tokens(self, tokens: object | None) -> None:
        self._theme_bridge = DeckThemeBridge.coerce(tokens)

    def bind(self, spec: _CommandSpec, terms: tuple[str, ...]) -> None:
        self._enabled = spec.enabled
        self._title_label.setText(self._highlight_html(spec.title or spec.name, terms, bold=True))
        self._description_label.setText(self._description_html(spec.description, terms))
        self._shortcut_label.setVisible(bool(spec.shortcut))
        if spec.shortcut:
            self._shortcut_label.setText(html.escape(spec.shortcut))
        self._keywords_label.setText(self._keywords_html(spec.keywords, terms))
        self._keywords_label.setVisible(bool(spec.keywords))
        if spec.enabled:
            self._state_label.setText('READY')
            self._state_label.setProperty('tone', 'ready')
        else:
            self._state_label.setText('LOCKED')
            self._state_label.setProperty('tone', 'disabled')
        self.setProperty('enabledState', spec.enabled)
        self._repolish(self._state_label)
        self._repolish(self)

    def set_selected(self, selected: bool) -> None:
        self.setProperty('selected', bool(selected))
        self._repolish(self)

    def enterEvent(self, event: QEvent) -> None:  # noqa: N802
        self._hovered = True
        self.setProperty('hovered', True)
        self._repolish(self)
        self._select_callback()
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:  # noqa: N802
        self._hovered = False
        self.setProperty('hovered', False)
        self._repolish(self)
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._select_callback()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton and self._enabled:
            self._select_callback()
            self._activate_callback()
        super().mouseDoubleClickEvent(event)

    def _description_html(self, text: str, terms: tuple[str, ...]) -> str:
        if not text:
            muted = self._theme_bridge.token('text_soft')
            return f'<span style="color:{muted};">No description provided.</span>'
        return self._highlight_html(text, terms, bold=False)

    def _keywords_html(self, keywords: Sequence[str], terms: tuple[str, ...]) -> str:
        if not keywords:
            return ''
        chips: list[str] = []
        highlight_ink = self._theme_bridge.token('accent')
        muted_ink = self._theme_bridge.token('text_muted')
        highlight_bg = self._theme_bridge.css_color('accent_soft', alpha=226)
        muted_bg = self._theme_bridge.css_color('panel', alpha=214)
        highlight_border = self._theme_bridge.accent_mix('border_strong', 0.58)
        muted_border = self._theme_bridge.token('border')
        for keyword in keywords[:6]:
            tone = highlight_ink if keyword.lower() in terms else muted_ink
            bg = highlight_bg if keyword.lower() in terms else muted_bg
            border = highlight_border if keyword.lower() in terms else muted_border
            chips.append(
                '<span style="'
                f'background:{bg}; color:{tone}; border:1px solid {border}; '
                'padding:2px 8px; border-radius:10px;">'
                f'{html.escape(keyword)}</span>'
            )
        return ' '.join(chips)

    def _highlight_html(self, text: str, terms: tuple[str, ...], *, bold: bool) -> str:
        escaped = html.escape(text or '')
        if not terms:
            if bold:
                return f'<span style="font-weight:600;">{escaped}</span>'
            return escaped
        pattern = '|'.join(re.escape(term) for term in sorted(set(terms), key=len, reverse=True) if term)
        if not pattern:
            return escaped

        def _replace(match: re.Match[str]) -> str:
            token = match.group(0)
            highlight_color = self._theme_bridge.token('accent')
            highlight_bg = self._theme_bridge.accent_mix('panel_alt', 0.36)
            return (
                f'<span style="color:{highlight_color}; font-weight:700; '
                f'background:{highlight_bg}; border-radius:6px; padding:0 2px;">'
                f'{html.escape(token)}</span>'
            )

        highlighted = re.sub(pattern, _replace, escaped, flags=re.IGNORECASE)
        if bold:
            return f'<span style="font-weight:600;">{highlighted}</span>'
        return highlighted

    def _repolish(self, widget: QWidget) -> None:
        style = widget.style()
        if style is not None:
            style.unpolish(widget)
            style.polish(widget)
        widget.update()


class CloudflareGuardianCommandBar(QWidget):
    commandActivated = Signal(str, object)
    commandHighlighted = Signal(str, object)
    queryEdited = Signal(str)
    executionFailed = Signal(str, object)

    _ALIASES: dict[str, tuple[str, ...]] = {
        'name': ('command_id', 'id', 'contribution_id'),
        'title': ('label', 'text'),
        'description': ('tooltip', 'summary', 'help'),
        'shortcut': ('key_sequence', 'key', 'hotkey'),
        'keywords': ('tags', 'search_terms'),
        'payload': ('data', 'args'),
        'enabled': ('is_enabled', 'disabled'),
        'visible': ('is_visible', 'hidden'),
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._dispatcher: Any | None = None
        self._context: dict[str, Any] = {}
        self._theme_bridge = DeckThemeBridge.coerce(None)
        self._all_commands: list[_CommandSpec] = []
        self._filtered_matches: list[_CommandMatch] = []
        self._row_widgets: dict[str, _CommandRowWidget] = {}
        self._items_by_name: dict[str, QListWidgetItem] = {}
        self._selection_signal_muted = False
        self._status_override: tuple[str, str] | None = None
        self._status_reset_serial = 0

        self.setObjectName('cloudflare_guardianCommandBar')
        self.setProperty('visualRole', 'command-surface')
        self.setProperty('visualTier', 'themed')
        self.setStyleSheet(self._build_stylesheet())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        shell = QFrame(self)
        shell.setObjectName('cloudflare_guardianCommandBarShell')
        shell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        shell.setMinimumHeight(260)
        root.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(14, 14, 14, 14)
        shell_layout.setSpacing(10)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)
        shell_layout.addLayout(header_row)

        self._header_label = QLabel('Command Bar', shell)
        self._header_label.setObjectName('cloudflare_guardianCommandBarHeader')
        header_row.addWidget(self._header_label, 1)

        self._count_label = QLabel('0', shell)
        self._count_label.setObjectName('cloudflare_guardianCommandBarCount')
        self._count_label.setAlignment(Qt.AlignCenter)
        header_row.addWidget(self._count_label, 0)

        self._status_label = QLabel('Awaiting commands', shell)
        self._status_label.setObjectName('cloudflare_guardianCommandBarStatus')
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setProperty('tone', 'idle')
        header_row.addWidget(self._status_label, 0)

        self._query_edit = QLineEdit(shell)
        self._query_edit.setObjectName('cloudflare_guardianCommandBarInput')
        self._query_edit.setClearButtonEnabled(True)
        self._query_edit.setPlaceholderText('Search commands, shortcuts, or keywords')
        self._query_edit.textChanged.connect(self._on_query_changed)
        self._query_edit.installEventFilter(self)
        shell_layout.addWidget(self._query_edit)

        self._hint_label = QLabel('Enter runs the current command. Up/Down moves selection. Esc clears.', shell)
        self._hint_label.setObjectName('cloudflare_guardianCommandBarHint')
        shell_layout.addWidget(self._hint_label)

        self._list = QListWidget(shell)
        self._list.setObjectName('cloudflare_guardianCommandBarList')
        self._list.setAlternatingRowColors(False)
        self._list.setSelectionMode(QAbstractItemView.SingleSelection)
        self._list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self._list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._list.setFocusPolicy(Qt.NoFocus)
        self._list.itemActivated.connect(self._on_item_activated)
        self._list.currentItemChanged.connect(self._on_current_item_changed)
        self._list.setMinimumHeight(190)
        shell_layout.addWidget(self._list, 1)

        self._empty_label = QLabel('No commands available.', shell)
        self._empty_label.setObjectName('cloudflare_guardianCommandBarEmpty')
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setWordWrap(True)
        shell_layout.addWidget(self._empty_label)

        self._detail_panel = QFrame(shell)
        self._detail_panel.setObjectName('cloudflare_guardianCommandBarDetail')
        self._detail_panel.setMinimumHeight(108)
        detail_layout = QVBoxLayout(self._detail_panel)
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(6)
        shell_layout.addWidget(self._detail_panel)

        detail_header = QHBoxLayout()
        detail_header.setContentsMargins(0, 0, 0, 0)
        detail_header.setSpacing(8)
        detail_layout.addLayout(detail_header)

        self._detail_title = QLabel('No command selected', self._detail_panel)
        self._detail_title.setObjectName('cloudflare_guardianCommandBarDetailTitle')
        detail_header.addWidget(self._detail_title, 1)

        self._detail_badge = QLabel('IDLE', self._detail_panel)
        self._detail_badge.setObjectName('cloudflare_guardianCommandBarDetailBadge')
        self._detail_badge.setAlignment(Qt.AlignCenter)
        self._detail_badge.setProperty('tone', 'idle')
        detail_header.addWidget(self._detail_badge, 0)

        self._detail_meta = QLabel('Load command specs to begin.', self._detail_panel)
        self._detail_meta.setObjectName('cloudflare_guardianCommandBarDetailMeta')
        self._detail_meta.setWordWrap(True)
        detail_layout.addWidget(self._detail_meta)

        self._detail_payload = QLabel('', self._detail_panel)
        self._detail_payload.setObjectName('cloudflare_guardianCommandBarDetailPayload')
        self._detail_payload.setWordWrap(True)
        self._detail_payload.setTextFormat(Qt.RichText)
        detail_layout.addWidget(self._detail_payload)

        self.refresh_commands()

    def set_dispatcher(self, dispatcher: Any) -> None:
        self._dispatcher = dispatcher
        self._refresh_status_banner()

    def set_skin(self, tokens: object | None) -> None:
        self.set_theme_tokens(tokens)

    def set_theme_tokens(self, tokens: object | None) -> None:
        self._theme_bridge = DeckThemeBridge.coerce(tokens)
        self.setStyleSheet(self._build_stylesheet())
        self.refresh_commands()

    def set_command_specs(self, commands: Iterable[object] | None) -> None:
        normalized: list[_CommandSpec] = []
        seen_names: set[str] = set()
        for raw in commands or []:
            spec = self._normalize_command(raw)
            if spec is None:
                continue
            if spec.name in seen_names:
                continue
            seen_names.add(spec.name)
            normalized.append(spec)
        self._all_commands = normalized
        self.refresh_commands()

    def refresh_commands(self) -> None:
        query_terms = self._query_terms(self.query())
        matches: list[_CommandMatch] = []
        for index, spec in enumerate(self._all_commands):
            if not spec.visible:
                continue
            match = self._match_command(spec, query_terms, index)
            if match is not None:
                matches.append(match)
        matches.sort(key=lambda item: (-item.score, item.index))
        self._filtered_matches = matches
        self._rebuild_list()

    def update_context(self, context: Mapping[str, Any] | None) -> None:
        self._context = self._coerce_mapping(context)
        self._refresh_detail_panel(self._current_spec())

    def focus_input(self, select_all: bool = True) -> None:
        self._query_edit.setFocus(Qt.OtherFocusReason)
        if select_all:
            self._query_edit.selectAll()

    def set_query(self, text: str) -> None:
        normalized = '' if text is None else str(text)
        if self._query_edit.text() == normalized:
            return
        self._query_edit.setText(normalized)

    def query(self) -> str:
        return self._query_edit.text()

    def clear_query(self) -> None:
        self._query_edit.clear()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._query_edit and event.type() == QEvent.KeyPress:
            key_event = event if isinstance(event, QKeyEvent) else None
            if key_event is not None:
                key = key_event.key()
                if key in (Qt.Key_Down, Qt.Key_Up):
                    self._step_selection(1 if key == Qt.Key_Down else -1)
                    return True
                if key in (Qt.Key_PageDown, Qt.Key_PageUp):
                    self._step_selection(5 if key == Qt.Key_PageDown else -5)
                    return True
                if key == Qt.Key_Home:
                    self._jump_to_edge(first=True)
                    return True
                if key == Qt.Key_End:
                    self._jump_to_edge(first=False)
                    return True
                if key in (Qt.Key_Return, Qt.Key_Enter):
                    self._activate_current_command()
                    return True
                if key == Qt.Key_Escape:
                    if self.query():
                        self.clear_query()
                    else:
                        self._jump_to_edge(first=True)
                    return True
        return super().eventFilter(watched, event)

    def _on_query_changed(self, text: str) -> None:
        self.queryEdited.emit(text)
        self.refresh_commands()

    def _rebuild_list(self) -> None:
        query_terms = self._query_terms(self.query())
        self._selection_signal_muted = True
        try:
            self._list.clear()
            self._row_widgets.clear()
            self._items_by_name.clear()
            for match in self._filtered_matches:
                spec = match.spec
                item = QListWidgetItem()
                item.setData(Qt.UserRole, spec.name)
                item.setData(Qt.UserRole + 1, dict(spec.payload))
                item.setToolTip(self._tooltip_text(spec))
                row_widget = _CommandRowWidget(
                    select_callback=lambda name=spec.name: self._select_command_by_name(name),
                    activate_callback=lambda name=spec.name: self._activate_command_by_name(name),
                    parent=self._list,
                )
                row_widget.set_theme_tokens(self._theme_bridge)
                row_widget.bind(spec, query_terms)
                item.setSizeHint(row_widget.sizeHint())
                self._list.addItem(item)
                self._list.setItemWidget(item, row_widget)
                self._row_widgets[spec.name] = row_widget
                self._items_by_name[spec.name] = item
            enabled_count = sum(1 for item in self._filtered_matches if item.spec.enabled)
            self._count_label.setText(f'{len(self._filtered_matches)} / {len(self._all_commands)}')
            has_items = bool(self._filtered_matches)
            self._list.setVisible(has_items)
            self._detail_panel.setVisible(has_items)
            self._empty_label.setVisible(not has_items)
            if has_items:
                self._list.setCurrentRow(self._first_enabled_row())
            else:
                self._detail_panel.setVisible(False)
                if self.query():
                    self._empty_label.setText('No commands match the current query. Try fewer filters or a different keyword.')
                elif self._all_commands:
                    self._empty_label.setText('Every command is hidden by visibility rules.')
                else:
                    self._empty_label.setText('No commands available. The shell must call set_command_specs(...).')
            self._hint_label.setText(
                f'Enter runs the current command. Up/Down moves selection. {enabled_count} enabled.'
            )
        finally:
            self._selection_signal_muted = False

        current = self._current_spec()
        self._sync_row_selection()
        self._refresh_detail_panel(current)
        if current is not None:
            self.commandHighlighted.emit(current.name, dict(current.payload))
        self._refresh_status_banner()

    def _select_command_by_name(self, name: str) -> None:
        item = self._items_by_name.get(str(name))
        if item is None:
            return
        self._list.setCurrentItem(item)
        self._list.scrollToItem(item, QAbstractItemView.PositionAtCenter)

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.UserRole)
        if isinstance(name, str):
            self._activate_command_by_name(name)

    def _on_current_item_changed(
        self,
        current: QListWidgetItem | None,
        previous: QListWidgetItem | None,
    ) -> None:
        del previous
        if self._selection_signal_muted:
            return
        self._sync_row_selection()
        spec = self._current_spec()
        self._refresh_detail_panel(spec)
        self._refresh_status_banner()
        if spec is not None:
            self.commandHighlighted.emit(spec.name, dict(spec.payload))

    def _sync_row_selection(self) -> None:
        current_name = ''
        current_item = self._list.currentItem()
        if current_item is not None:
            current_name = str(current_item.data(Qt.UserRole) or '')
        for name, widget in self._row_widgets.items():
            widget.set_selected(name == current_name)

    def _refresh_detail_panel(self, spec: _CommandSpec | None) -> None:
        if spec is None:
            self._detail_title.setText('No command selected')
            self._detail_badge.setText('IDLE')
            self._detail_badge.setProperty('tone', 'idle')
            self._detail_meta.setText('Load command specs to begin.')
            self._detail_payload.setText('')
            self._repolish(self._detail_badge)
            return
        self._detail_title.setText(spec.title or spec.name)
        if spec.enabled:
            self._detail_badge.setText('READY')
            self._detail_badge.setProperty('tone', 'ready')
        else:
            self._detail_badge.setText('LOCKED')
            self._detail_badge.setProperty('tone', 'disabled')
        meta_parts = [f'Command id: {spec.name}']
        if spec.shortcut:
            meta_parts.append(f'Shortcut: {spec.shortcut}')
        if spec.keywords:
            meta_parts.append('Keywords: ' + ', '.join(spec.keywords))
        if spec.description:
            meta_parts.append(spec.description)
        self._detail_meta.setText(' | '.join(meta_parts))
        if spec.payload:
            payload_lines = []
            key_color = self._theme_bridge.token('text_soft')
            value_color = self._theme_bridge.token('text')
            for key, value in list(spec.payload.items())[:6]:
                payload_lines.append(
                    f'<span style="color:{key_color};">{html.escape(str(key))}</span>'
                    f' = <span style="color:{value_color};">{html.escape(self._compact_value(value))}</span>'
                )
            self._detail_payload.setText('<br/>'.join(payload_lines))
        else:
            self._detail_payload.setText(
                f'<span style="color:{self._theme_bridge.token("text_soft")};">No payload.</span>'
            )
        self._repolish(self._detail_badge)

    def _activate_current_command(self) -> None:
        spec = self._current_spec()
        if spec is not None:
            self._activate_command(spec)

    def _activate_command_by_name(self, name: str) -> None:
        for match in self._filtered_matches:
            if match.spec.name == str(name):
                self._activate_command(match.spec)
                return
        for spec in self._all_commands:
            if spec.name == str(name):
                self._activate_command(spec)
                return

    def _activate_command(self, spec: _CommandSpec) -> None:
        if not spec.enabled:
            payload = self._failure_payload(
                name=spec.name,
                command_payload=spec.payload,
                reason='disabled',
                error='',
            )
            self.executionFailed.emit(spec.name, payload)
            self._flash_status('danger', f'{spec.title or spec.name} is disabled.')
            return

        self.commandActivated.emit(spec.name, dict(spec.payload))
        self._flash_status('ready', f'Activated {spec.title or spec.name}.', timeout_ms=1000)
        if self._dispatcher is None:
            self._flash_status('idle', 'Preview mode only. No dispatcher is connected.', timeout_ms=1800)
            return

        if hasattr(self._dispatcher, 'has'):
            try:
                has_command = bool(self._dispatcher.has(spec.name))
            except Exception as exc:  # pragma: no cover
                payload = self._failure_payload(
                    name=spec.name,
                    command_payload=spec.payload,
                    reason='dispatcher_has_failed',
                    error=str(exc),
                )
                self.executionFailed.emit(spec.name, payload)
                self._flash_status('danger', f'Preflight failed for {spec.name}.')
                return
            if not has_command:
                payload = self._failure_payload(
                    name=spec.name,
                    command_payload=spec.payload,
                    reason='unavailable',
                    error='',
                )
                self.executionFailed.emit(spec.name, payload)
                self._flash_status('danger', f'{spec.title or spec.name} is unavailable.')
                return

        execute = getattr(self._dispatcher, 'execute', None)
        if not callable(execute):
            payload = self._failure_payload(
                name=spec.name,
                command_payload=spec.payload,
                reason='dispatcher_missing_execute',
                error='',
            )
            self.executionFailed.emit(spec.name, payload)
            self._flash_status('danger', 'Dispatcher has no execute(name, **payload) route.')
            return

        try:
            execute(spec.name, **dict(spec.payload))
        except Exception as exc:  # pragma: no cover
            payload = self._failure_payload(
                name=spec.name,
                command_payload=spec.payload,
                reason='execute_failed',
                error=str(exc),
            )
            self.executionFailed.emit(spec.name, payload)
            self._flash_status('danger', f'Execution failed for {spec.title or spec.name}.')
            return
        self._flash_status('ready', f'Executed {spec.title or spec.name}.', timeout_ms=1400)

    def _step_selection(self, step: int) -> None:
        if not self._filtered_matches:
            return
        enabled_rows = [index for index, match in enumerate(self._filtered_matches) if match.spec.enabled]
        if not enabled_rows:
            self._list.setCurrentRow(0)
            return
        row = self._list.currentRow()
        if row not in enabled_rows:
            target = enabled_rows[0] if step >= 0 else enabled_rows[-1]
            self._list.setCurrentRow(target)
            return
        position = enabled_rows.index(row) + step
        position = max(0, min(position, len(enabled_rows) - 1))
        self._list.setCurrentRow(enabled_rows[position])
        item = self._list.currentItem()
        if item is not None:
            self._list.scrollToItem(item, QAbstractItemView.PositionAtCenter)

    def _jump_to_edge(self, *, first: bool) -> None:
        if not self._filtered_matches:
            return
        enabled_rows = [index for index, match in enumerate(self._filtered_matches) if match.spec.enabled]
        if enabled_rows:
            self._list.setCurrentRow(enabled_rows[0] if first else enabled_rows[-1])
        else:
            self._list.setCurrentRow(0 if first else max(0, len(self._filtered_matches) - 1))

    def _current_spec(self) -> _CommandSpec | None:
        item = self._list.currentItem()
        if item is None:
            return None
        name = item.data(Qt.UserRole)
        if not isinstance(name, str):
            return None
        for match in self._filtered_matches:
            if match.spec.name == name:
                return match.spec
        for spec in self._all_commands:
            if spec.name == name:
                return spec
        return None

    def _match_command(self, spec: _CommandSpec, terms: tuple[str, ...], index: int) -> _CommandMatch | None:
        if not terms:
            base_score = 20 if spec.enabled else 5
            if spec.shortcut:
                base_score += 2
            if spec.description:
                base_score += 1
            return _CommandMatch(spec=spec, index=index, score=base_score)

        title_l = spec.title.lower()
        name_l = spec.name.lower()
        desc_l = spec.description.lower()
        shortcut_l = spec.shortcut.lower()
        keywords_l = [keyword.lower() for keyword in spec.keywords]
        total = 0
        for term in terms:
            matched = False
            if term == name_l or name_l.startswith(term):
                total += 72
                matched = True
            elif term in name_l:
                total += 42
                matched = True
            if term == title_l or title_l.startswith(term):
                total += 80
                matched = True
            elif term in title_l:
                total += 45
                matched = True
            keyword_exact = any(term == keyword for keyword in keywords_l)
            keyword_partial = any(term in keyword for keyword in keywords_l)
            if keyword_exact:
                total += 36
                matched = True
            elif keyword_partial:
                total += 24
                matched = True
            if term and shortcut_l and term in shortcut_l:
                total += 20
                matched = True
            if term and desc_l and term in desc_l:
                total += 12
                matched = True
            if not matched:
                return None
        if spec.enabled:
            total += 12
        return _CommandMatch(spec=spec, index=index, score=total)

    def _normalize_command(self, raw: object) -> _CommandSpec | None:
        name = self._string_value(raw, 'name').strip()
        if not name:
            return None
        title = self._string_value(raw, 'title').strip() or name
        description = self._string_value(raw, 'description').strip()
        shortcut = self._string_value(raw, 'shortcut').strip()
        keywords = self._keywords_value(raw, 'keywords')
        payload = self._mapping_value(raw, 'payload')
        enabled = self._bool_value(raw, 'enabled', default=True)
        visible = self._bool_value(raw, 'visible', default=True)
        return _CommandSpec(
            name=name,
            title=title,
            description=description,
            shortcut=shortcut,
            keywords=keywords,
            payload=payload,
            enabled=enabled,
            visible=visible,
        )

    def _query_terms(self, text: str) -> tuple[str, ...]:
        cleaned = re.split(r'\s+', str(text or '').strip().lower())
        return tuple(part for part in cleaned if part)

    def _tooltip_text(self, spec: _CommandSpec) -> str:
        parts = [spec.title or spec.name]
        if spec.description:
            parts.append(spec.description)
        if spec.keywords:
            parts.append('Keywords: ' + ', '.join(spec.keywords))
        if spec.shortcut:
            parts.append('Shortcut: ' + spec.shortcut)
        return '\n'.join(parts)

    def _first_enabled_row(self) -> int:
        for index, match in enumerate(self._filtered_matches):
            if match.spec.enabled:
                return index
        return 0

    def _string_value(self, raw: object, key: str) -> str:
        value = self._field_value(raw, key)
        return '' if value is _MISSING or value is None else str(value)

    def _keywords_value(self, raw: object, key: str) -> tuple[str, ...]:
        value = self._field_value(raw, key)
        if value is _MISSING or value is None:
            return ()
        if isinstance(value, str):
            parts = [part.strip() for part in re.split(r'[\s,]+', value) if part.strip()]
            return tuple(parts)
        if isinstance(value, Sequence):
            parts = [str(item).strip() for item in value if str(item).strip()]
            return tuple(parts)
        return ()

    def _mapping_value(self, raw: object, key: str) -> dict[str, Any]:
        value = self._field_value(raw, key)
        if value is _MISSING:
            return {}
        return self._coerce_mapping(value)

    def _bool_value(self, raw: object, key: str, *, default: bool) -> bool:
        canonical = self._primary_field_value(raw, key)
        aliases = self._ALIASES.get(key, ())
        if key == 'enabled':
            if canonical is not _MISSING:
                return default if canonical is None else bool(canonical)
            if 'is_enabled' in aliases:
                alias_value = self._value_from_alias(raw, 'is_enabled')
                if alias_value is not _MISSING:
                    return default if alias_value is None else bool(alias_value)
            if 'disabled' in aliases:
                alias_value = self._value_from_alias(raw, 'disabled')
                if alias_value is not _MISSING:
                    return not bool(alias_value)
            return default
        if key == 'visible':
            if canonical is not _MISSING:
                return default if canonical is None else bool(canonical)
            if 'is_visible' in aliases:
                alias_value = self._value_from_alias(raw, 'is_visible')
                if alias_value is not _MISSING:
                    return default if alias_value is None else bool(alias_value)
            if 'hidden' in aliases:
                alias_value = self._value_from_alias(raw, 'hidden')
                if alias_value is not _MISSING:
                    return not bool(alias_value)
            return default
        value = self._field_value(raw, key)
        if value is _MISSING or value is None:
            return default
        return bool(value)

    def _field_value(self, raw: object, key: str) -> Any:
        primary = self._primary_field_value(raw, key)
        if primary is not _MISSING:
            return primary
        for alias in self._ALIASES.get(key, ()):
            value = self._value_from_alias(raw, alias)
            if value is not _MISSING:
                return value
        return _MISSING

    def _primary_field_value(self, raw: object, key: str) -> Any:
        if isinstance(raw, Mapping):
            if key in raw:
                return raw[key]
            return _MISSING
        if hasattr(raw, key):
            return getattr(raw, key)
        return _MISSING

    def _value_from_alias(self, raw: object, alias: str) -> Any:
        if isinstance(raw, Mapping):
            if alias in raw:
                return raw[alias]
            return _MISSING
        if hasattr(raw, alias):
            return getattr(raw, alias)
        return _MISSING

    def _coerce_mapping(self, value: Any) -> dict[str, Any]:
        if isinstance(value, Mapping):
            return {str(key): item for key, item in value.items()}
        return {}

    def _failure_payload(
        self,
        *,
        name: str,
        command_payload: Mapping[str, Any],
        reason: str,
        error: str,
    ) -> dict[str, Any]:
        return {
            'name': name,
            'context': dict(self._context),
            'command_payload': dict(command_payload),
            'reason': reason,
            'error': error,
        }

    def _compact_value(self, value: Any) -> str:
        text = repr(value)
        if len(text) > 72:
            return text[:69] + '...'
        return text

    def _flash_status(self, tone: str, text: str, *, timeout_ms: int = 1800) -> None:
        self._status_override = (tone, text)
        self._refresh_status_banner()
        self._status_reset_serial += 1
        serial = self._status_reset_serial
        if timeout_ms > 0:
            QTimer.singleShot(timeout_ms, lambda: self._clear_status_override(serial))

    def _clear_status_override(self, serial: int) -> None:
        if serial != self._status_reset_serial:
            return
        self._status_override = None
        self._refresh_status_banner()

    def _refresh_status_banner(self) -> None:
        if self._status_override is not None:
            tone, text = self._status_override
        elif not self._all_commands:
            tone, text = 'idle', 'Awaiting commands from set_command_specs(...)'
        elif not self._filtered_matches:
            if self.query():
                tone, text = 'empty', 'No results for the current query'
            else:
                tone, text = 'empty', 'No visible commands to show'
        elif self._dispatcher is None:
            tone, text = 'idle', 'Preview mode only. Activation signals still emit.'
        else:
            current = self._current_spec()
            if current is not None and not current.enabled:
                tone, text = 'warning', 'Highlighted command is disabled.'
            else:
                tone, text = 'ready', 'Ready to execute the highlighted command.'
        self._status_label.setText(text)
        self._status_label.setProperty('tone', tone)
        self._repolish(self._status_label)

    def _repolish(self, widget: QWidget) -> None:
        style = widget.style()
        if style is not None:
            style.unpolish(widget)
            style.polish(widget)
        widget.update()

    def _build_stylesheet(self) -> str:
        bridge = self._theme_bridge
        panel = bridge.role_palette('panel')
        toolbar = bridge.role_palette('toolbar')
        ready = bridge.status_palette('success')
        warning = bridge.status_palette('warning')
        danger = bridge.status_palette('danger')
        muted = bridge.status_palette('muted')
        accent = bridge.status_palette('accent')
        return f"""
        QFrame#cloudflare_guardianCommandBarShell {{
            background:qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {toolbar['surface']}, stop:0.55 {panel['surface']}, stop:1 {panel['surface_alt']});
            border:1px solid {panel['border']};
            border-radius:18px;
        }}
        QLabel#cloudflare_guardianCommandBarHeader {{
            color:{panel['text']};
            font-size:16px;
            font-weight:700;
            letter-spacing:0.3px;
        }}
        QLabel#cloudflare_guardianCommandBarCount,
        QLabel#cloudflare_guardianCommandBarStatus,
        QLabel#cloudflare_guardianCommandBarDetailBadge,
        QLabel#cloudflare_guardianCommandRowState,
        QLabel#cloudflare_guardianCommandRowShortcut {{
            padding:4px 10px;
            border-radius:10px;
            border:1px solid {panel['border']};
            background:{panel['surface_alt']};
            color:{panel['text']};
            font-size:11px;
            font-weight:600;
        }}
        QLabel#cloudflare_guardianCommandBarCount {{
            background:{accent['soft']};
            color:{accent['ink']};
            min-width:56px;
        }}
        QLabel#cloudflare_guardianCommandBarStatus[tone="idle"],
        QLabel#cloudflare_guardianCommandBarDetailBadge[tone="idle"] {{
            background:{muted['soft']};
            color:{muted['ink']};
            border-color:{muted['line']};
        }}
        QLabel#cloudflare_guardianCommandBarStatus[tone="ready"],
        QLabel#cloudflare_guardianCommandBarDetailBadge[tone="ready"],
        QLabel#cloudflare_guardianCommandRowState[tone="ready"] {{
            background:{ready['soft']};
            color:{ready['ink']};
            border-color:{ready['line']};
        }}
        QLabel#cloudflare_guardianCommandBarStatus[tone="warning"] {{
            background:{warning['soft']};
            color:{warning['ink']};
            border-color:{warning['line']};
        }}
        QLabel#cloudflare_guardianCommandBarStatus[tone="danger"],
        QLabel#cloudflare_guardianCommandRowState[tone="disabled"],
        QLabel#cloudflare_guardianCommandBarDetailBadge[tone="disabled"] {{
            background:{danger['soft']};
            color:{danger['ink']};
            border-color:{danger['line']};
        }}
        QLabel#cloudflare_guardianCommandBarStatus[tone="empty"] {{
            background:{muted['soft']};
            color:{panel['muted']};
            border-color:{panel['divider']};
        }}
        QLineEdit#cloudflare_guardianCommandBarInput {{
            background:{toolbar['surface']};
            color:{panel['text']};
            border:1px solid {panel['border']};
            border-radius:12px;
            padding:12px 14px;
            selection-background-color:{panel['surface_active']};
            selection-color:{panel['text']};
            font-size:13px;
        }}
        QLineEdit#cloudflare_guardianCommandBarInput:focus {{
            border:1px solid {panel['focus_ring']};
            background:{panel['surface']};
        }}
        QLabel#cloudflare_guardianCommandBarHint {{
            color:{panel['soft_text']};
            font-size:11px;
            padding-left:2px;
        }}
        QListWidget#cloudflare_guardianCommandBarList {{
            background:transparent;
            border:none;
            outline:none;
        }}
        QListWidget#cloudflare_guardianCommandBarList::item {{
            margin:0px;
            padding:0px;
            border:none;
        }}
        QFrame#cloudflare_guardianCommandRow {{
            background:{panel['surface']};
            border:1px solid {panel['border']};
            border-radius:14px;
        }}
        QFrame#cloudflare_guardianCommandRow[hovered="true"] {{
            background:{panel['surface_hover']};
            border-color:{panel['divider']};
        }}
        QFrame#cloudflare_guardianCommandRow[selected="true"] {{
            background:qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {panel['surface_active']}, stop:1 {panel['surface_hover']});
            border-color:{accent['line']};
        }}
        QFrame#cloudflare_guardianCommandRow[enabledState="false"] {{
            background:{toolbar['surface']};
            border-color:{panel['border']};
        }}
        QLabel#cloudflare_guardianCommandRowTitle {{
            color:{panel['text']};
            font-size:14px;
        }}
        QLabel#cloudflare_guardianCommandRowDescription {{
            color:{panel['muted']};
            font-size:12px;
        }}
        QLabel#cloudflare_guardianCommandRowKeywords {{
            color:{panel['soft_text']};
            font-size:11px;
        }}
        QLabel#cloudflare_guardianCommandBarEmpty {{
            color:{panel['soft_text']};
            border:1px dashed {panel['border']};
            border-radius:14px;
            background:{toolbar['surface']};
            padding:22px;
            font-size:13px;
        }}
        QFrame#cloudflare_guardianCommandBarDetail {{
            background:{toolbar['surface']};
            border:1px solid {panel['border']};
            border-radius:14px;
        }}
        QLabel#cloudflare_guardianCommandBarDetailTitle {{
            color:{panel['text']};
            font-size:14px;
            font-weight:700;
        }}
        QLabel#cloudflare_guardianCommandBarDetailMeta {{
            color:{panel['muted']};
            font-size:12px;
        }}
        QLabel#cloudflare_guardianCommandBarDetailPayload {{
            color:{panel['text']};
            background:{bridge.token('code_bg')};
            border:1px solid {bridge.token('code_line')};
            border-radius:10px;
            padding:10px;
            font-family:monospace;
            font-size:11px;
        }}
        """


__all__ = ['CloudflareGuardianCommandBar']


