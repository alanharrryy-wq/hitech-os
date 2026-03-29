from __future__ import annotations

import html
import re
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

from PySide6.QtCore import QEvent, QObject, QTimer, Qt, Signal
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .theme_bridge import DeckThemeBridge

_MISSING = object()


@dataclass(frozen=True, slots=True)
class _ActionSpec:
    action_id: str
    title: str
    description: str
    keywords: tuple[str, ...]
    payload: dict[str, Any]
    enabled: bool
    visible: bool


class _ActionTile(QFrame):
    def __init__(
        self,
        *,
        select_callback: Callable[[], None],
        trigger_callback: Callable[[], None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._select_callback = select_callback
        self._trigger_callback = trigger_callback
        self._action_id = ''
        self._theme_bridge = DeckThemeBridge.coerce(None)

        self.setObjectName('cloudflare_guardianActionRailTile')
        self.setProperty('selected', False)
        self.setProperty('tone', 'ready')

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
        root.addLayout(top)

        self._title_label = QLabel(self)
        self._title_label.setObjectName('cloudflare_guardianActionRailTileTitle')
        self._title_label.setWordWrap(True)
        top.addWidget(self._title_label, 1)

        self._badge_label = QLabel('READY', self)
        self._badge_label.setObjectName('cloudflare_guardianActionRailTileBadge')
        self._badge_label.setAlignment(Qt.AlignCenter)
        self._badge_label.setProperty('tone', 'ready')
        top.addWidget(self._badge_label, 0)

        self._description_label = QLabel(self)
        self._description_label.setObjectName('cloudflare_guardianActionRailTileDescription')
        self._description_label.setWordWrap(True)
        root.addWidget(self._description_label)

        self._keywords_label = QLabel(self)
        self._keywords_label.setObjectName('cloudflare_guardianActionRailTileKeywords')
        self._keywords_label.setTextFormat(Qt.RichText)
        self._keywords_label.setWordWrap(True)
        root.addWidget(self._keywords_label)

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(8)
        root.addLayout(footer)

        self._payload_label = QLabel(self)
        self._payload_label.setObjectName('cloudflare_guardianActionRailTilePayload')
        self._payload_label.setWordWrap(True)
        footer.addWidget(self._payload_label, 1)

        self._trigger_button = QPushButton('Run', self)
        self._trigger_button.setObjectName('cloudflare_guardianActionRailTileButton')
        self._trigger_button.setCursor(Qt.PointingHandCursor)
        self._trigger_button.clicked.connect(self._on_trigger_clicked)
        self._trigger_button.installEventFilter(self)
        footer.addWidget(self._trigger_button, 0)

    def set_theme_tokens(self, tokens: object | None) -> None:
        self._theme_bridge = DeckThemeBridge.coerce(tokens)

    def bind(self, spec: _ActionSpec, *, busy: bool, selected: bool) -> None:
        self._action_id = spec.action_id
        self._title_label.setText(spec.title or spec.action_id)
        self._description_label.setText(spec.description or 'No description provided.')
        self._keywords_label.setText(self._keywords_html(spec.keywords))
        self._keywords_label.setVisible(bool(spec.keywords))
        self._payload_label.setText(self._payload_summary(spec.payload))
        self.set_selected(selected)
        if busy:
            self._badge_label.setText('BUSY')
            self._badge_label.setProperty('tone', 'busy')
            self.setProperty('tone', 'busy')
        elif spec.enabled:
            self._badge_label.setText('READY')
            self._badge_label.setProperty('tone', 'ready')
            self.setProperty('tone', 'ready')
        else:
            self._badge_label.setText('LOCKED')
            self._badge_label.setProperty('tone', 'disabled')
            self.setProperty('tone', 'disabled')
        self._trigger_button.setEnabled(spec.enabled and not busy)
        self._repolish(self._badge_label)
        self._repolish(self)

    def set_selected(self, selected: bool) -> None:
        self.setProperty('selected', bool(selected))
        self._repolish(self)

    def set_recent_result(self, result: str) -> None:
        if result == 'success':
            self._badge_label.setText('DONE')
            self._badge_label.setProperty('tone', 'success')
        elif result == 'failure':
            self._badge_label.setText('FAILED')
            self._badge_label.setProperty('tone', 'danger')
        self._repolish(self._badge_label)

    def focus_button(self) -> None:
        self._trigger_button.setFocus(Qt.TabFocusReason)

    def action_id(self) -> str:
        return self._action_id

    def trigger_button(self) -> QPushButton:
        return self._trigger_button

    def enterEvent(self, event: QEvent) -> None:  # noqa: N802
        self._select_callback()
        super().enterEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._select_callback()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self._select_callback()
            self._trigger_callback()
        super().mouseDoubleClickEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if watched is self._trigger_button and event.type() == QEvent.FocusIn:
            self._select_callback()
        return super().eventFilter(watched, event)

    def _on_trigger_clicked(self) -> None:
        self._select_callback()
        self._trigger_callback()

    def _keywords_html(self, keywords: Sequence[str]) -> str:
        if not keywords:
            return ''
        chips = []
        chip_bg = self._theme_bridge.css_color('accent_soft', alpha=214)
        chip_text = self._theme_bridge.token('accent')
        chip_border = self._theme_bridge.accent_mix('border_strong', 0.55)
        for keyword in keywords[:6]:
            chips.append(
                f'<span style="background:{chip_bg}; color:{chip_text}; border:1px solid {chip_border}; '
                'padding:2px 8px; border-radius:10px;">'
                f'{html.escape(keyword)}</span>'
            )
        return ' '.join(chips)

    def _payload_summary(self, payload: Mapping[str, Any]) -> str:
        if not payload:
            return 'No payload'
        pairs = []
        for key, value in list(payload.items())[:3]:
            pairs.append(f'{key}={self._compact(value)}')
        return ' | '.join(pairs)

    def _compact(self, value: Any) -> str:
        text = repr(value)
        if len(text) > 36:
            return text[:33] + '...'
        return text

    def _repolish(self, widget: QWidget) -> None:
        style = widget.style()
        if style is not None:
            style.unpolish(widget)
            style.polish(widget)
        widget.update()


class CloudflareGuardianActionRail(QWidget):
    actionTriggered = Signal(str, object)
    actionFailed = Signal(str, object)

    _ALIASES: dict[str, tuple[str, ...]] = {
        'action_id': ('id', 'name', 'contribution_id'),
        'title': ('label', 'text'),
        'description': ('tooltip', 'summary', 'help'),
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
        self._all_actions: list[_ActionSpec] = []
        self._visible_actions: list[_ActionSpec] = []
        self._tiles: dict[str, _ActionTile] = {}
        self._busy = False
        self._current_action_id = ''
        self._status_override: tuple[str, str] | None = None
        self._status_reset_serial = 0
        self._tile_reset_serial = 0

        self.setObjectName('cloudflare_guardianActionRail')
        self.setProperty('visualRole', 'action-surface')
        self.setProperty('visualTier', 'themed')
        self.setStyleSheet(self._build_stylesheet())

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(10)

        shell = QFrame(self)
        shell.setObjectName('cloudflare_guardianActionRailShell')
        shell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        shell.setMinimumHeight(250)
        root.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(14, 14, 14, 14)
        shell_layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        shell_layout.addLayout(header)

        self._header_label = QLabel('Action Rail', shell)
        self._header_label.setObjectName('cloudflare_guardianActionRailHeader')
        header.addWidget(self._header_label, 1)

        self._count_label = QLabel('0', shell)
        self._count_label.setObjectName('cloudflare_guardianActionRailCount')
        self._count_label.setAlignment(Qt.AlignCenter)
        header.addWidget(self._count_label, 0)

        self._status_label = QLabel('Awaiting actions', shell)
        self._status_label.setObjectName('cloudflare_guardianActionRailStatus')
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setProperty('tone', 'idle')
        header.addWidget(self._status_label, 0)

        self._hint_label = QLabel('Arrow keys move between action buttons. Enter or Space triggers.', shell)
        self._hint_label.setObjectName('cloudflare_guardianActionRailHint')
        self._hint_label.setWordWrap(True)
        shell_layout.addWidget(self._hint_label)

        self._scroll = QScrollArea(shell)
        self._scroll.setObjectName('cloudflare_guardianActionRailScroll')
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._scroll.setMinimumHeight(170)
        shell_layout.addWidget(self._scroll, 1)

        self._content = QWidget(self._scroll)
        self._content.setObjectName('cloudflare_guardianActionRailContent')
        self._content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._scroll.setWidget(self._content)

        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(8)

        self._empty_label = QLabel('No actions available.', self._content)
        self._empty_label.setObjectName('cloudflare_guardianActionRailEmpty')
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.setWordWrap(True)
        self._content_layout.addWidget(self._empty_label)
        self._content_layout.addStretch(1)

        self._detail_panel = QFrame(shell)
        self._detail_panel.setObjectName('cloudflare_guardianActionRailDetail')
        self._detail_panel.setMinimumHeight(104)
        detail_layout = QVBoxLayout(self._detail_panel)
        detail_layout.setContentsMargins(12, 12, 12, 12)
        detail_layout.setSpacing(6)
        shell_layout.addWidget(self._detail_panel)

        detail_header = QHBoxLayout()
        detail_header.setContentsMargins(0, 0, 0, 0)
        detail_header.setSpacing(8)
        detail_layout.addLayout(detail_header)

        self._detail_title = QLabel('No action selected', self._detail_panel)
        self._detail_title.setObjectName('cloudflare_guardianActionRailDetailTitle')
        detail_header.addWidget(self._detail_title, 1)

        self._detail_badge = QLabel('IDLE', self._detail_panel)
        self._detail_badge.setObjectName('cloudflare_guardianActionRailDetailBadge')
        self._detail_badge.setAlignment(Qt.AlignCenter)
        self._detail_badge.setProperty('tone', 'idle')
        detail_header.addWidget(self._detail_badge, 0)

        self._detail_meta = QLabel('Load actions with set_actions(...) to begin.', self._detail_panel)
        self._detail_meta.setObjectName('cloudflare_guardianActionRailDetailMeta')
        self._detail_meta.setWordWrap(True)
        detail_layout.addWidget(self._detail_meta)

        self._detail_payload = QLabel('', self._detail_panel)
        self._detail_payload.setObjectName('cloudflare_guardianActionRailDetailPayload')
        self._detail_payload.setWordWrap(True)
        self._detail_payload.setTextFormat(Qt.RichText)
        detail_layout.addWidget(self._detail_payload)

        self.refresh_actions()

    def set_dispatcher(self, dispatcher: Any) -> None:
        self._dispatcher = dispatcher
        self._refresh_status_banner()

    def set_skin(self, tokens: object | None) -> None:
        self.set_theme_tokens(tokens)

    def set_theme_tokens(self, tokens: object | None) -> None:
        self._theme_bridge = DeckThemeBridge.coerce(tokens)
        self.setStyleSheet(self._build_stylesheet())
        self.refresh_actions()

    def set_actions(self, actions: Iterable[object] | None) -> None:
        normalized: list[_ActionSpec] = []
        seen_ids: set[str] = set()
        for raw in actions or []:
            spec = self._normalize_action(raw)
            if spec is None:
                continue
            if spec.action_id in seen_ids:
                continue
            seen_ids.add(spec.action_id)
            normalized.append(spec)
        self._all_actions = normalized
        self.refresh_actions()

    def refresh_actions(self) -> None:
        self._visible_actions = [spec for spec in self._all_actions if spec.visible]
        if self._current_action_id and all(spec.action_id != self._current_action_id for spec in self._visible_actions):
            self._current_action_id = ''
        if not self._current_action_id:
            self._current_action_id = self._first_enabled_action_id()
        self._rebuild_tiles()

    def update_context(self, context: Mapping[str, Any] | None) -> None:
        self._context = self._coerce_mapping(context)
        self._refresh_detail_panel(self._current_spec())

    def set_busy(self, busy: bool) -> None:
        self._busy = bool(busy)
        self._sync_tiles()
        self._refresh_status_banner()

    def trigger_action(self, action_id: str) -> None:
        spec = self._find_action(action_id)
        if spec is None:
            payload = self._failure_payload(
                action_id=str(action_id),
                action_payload={},
                reason='action_not_found',
                error='',
            )
            self.actionFailed.emit(str(action_id), payload)
            self._flash_status('danger', f'Action {action_id} was not found.')
            return
        self._current_action_id = spec.action_id
        self._sync_tiles()
        self._refresh_detail_panel(spec)

        if self._busy:
            payload = self._failure_payload(
                action_id=spec.action_id,
                action_payload=spec.payload,
                reason='busy',
                error='',
            )
            self.actionFailed.emit(spec.action_id, payload)
            self._mark_recent(spec.action_id, success=False)
            self._flash_status('warning', f'{spec.title or spec.action_id} is blocked while busy.')
            return
        if not spec.enabled:
            payload = self._failure_payload(
                action_id=spec.action_id,
                action_payload=spec.payload,
                reason='disabled',
                error='',
            )
            self.actionFailed.emit(spec.action_id, payload)
            self._mark_recent(spec.action_id, success=False)
            self._flash_status('danger', f'{spec.title or spec.action_id} is disabled.')
            return

        self.actionTriggered.emit(spec.action_id, dict(spec.payload))
        self._mark_recent(spec.action_id, success=True)
        self._flash_status('ready', f'Triggered {spec.title or spec.action_id}.', timeout_ms=1000)
        if self._dispatcher is None:
            self._flash_status('idle', 'Preview mode only. Action signal emitted without dispatcher.', timeout_ms=1800)
            return

        if hasattr(self._dispatcher, 'has'):
            try:
                has_action = bool(self._dispatcher.has(spec.action_id))
            except Exception as exc:  # pragma: no cover
                payload = self._failure_payload(
                    action_id=spec.action_id,
                    action_payload=spec.payload,
                    reason='dispatcher_has_failed',
                    error=str(exc),
                )
                self.actionFailed.emit(spec.action_id, payload)
                self._mark_recent(spec.action_id, success=False)
                self._flash_status('danger', f'Preflight failed for {spec.action_id}.')
                return
            if not has_action:
                payload = self._failure_payload(
                    action_id=spec.action_id,
                    action_payload=spec.payload,
                    reason='unavailable',
                    error='',
                )
                self.actionFailed.emit(spec.action_id, payload)
                self._mark_recent(spec.action_id, success=False)
                self._flash_status('danger', f'{spec.title or spec.action_id} is unavailable.')
                return

        execute = getattr(self._dispatcher, 'execute', None)
        if not callable(execute):
            payload = self._failure_payload(
                action_id=spec.action_id,
                action_payload=spec.payload,
                reason='dispatcher_missing_execute',
                error='',
            )
            self.actionFailed.emit(spec.action_id, payload)
            self._mark_recent(spec.action_id, success=False)
            self._flash_status('danger', 'Dispatcher has no execute(name, **payload) route.')
            return

        try:
            execute(spec.action_id, **dict(spec.payload))
        except Exception as exc:  # pragma: no cover
            payload = self._failure_payload(
                action_id=spec.action_id,
                action_payload=spec.payload,
                reason='execute_failed',
                error=str(exc),
            )
            self.actionFailed.emit(spec.action_id, payload)
            self._mark_recent(spec.action_id, success=False)
            self._flash_status('danger', f'Execution failed for {spec.title or spec.action_id}.')
            return
        self._flash_status('ready', f'Executed {spec.title or spec.action_id}.', timeout_ms=1400)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # noqa: N802
        if event.type() == QEvent.KeyPress and isinstance(event, QKeyEvent):
            owner_action_id = ''
            for action_id, tile in self._tiles.items():
                if watched is tile.trigger_button():
                    owner_action_id = action_id
                    break
            if owner_action_id:
                key = event.key()
                if key in (Qt.Key_Down, Qt.Key_Right):
                    self._move_focus(owner_action_id, step=1)
                    return True
                if key in (Qt.Key_Up, Qt.Key_Left):
                    self._move_focus(owner_action_id, step=-1)
                    return True
                if key == Qt.Key_Home:
                    self._focus_edge(first=True)
                    return True
                if key == Qt.Key_End:
                    self._focus_edge(first=False)
                    return True
                if key in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
                    self.trigger_action(owner_action_id)
                    return True
        return super().eventFilter(watched, event)

    def _rebuild_tiles(self) -> None:
        while self._content_layout.count() > 0:
            item = self._content_layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                child_layout.deleteLater()

        self._tiles.clear()
        if not self._visible_actions:
            self._empty_label = QLabel('No actions available. The shell must call set_actions(...).', self._content)
            self._empty_label.setObjectName('cloudflare_guardianActionRailEmpty')
            self._empty_label.setAlignment(Qt.AlignCenter)
            self._empty_label.setWordWrap(True)
            self._content_layout.addWidget(self._empty_label)
            self._content_layout.addStretch(1)
            self._detail_panel.setVisible(False)
            self._count_label.setText(f'0 / {len(self._all_actions)}')
            self._refresh_status_banner()
            return

        self._detail_panel.setVisible(True)
        self._count_label.setText(f'{len(self._visible_actions)} / {len(self._all_actions)}')
        for spec in self._visible_actions:
            tile = _ActionTile(
                select_callback=lambda action_id=spec.action_id: self._select_action(action_id),
                trigger_callback=lambda action_id=spec.action_id: self.trigger_action(action_id),
                parent=self._content,
            )
            tile.set_theme_tokens(self._theme_bridge)
            tile.bind(spec, busy=self._busy, selected=(spec.action_id == self._current_action_id))
            tile.trigger_button().installEventFilter(self)
            self._content_layout.addWidget(tile)
            self._tiles[spec.action_id] = tile
        self._content_layout.addStretch(1)
        self._sync_tiles()
        self._refresh_detail_panel(self._current_spec())
        self._refresh_status_banner()

    def _sync_tiles(self) -> None:
        for spec in self._visible_actions:
            tile = self._tiles.get(spec.action_id)
            if tile is None:
                continue
            tile.bind(spec, busy=self._busy, selected=(spec.action_id == self._current_action_id))
        self._refresh_detail_panel(self._current_spec())

    def _select_action(self, action_id: str) -> None:
        normalized = str(action_id or '')
        if not normalized:
            return
        self._current_action_id = normalized
        self._sync_tiles()
        tile = self._tiles.get(normalized)
        if tile is not None:
            self._scroll.ensureWidgetVisible(tile, 0, 40)
        self._refresh_status_banner()

    def _refresh_detail_panel(self, spec: _ActionSpec | None) -> None:
        if spec is None:
            self._detail_title.setText('No action selected')
            self._detail_badge.setText('IDLE')
            self._detail_badge.setProperty('tone', 'idle')
            self._detail_meta.setText('Load actions with set_actions(...) to begin.')
            self._detail_payload.setText('')
            self._repolish(self._detail_badge)
            return
        self._detail_title.setText(spec.title or spec.action_id)
        if self._busy:
            self._detail_badge.setText('BUSY')
            self._detail_badge.setProperty('tone', 'busy')
        elif spec.enabled:
            self._detail_badge.setText('READY')
            self._detail_badge.setProperty('tone', 'ready')
        else:
            self._detail_badge.setText('LOCKED')
            self._detail_badge.setProperty('tone', 'disabled')
        meta_parts = [f'Action id: {spec.action_id}']
        if spec.keywords:
            meta_parts.append('Keywords: ' + ', '.join(spec.keywords))
        if spec.description:
            meta_parts.append(spec.description)
        self._detail_meta.setText(' | '.join(meta_parts))
        if spec.payload:
            lines = []
            key_color = self._theme_bridge.token('text_soft')
            value_color = self._theme_bridge.token('text')
            for key, value in list(spec.payload.items())[:6]:
                lines.append(
                    f'<span style="color:{key_color};">{html.escape(str(key))}</span>'
                    f' = <span style="color:{value_color};">{html.escape(self._compact_value(value))}</span>'
                )
            self._detail_payload.setText('<br/>'.join(lines))
        else:
            self._detail_payload.setText(
                f'<span style="color:{self._theme_bridge.token("text_soft")};">No payload.</span>'
            )
        self._repolish(self._detail_badge)

    def _move_focus(self, action_id: str, *, step: int) -> None:
        enabled_ids = [spec.action_id for spec in self._visible_actions if spec.enabled and not self._busy]
        if not enabled_ids:
            return
        if action_id not in enabled_ids:
            target = enabled_ids[0] if step >= 0 else enabled_ids[-1]
        else:
            position = enabled_ids.index(action_id) + step
            position = max(0, min(position, len(enabled_ids) - 1))
            target = enabled_ids[position]
        self._current_action_id = target
        self._sync_tiles()
        tile = self._tiles.get(target)
        if tile is not None:
            tile.focus_button()
            self._scroll.ensureWidgetVisible(tile, 0, 40)
        self._refresh_status_banner()

    def _focus_edge(self, *, first: bool) -> None:
        enabled_ids = [spec.action_id for spec in self._visible_actions if spec.enabled and not self._busy]
        if not enabled_ids:
            return
        target = enabled_ids[0] if first else enabled_ids[-1]
        self._current_action_id = target
        self._sync_tiles()
        tile = self._tiles.get(target)
        if tile is not None:
            tile.focus_button()
            self._scroll.ensureWidgetVisible(tile, 0, 40)
        self._refresh_status_banner()

    def _mark_recent(self, action_id: str, *, success: bool) -> None:
        tile = self._tiles.get(str(action_id))
        if tile is None:
            return
        tile.set_recent_result('success' if success else 'failure')
        self._tile_reset_serial += 1
        serial = self._tile_reset_serial
        QTimer.singleShot(1200, lambda: self._restore_recent_badge(serial, action_id))

    def _restore_recent_badge(self, serial: int, action_id: str) -> None:
        if serial != self._tile_reset_serial:
            return
        self._sync_tiles()
        if self._current_action_id == str(action_id):
            self._refresh_detail_panel(self._current_spec())

    def _find_action(self, action_id: str) -> _ActionSpec | None:
        normalized = str(action_id or '')
        for spec in self._visible_actions:
            if spec.action_id == normalized:
                return spec
        for spec in self._all_actions:
            if spec.action_id == normalized:
                return spec
        return None

    def _current_spec(self) -> _ActionSpec | None:
        return self._find_action(self._current_action_id)

    def _first_enabled_action_id(self) -> str:
        for spec in self._visible_actions:
            if spec.enabled:
                return spec.action_id
        return self._visible_actions[0].action_id if self._visible_actions else ''

    def _normalize_action(self, raw: object) -> _ActionSpec | None:
        action_id = self._string_value(raw, 'action_id').strip()
        if not action_id:
            return None
        title = self._string_value(raw, 'title').strip() or action_id
        description = self._string_value(raw, 'description').strip()
        keywords = self._keywords_value(raw, 'keywords')
        payload = self._mapping_value(raw, 'payload')
        enabled = self._bool_value(raw, 'enabled', default=True)
        visible = self._bool_value(raw, 'visible', default=True)
        return _ActionSpec(
            action_id=action_id,
            title=title,
            description=description,
            keywords=keywords,
            payload=payload,
            enabled=enabled,
            visible=visible,
        )

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
        action_id: str,
        action_payload: Mapping[str, Any],
        reason: str,
        error: str,
    ) -> dict[str, Any]:
        return {
            'action_id': action_id,
            'context': dict(self._context),
            'action_payload': dict(action_payload),
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
        elif not self._all_actions:
            tone, text = 'idle', 'Awaiting actions from set_actions(...)'
        elif not self._visible_actions:
            tone, text = 'empty', 'No visible actions to show'
        elif self._busy:
            tone, text = 'warning', 'Busy state active. Action buttons are temporarily locked.'
        elif self._dispatcher is None:
            tone, text = 'idle', 'Preview mode only. Trigger signals still emit.'
        else:
            current = self._current_spec()
            if current is not None and not current.enabled:
                tone, text = 'danger', 'Selected action is disabled.'
            else:
                tone, text = 'ready', 'Ready to trigger the selected action.'
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
        QFrame#cloudflare_guardianActionRailShell {{
            background:qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 {toolbar['surface']}, stop:0.55 {panel['surface']}, stop:1 {panel['surface_alt']});
            border:1px solid {panel['border']};
            border-radius:18px;
        }}
        QLabel#cloudflare_guardianActionRailHeader {{
            color:{panel['text']};
            font-size:16px;
            font-weight:700;
            letter-spacing:0.3px;
        }}
        QLabel#cloudflare_guardianActionRailCount,
        QLabel#cloudflare_guardianActionRailStatus,
        QLabel#cloudflare_guardianActionRailDetailBadge,
        QLabel#cloudflare_guardianActionRailTileBadge {{
            padding:4px 10px;
            border-radius:10px;
            border:1px solid {panel['border']};
            background:{panel['surface_alt']};
            color:{panel['text']};
            font-size:11px;
            font-weight:600;
        }}
        QLabel#cloudflare_guardianActionRailCount {{
            background:{accent['soft']};
            color:{accent['ink']};
            min-width:56px;
        }}
        QLabel#cloudflare_guardianActionRailStatus[tone="idle"],
        QLabel#cloudflare_guardianActionRailDetailBadge[tone="idle"] {{
            background:{muted['soft']};
            color:{muted['ink']};
            border-color:{muted['line']};
        }}
        QLabel#cloudflare_guardianActionRailStatus[tone="ready"],
        QLabel#cloudflare_guardianActionRailDetailBadge[tone="ready"],
        QLabel#cloudflare_guardianActionRailTileBadge[tone="ready"] {{
            background:{ready['soft']};
            color:{ready['ink']};
            border-color:{ready['line']};
        }}
        QLabel#cloudflare_guardianActionRailStatus[tone="warning"],
        QLabel#cloudflare_guardianActionRailDetailBadge[tone="busy"],
        QLabel#cloudflare_guardianActionRailTileBadge[tone="busy"] {{
            background:{warning['soft']};
            color:{warning['ink']};
            border-color:{warning['line']};
        }}
        QLabel#cloudflare_guardianActionRailStatus[tone="danger"],
        QLabel#cloudflare_guardianActionRailDetailBadge[tone="disabled"],
        QLabel#cloudflare_guardianActionRailTileBadge[tone="disabled"],
        QLabel#cloudflare_guardianActionRailTileBadge[tone="danger"] {{
            background:{danger['soft']};
            color:{danger['ink']};
            border-color:{danger['line']};
        }}
        QLabel#cloudflare_guardianActionRailStatus[tone="empty"] {{
            background:{muted['soft']};
            color:{panel['muted']};
            border-color:{panel['divider']};
        }}
        QLabel#cloudflare_guardianActionRailTileBadge[tone="success"] {{
            background:{ready['soft']};
            color:{ready['ink']};
            border-color:{ready['line']};
        }}
        QLabel#cloudflare_guardianActionRailHint {{
            color:{panel['soft_text']};
            font-size:11px;
        }}
        QScrollArea#cloudflare_guardianActionRailScroll {{
            background:transparent;
            border:none;
        }}
        QWidget#cloudflare_guardianActionRailContent {{
            background:transparent;
        }}
        QFrame#cloudflare_guardianActionRailTile {{
            background:{panel['surface']};
            border:1px solid {panel['border']};
            border-radius:16px;
        }}
        QFrame#cloudflare_guardianActionRailTile[selected="true"] {{
            background:qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {panel['surface_active']}, stop:1 {panel['surface_hover']});
            border-color:{accent['line']};
        }}
        QFrame#cloudflare_guardianActionRailTile[tone="busy"] {{
            border-color:{warning['line']};
        }}
        QFrame#cloudflare_guardianActionRailTile[tone="disabled"] {{
            background:{toolbar['surface']};
            border-color:{panel['border']};
        }}
        QLabel#cloudflare_guardianActionRailTileTitle {{
            color:{panel['text']};
            font-size:14px;
            font-weight:700;
        }}
        QLabel#cloudflare_guardianActionRailTileDescription {{
            color:{panel['muted']};
            font-size:12px;
        }}
        QLabel#cloudflare_guardianActionRailTileKeywords {{
            color:{panel['soft_text']};
            font-size:11px;
        }}
        QLabel#cloudflare_guardianActionRailTilePayload {{
            color:{panel['soft_text']};
            font-size:11px;
        }}
        QPushButton#cloudflare_guardianActionRailTileButton {{
            background:{panel['surface_active']};
            color:{panel['text']};
            border:1px solid {accent['line']};
            border-radius:11px;
            padding:8px 14px;
            font-weight:700;
        }}
        QPushButton#cloudflare_guardianActionRailTileButton:hover {{
            background:{panel['surface_hover']};
            border-color:{panel['focus_ring']};
        }}
        QPushButton#cloudflare_guardianActionRailTileButton:pressed {{
            background:{toolbar['surface']};
        }}
        QPushButton#cloudflare_guardianActionRailTileButton:focus {{
            border:1px solid {panel['focus_ring']};
        }}
        QPushButton#cloudflare_guardianActionRailTileButton:disabled {{
            background:{toolbar['surface']};
            color:{panel['soft_text']};
            border-color:{panel['border']};
        }}
        QLabel#cloudflare_guardianActionRailEmpty {{
            color:{panel['soft_text']};
            border:1px dashed {panel['border']};
            border-radius:14px;
            background:{toolbar['surface']};
            padding:22px;
            font-size:13px;
        }}
        QFrame#cloudflare_guardianActionRailDetail {{
            background:{toolbar['surface']};
            border:1px solid {panel['border']};
            border-radius:14px;
        }}
        QLabel#cloudflare_guardianActionRailDetailTitle {{
            color:{panel['text']};
            font-size:14px;
            font-weight:700;
        }}
        QLabel#cloudflare_guardianActionRailDetailMeta {{
            color:{panel['muted']};
            font-size:12px;
        }}
        QLabel#cloudflare_guardianActionRailDetailPayload {{
            color:{panel['text']};
            background:{bridge.token('code_bg')};
            border:1px solid {bridge.token('code_line')};
            border-radius:10px;
            padding:10px;
            font-family:monospace;
            font-size:11px;
        }}
        """


__all__ = ['CloudflareGuardianActionRail']


