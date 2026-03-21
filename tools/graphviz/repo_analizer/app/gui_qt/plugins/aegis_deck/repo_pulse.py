from __future__ import annotations

from typing import Any, Mapping

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .state_adapter import AegisDeckSnapshot, snapshot_payload
from .theme_bridge import DeckThemeBridge


class AegisRepoPulse(QFrame):
    """Snapshot consumer for deterministic repo, search, nav, and graph counters."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('aegisRepoPulse')
        self._snapshot = AegisDeckSnapshot()
        self._theme_bridge = DeckThemeBridge.coerce(None)

        self._title_label = QLabel('Repo pulse', self)
        self._title_label.setObjectName('aegisRepoPulseTitle')

        self._phase_chip = QLabel('', self)
        self._phase_chip.setObjectName('aegisRepoPulsePhaseChip')
        self._phase_chip.setAlignment(Qt.AlignCenter)

        self._status_label = QLabel('', self)
        self._status_label.setObjectName('aegisRepoPulseStatus')
        self._status_label.setWordWrap(True)
        self._status_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self._summary_label = QLabel('', self)
        self._summary_label.setObjectName('aegisRepoPulseSummary')
        self._summary_label.setWordWrap(True)
        self._summary_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self._footer_label = QLabel('', self)
        self._footer_label.setObjectName('aegisRepoPulseFooter')
        self._footer_label.setWordWrap(True)
        self._footer_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(8)
        header_row.addWidget(self._title_label, 1)
        header_row.addWidget(self._phase_chip, 0)

        self._metrics = {
            'files': _MetricTile('Indexed files', self),
            'exts': _MetricTile('Extensions', self),
            'results': _MetricTile('Results', self),
            'bookmarks': _MetricTile('Bookmarks', self),
            'warnings': _MetricTile('Warnings', self),
            'plugins': _MetricTile('Plugins', self),
        }

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(10)
        positions = [
            ('files', 0, 0),
            ('exts', 0, 1),
            ('results', 0, 2),
            ('bookmarks', 1, 0),
            ('warnings', 1, 1),
            ('plugins', 1, 2),
        ]
        for key, row, col in positions:
            grid.addWidget(self._metrics[key], row, col)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        layout.addLayout(header_row)
        layout.addWidget(self._status_label)
        layout.addWidget(self._summary_label)
        layout.addLayout(grid)
        layout.addWidget(self._footer_label)
        layout.addStretch(1)

        self.setStyleSheet(_build_style_sheet(self._theme_bridge))
        self.refresh_now(self._snapshot)

    def set_skin(self, tokens: object | None) -> None:
        self.set_theme_tokens(tokens)

    def set_theme_tokens(self, tokens: object | None) -> None:
        self._theme_bridge = DeckThemeBridge.coerce(tokens)
        self.setStyleSheet(_build_style_sheet(self._theme_bridge))

    def set_snapshot(self, snapshot: AegisDeckSnapshot | Mapping[str, Any] | object) -> None:
        self._snapshot = _coerce_snapshot(snapshot)
        payload = snapshot_payload(self._snapshot)
        tone = _resolve_tone(payload)
        self.setProperty('tone', tone)
        self._phase_chip.setProperty('tone', tone)
        self._phase_chip.setText(_phase_text(payload))

        self._status_label.setText(payload['status_text'] or 'No pulse signal yet.')
        self._summary_label.setText(_summary_text(payload))
        self._footer_label.setText(_footer_text(payload))

        self._metrics['files'].set_metric(
            value=str(payload['index_file_count']),
            meta=f"elapsed {payload['index_elapsed_sec']:.2f}s" if payload['index_elapsed_sec'] else 'No completed index elapsed time yet',
            tone='ok' if payload['index_file_count'] else 'idle',
        )
        self._metrics['exts'].set_metric(
            value=str(payload['index_ext_count']),
            meta=payload['active_extension'] or 'All extensions',
            tone='ok' if payload['index_ext_count'] else 'idle',
        )
        self._metrics['results'].set_metric(
            value=str(payload['results_count']),
            meta=payload['query_text'] or 'No active query',
            tone='busy' if payload['query_text'] else 'idle',
        )
        self._metrics['bookmarks'].set_metric(
            value=str(payload['bookmarks_count']),
            meta='Navigation memory ready' if payload['bookmarks_count'] else 'No saved preview bookmarks',
            tone='ok' if payload['bookmarks_count'] else 'idle',
        )
        self._metrics['warnings'].set_metric(
            value=str(payload['warning_count']),
            meta=payload['startup_status'] or 'startup unknown',
            tone='warn' if payload['warning_count'] or payload['startup_status'] == 'degraded' else 'ok',
        )
        self._metrics['plugins'].set_metric(
            value=str(payload['plugin_count']),
            meta='Loaded plugins observed from host diagnostics',
            tone='ok' if payload['plugin_count'] else 'idle',
        )

        _refresh_widget_state(self)
        _refresh_widget_state(self._phase_chip)
        for tile in self._metrics.values():
            tile.refresh_visual_state()

    def refresh_now(self, snapshot: AegisDeckSnapshot | Mapping[str, Any] | object | None = None) -> None:
        if snapshot is not None:
            self.set_snapshot(snapshot)
        else:
            self.set_snapshot(self._snapshot)


class _MetricTile(QFrame):
    def __init__(self, heading: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('aegisRepoPulseMetricTile')

        self._heading_label = QLabel(heading, self)
        self._heading_label.setObjectName('aegisRepoPulseMetricHeading')

        self._value_label = QLabel('', self)
        self._value_label.setObjectName('aegisRepoPulseMetricValue')
        self._value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self._meta_label = QLabel('', self)
        self._meta_label.setObjectName('aegisRepoPulseMetricMeta')
        self._meta_label.setWordWrap(True)
        self._meta_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(5)
        layout.addWidget(self._heading_label)
        layout.addWidget(self._value_label)
        layout.addWidget(self._meta_label)
        layout.addStretch(1)

    def set_metric(self, *, value: str, meta: str, tone: str) -> None:
        self._value_label.setText(value)
        self._meta_label.setText(meta)
        self.setProperty('tone', tone)

    def refresh_visual_state(self) -> None:
        _refresh_widget_state(self)



def _coerce_snapshot(snapshot: AegisDeckSnapshot | Mapping[str, Any] | object) -> AegisDeckSnapshot:
    return AegisDeckSnapshot(**snapshot_payload(snapshot))



def _resolve_tone(payload: Mapping[str, Any]) -> str:
    if payload['startup_status'] == 'degraded' or payload['warning_count']:
        return 'warn'
    if payload['query_text']:
        return 'busy'
    if payload['repo_ready'] or payload['current_preview_relpath']:
        return 'ok'
    return 'idle'



def _phase_text(payload: Mapping[str, Any]) -> str:
    if payload['startup_status'] == 'degraded':
        return 'DEGRADED'
    if payload['query_text']:
        return 'SEARCH'
    if payload['current_preview_relpath']:
        return 'PREVIEW'
    if payload['repo_ready']:
        return 'INDEXED'
    return 'IDLE'



def _summary_text(payload: Mapping[str, Any]) -> str:
    parts = []
    if payload['repo_name']:
        parts.append(payload['repo_name'])
    if payload['repo_root']:
        parts.append(payload['repo_root'])
    if payload['current_preview_relpath']:
        parts.append(payload['current_preview_relpath'])
    elif payload['query_text']:
        parts.append(f"query {payload['query_text']}")
    else:
        parts.append('No focused preview yet')
    return ' • '.join(part for part in parts if part)



def _footer_text(payload: Mapping[str, Any]) -> str:
    nav_text = f"back={payload['nav_can_go_back']} • forward={payload['nav_can_go_forward']}"
    graph_text = (
        f"graph contract empty-valid: nodes={len(payload['nodes'])} • edges={len(payload['edges'])} • "
        f"hotspots={len(payload['hotspots'])} • focus={payload['focus_node_id'] or '(empty)'}"
    )
    if payload['startup_status'] == 'degraded':
        return f"{nav_text} • degraded startup remains visible to downstream consumers • {graph_text}"
    if payload['query_text'] and not payload['results_count']:
        return f"{nav_text} • zero-result searches stay explicit instead of being softened away • {graph_text}"
    if payload['current_preview_relpath']:
        return f"{nav_text} • preview kind={payload['current_preview_kind'] or 'unknown'} • {graph_text}"
    return f"{nav_text} • pulse stays deterministic under sparse startup data • {graph_text}"



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
QFrame#aegisRepoPulse {{
    border: 1px solid {panel['border']};
    border-radius: 18px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 {panel['surface_alt']},
        stop:0.52 {panel['surface']},
        stop:1 {theme.token('bg')});
}}
QLabel#aegisRepoPulseTitle {{
    color: {panel['text']};
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.4px;
}}
QLabel#aegisRepoPulsePhaseChip {{
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
QLabel#aegisRepoPulsePhaseChip[tone="ok"] {{
    background: {ready['soft']};
    border-color: {ready['line']};
}}
QLabel#aegisRepoPulsePhaseChip[tone="busy"] {{
    background: {busy['soft']};
    border-color: {busy['line']};
}}
QLabel#aegisRepoPulsePhaseChip[tone="warn"] {{
    background: {warn['soft']};
    border-color: {warn['line']};
}}
QLabel#aegisRepoPulseStatus {{
    color: {panel['text']};
    font-size: 18px;
    font-weight: 700;
    line-height: 1.2;
}}
QLabel#aegisRepoPulseSummary {{
    color: {panel['muted']};
    font-size: 12px;
    line-height: 1.35;
}}
QLabel#aegisRepoPulseFooter {{
    color: {panel['soft_text']};
    font-size: 11px;
    line-height: 1.35;
}}
QFrame#aegisRepoPulseMetricTile {{
    border-radius: 14px;
    border: 1px solid {panel['border']};
    background: {panel['surface']};
}}
QFrame#aegisRepoPulseMetricTile[tone="ok"] {{
    border-color: {ready['line']};
    background: {ready['soft']};
}}
QFrame#aegisRepoPulseMetricTile[tone="busy"] {{
    border-color: {busy['line']};
    background: {busy['soft']};
}}
QFrame#aegisRepoPulseMetricTile[tone="warn"] {{
    border-color: {warn['line']};
    background: {warn['soft']};
}}
QLabel#aegisRepoPulseMetricHeading {{
    color: {panel['soft_text']};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.0px;
    text-transform: uppercase;
}}
QLabel#aegisRepoPulseMetricValue {{
    color: {panel['text']};
    font-size: 20px;
    font-weight: 800;
}}
QLabel#aegisRepoPulseMetricMeta {{
    color: {panel['muted']};
    font-size: 11px;
    line-height: 1.3;
}}
"""


__all__ = ['AegisRepoPulse']
