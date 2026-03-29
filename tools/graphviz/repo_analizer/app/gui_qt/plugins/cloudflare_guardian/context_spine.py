from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .state_adapter import CloudflareGuardianDeckSnapshot, snapshot_payload
from .theme_bridge import DeckThemeBridge


class CloudflareGuardianContextSpine(QFrame):
    """Read-only snapshot consumer that renders rich context blocks."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('cloudflare_guardianContextSpine')
        self._snapshot = CloudflareGuardianDeckSnapshot()
        self._theme_bridge = DeckThemeBridge.coerce(None)

        self._title_label = QLabel('Context spine', self)
        self._title_label.setObjectName('cloudflare_guardianContextSpineTitle')

        self._phase_chip = QLabel('', self)
        self._phase_chip.setObjectName('cloudflare_guardianContextSpinePhaseChip')
        self._phase_chip.setAlignment(Qt.AlignCenter)

        self._subtitle_label = QLabel('', self)
        self._subtitle_label.setObjectName('cloudflare_guardianContextSpineSubtitle')
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self._note_label = QLabel('', self)
        self._note_label.setObjectName('cloudflare_guardianContextSpineNote')
        self._note_label.setWordWrap(True)
        self._note_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)
        header_row.addWidget(self._title_label, 1)
        header_row.addWidget(self._phase_chip, 0)

        self._tiles = {
            'repo': _ContextTile('Repository', self),
            'scope': _ContextTile('Search scope', self),
            'query': _ContextTile('Query', self),
            'preview': _ContextTile('Preview', self),
            'runtime': _ContextTile('Runtime', self),
            'graph': _ContextTile('Graph contract', self),
        }

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        positions = [
            ('repo', 0, 0),
            ('scope', 0, 1),
            ('query', 1, 0),
            ('preview', 1, 1),
            ('runtime', 2, 0),
            ('graph', 2, 1),
        ]
        for key, row, col in positions:
            grid.addWidget(self._tiles[key], row, col)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addLayout(header_row)
        layout.addWidget(self._subtitle_label)
        layout.addLayout(grid)
        layout.addWidget(self._note_label)
        layout.addStretch(1)

        self.setStyleSheet(_build_style_sheet(self._theme_bridge))
        self.refresh_now(self._snapshot)

    def set_skin(self, tokens: object | None) -> None:
        self.set_theme_tokens(tokens)

    def set_theme_tokens(self, tokens: object | None) -> None:
        self._theme_bridge = DeckThemeBridge.coerce(tokens)
        self.setStyleSheet(_build_style_sheet(self._theme_bridge))

    def set_snapshot(self, snapshot: CloudflareGuardianDeckSnapshot | Mapping[str, Any] | object) -> None:
        self._snapshot = _coerce_snapshot(snapshot)
        payload = snapshot_payload(self._snapshot)
        tone = _resolve_tone(payload)
        phase_text = _phase_text(payload)

        self.setProperty('tone', tone)
        self._phase_chip.setProperty('tone', tone)
        self._phase_chip.setText(phase_text)
        self._subtitle_label.setText(payload['subtitle'] or 'No derived subtitle is available yet.')
        self._note_label.setText(_note_text(payload))

        repo_root = payload['repo_root'] or 'No repo path selected yet'
        repo_value = payload['repo_name'] or 'Detached workspace'
        repo_meta_parts = [repo_root]
        if payload['index_file_count']:
            repo_meta_parts.append(f"{payload['index_file_count']} files")
        if payload['index_ext_count']:
            repo_meta_parts.append(f"{payload['index_ext_count']} extensions")
        if payload['index_elapsed_sec']:
            repo_meta_parts.append(f"{payload['index_elapsed_sec']:.2f}s")
        self._tiles['repo'].set_content(
            value=repo_value,
            meta=' • '.join(repo_meta_parts),
            tone=tone if payload['repo_ready'] else 'idle',
        )

        scope_value = payload['active_scope'] or 'Whole repository'
        extension_text = payload['active_extension'] or 'All extensions'
        scope_meta = f"extension filter: {extension_text}"
        if payload['results_count']:
            scope_meta += f" • {payload['results_count']} current results"
        self._tiles['scope'].set_content(
            value=scope_value,
            meta=scope_meta,
            tone='busy' if payload['query_text'] else ('ok' if payload['repo_ready'] else 'idle'),
        )

        query_value = payload['query_text'] or 'No active search query'
        query_meta = 'Search ready'
        if payload['query_text']:
            if payload['results_count']:
                query_meta = f"{payload['results_count']} matches in the current snapshot"
            else:
                query_meta = 'No matches in the current snapshot'
        self._tiles['query'].set_content(
            value=query_value,
            meta=query_meta,
            tone='busy' if payload['query_text'] else 'idle',
        )

        preview_name = Path(payload['current_preview_relpath']).name if payload['current_preview_relpath'] else 'No preview open'
        preview_meta_parts = []
        if payload['current_preview_relpath']:
            preview_meta_parts.append(payload['current_preview_relpath'])
        if payload['current_preview_kind']:
            preview_meta_parts.append(payload['current_preview_kind'])
        if payload['current_preview_path']:
            preview_meta_parts.append(payload['current_preview_path'])
        if payload['nav_can_go_back'] or payload['nav_can_go_forward']:
            preview_meta_parts.append(
                f"history b:{payload['nav_can_go_back']} f:{payload['nav_can_go_forward']}"
            )
        self._tiles['preview'].set_content(
            value=preview_name,
            meta=' • '.join(preview_meta_parts) or 'Select a file from the tree or search results to populate this block.',
            tone='ok' if payload['current_preview_relpath'] else 'idle',
        )

        runtime_value = payload['status_text'] or 'No runtime summary available'
        runtime_meta_parts = []
        startup_status = payload['startup_status'] or 'startup unknown'
        runtime_meta_parts.append(startup_status)
        runtime_meta_parts.append(f"warnings: {payload['warning_count']}")
        runtime_meta_parts.append(f"plugins: {payload['plugin_count']}")
        runtime_meta_parts.append(f"bookmarks: {payload['bookmarks_count']}")
        self._tiles['runtime'].set_content(
            value=runtime_value,
            meta=' • '.join(runtime_meta_parts),
            tone=tone,
        )

        self._tiles['graph'].set_content(
            value='Graph fields remain empty-valid',
            meta=(
                f"nodes={len(payload['nodes'])} • edges={len(payload['edges'])} • "
                f"hotspots={len(payload['hotspots'])} • focus={payload['focus_node_id'] or '(empty)'}"
            ),
            tone='idle' if not payload['nodes'] and not payload['edges'] else 'ok',
        )

        _refresh_widget_state(self)
        _refresh_widget_state(self._phase_chip)
        for tile in self._tiles.values():
            tile.refresh_visual_state()

    def refresh_now(self, snapshot: CloudflareGuardianDeckSnapshot | Mapping[str, Any] | object | None = None) -> None:
        if snapshot is not None:
            self.set_snapshot(snapshot)
        else:
            self.set_snapshot(self._snapshot)


class _ContextTile(QFrame):
    def __init__(self, heading: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('cloudflare_guardianContextSpineTile')

        self._heading_label = QLabel(heading, self)
        self._heading_label.setObjectName('cloudflare_guardianContextSpineTileHeading')

        self._value_label = QLabel('', self)
        self._value_label.setObjectName('cloudflare_guardianContextSpineTileValue')
        self._value_label.setWordWrap(True)
        self._value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self._meta_label = QLabel('', self)
        self._meta_label.setObjectName('cloudflare_guardianContextSpineTileMeta')
        self._meta_label.setWordWrap(True)
        self._meta_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        layout.addWidget(self._heading_label)
        layout.addWidget(self._value_label)
        layout.addWidget(self._meta_label)
        layout.addStretch(1)

    def set_content(self, *, value: str, meta: str, tone: str) -> None:
        self._value_label.setText(value)
        self._meta_label.setText(meta)
        self.setProperty('tone', tone)

    def refresh_visual_state(self) -> None:
        _refresh_widget_state(self)



def _coerce_snapshot(snapshot: CloudflareGuardianDeckSnapshot | Mapping[str, Any] | object) -> CloudflareGuardianDeckSnapshot:
    return CloudflareGuardianDeckSnapshot(**snapshot_payload(snapshot))



def _resolve_tone(payload: Mapping[str, Any]) -> str:
    if payload['startup_status'] == 'degraded' or payload['warning_count']:
        return 'warn'
    if payload['current_preview_relpath']:
        return 'ok'
    if payload['query_text']:
        return 'busy'
    if payload['repo_ready']:
        return 'ok'
    return 'idle'



def _phase_text(payload: Mapping[str, Any]) -> str:
    if payload['startup_status'] == 'degraded':
        return 'DEGRADED'
    if payload['current_preview_relpath']:
        return 'PREVIEW'
    if payload['query_text']:
        return 'SEARCH'
    if payload['repo_ready']:
        return 'READY'
    return 'IDLE'



def _note_text(payload: Mapping[str, Any]) -> str:
    if payload['startup_status'] == 'degraded':
        return 'The host surfaced degraded startup state. Consumers stay read-only and expose the warning pressure instead of inventing recovery flows.'
    if payload['current_preview_relpath']:
        return 'Preview context takes priority because it is the sharpest host evidence currently available to sibling widgets.'
    if payload['query_text'] and not payload['results_count']:
        return 'The snapshot keeps the active query visible even when zero results are returned, so sparse search states remain explicit.'
    if payload['repo_ready'] and not payload['current_preview_relpath']:
        return 'Repository context is live, but no preview has claimed focus yet. This is a merge-safe resting state.'
    return 'This surface stays intentionally informative under empty startup conditions and does not probe host internals on its own.'



def _refresh_widget_state(widget: QWidget) -> None:
    style = widget.style()
    if style is None:
        return
    try:
        style.unpolish(widget)
        style.polish(widget)
    except Exception:
        pass
    widget.update()


def _build_style_sheet(theme: DeckThemeBridge) -> str:
    panel = theme.role_palette('panel')
    ready = theme.status_palette('success')
    busy = theme.status_palette('accent')
    warn = theme.status_palette('warning')
    muted = theme.status_palette('muted')
    return f"""
QFrame#cloudflare_guardianContextSpine {{
    border: 1px solid {panel['border']};
    border-radius: 18px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {panel['surface_alt']},
        stop:0.62 {panel['surface']},
        stop:1 {theme.token('bg')});
}}
QLabel#cloudflare_guardianContextSpineTitle {{
    color: {panel['text']};
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.4px;
}}
QLabel#cloudflare_guardianContextSpinePhaseChip {{
    min-width: 84px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.1px;
    color: {panel['text']};
    background: {muted['soft']};
    border: 1px solid {muted['line']};
}}
QLabel#cloudflare_guardianContextSpinePhaseChip[tone="ok"] {{
    background: {ready['soft']};
    border-color: {ready['line']};
}}
QLabel#cloudflare_guardianContextSpinePhaseChip[tone="busy"] {{
    background: {busy['soft']};
    border-color: {busy['line']};
}}
QLabel#cloudflare_guardianContextSpinePhaseChip[tone="warn"] {{
    background: {warn['soft']};
    border-color: {warn['line']};
}}
QLabel#cloudflare_guardianContextSpineSubtitle {{
    color: {panel['muted']};
    font-size: 12px;
    line-height: 1.35;
}}
QLabel#cloudflare_guardianContextSpineNote {{
    color: {panel['soft_text']};
    font-size: 11px;
    line-height: 1.35;
    padding-top: 2px;
}}
QFrame#cloudflare_guardianContextSpineTile {{
    border-radius: 14px;
    border: 1px solid {panel['border']};
    background: {panel['surface']};
}}
QFrame#cloudflare_guardianContextSpineTile[tone="ok"] {{
    border-color: {ready['line']};
    background: {ready['soft']};
}}
QFrame#cloudflare_guardianContextSpineTile[tone="busy"] {{
    border-color: {busy['line']};
    background: {busy['soft']};
}}
QFrame#cloudflare_guardianContextSpineTile[tone="warn"] {{
    border-color: {warn['line']};
    background: {warn['soft']};
}}
QLabel#cloudflare_guardianContextSpineTileHeading {{
    color: {panel['soft_text']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.0px;
    text-transform: uppercase;
}}
QLabel#cloudflare_guardianContextSpineTileValue {{
    color: {panel['text']};
    font-size: 13px;
    font-weight: 700;
}}
QLabel#cloudflare_guardianContextSpineTileMeta {{
    color: {panel['muted']};
    font-size: 11px;
    line-height: 1.35;
}}
"""


__all__ = ['CloudflareGuardianContextSpine']


