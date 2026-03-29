from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Callable

from PySide6.QtCore import QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QBoxLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .snapshot_model import (
    coerce_bool as _snapshot_coerce_bool,
    coerce_float as _snapshot_coerce_float,
    coerce_int as _snapshot_coerce_int,
    coerce_list as _snapshot_coerce_list,
    coerce_mapping as _snapshot_coerce_mapping,
    coerce_string as _snapshot_coerce_string,
    empty_snapshot as _snapshot_empty,
    format_elapsed as _snapshot_format_elapsed,
    normalize_snapshot as _normalize_snapshot_payload,
)
from .spec_factory import (
    action_spec as _build_action_spec,
    command_spec as _build_command_spec,
)
from .deck_host_runtime import DeckHostRuntimeCoordinator
from .deck_runtime import DeckRuntimeCoordinator

_WIDGET_MODULES: dict[str, tuple[str, str]] = {
    'command_bar': ('command_bar', 'CloudflareGuardianCommandBar'),
    'action_rail': ('action_rail', 'CloudflareGuardianActionRail'),
    'context_spine': ('context_spine', 'CloudflareGuardianContextSpine'),
    'repo_pulse': ('repo_pulse', 'CloudflareGuardianRepoPulse'),
    'graph_radar': ('graph_radar', 'CloudflareGuardianGraphRadar'),
    'deck_surface': ('deck_surface', 'CloudflareGuardianDeckSurface'),
    'theme_bridge': ('theme_bridge', 'DeckThemeBridge'),
    'motion': ('motion', 'DeckStateAnimator'),
    'state_adapter': ('state_adapter', 'CloudflareGuardianStateAdapter'),
}
_THEME_DEFAULTS: dict[str, str] = {
    'bg': '#0d1118',
    'bg_alt': '#101723',
    'bg_elevated': '#151e2b',
    'panel': '#182231',
    'panel_alt': '#202b3c',
    'panel_hover': '#253246',
    'panel_active': '#2b3c55',
    'text': '#edf3fb',
    'text_muted': '#9caabd',
    'text_soft': '#7b899a',
    'accent': '#dca269',
    'accent_soft': '#322416',
    'accent_glow': '#dca26933',
    'success': '#5dc48f',
    'warning': '#d8b268',
    'danger': '#d48087',
    'border': '#2b384a',
    'border_soft': '#253243',
    'border_strong': '#425470',
    'focus_ring': '#dca2696a',
    'scrollbar': '#4f5d70',
    'scrollbar_hover': '#dca269',
    'shadow': '#0000009f',
    'code_bg': '#0b1118',
    'code_line': '#15202d',
}

_SECTION_MIN_HEIGHTS: dict[str, int] = {
    'command_bar': 320,
    'action_rail': 300,
    'context_spine': 250,
    'repo_pulse': 250,
    'graph_radar': 360,
}
_COMPACT_BREAKPOINT_PX = 980


@dataclass
class _SectionBinding:
    root: QWidget
    surface: Any = None
    title_label: QLabel | None = None
    subtitle_label: QLabel | None = None
    status_label: QLabel | None = None
    fallback: '_FallbackSlate | None' = None
    has_real_content: bool = False

    def set_subtitle(self, text: str) -> None:
        if self.surface is not None and hasattr(self.surface, 'set_subtitle'):
            try:
                self.surface.set_subtitle(text)
                return
            except Exception:
                pass
        if self.subtitle_label is not None:
            self.subtitle_label.setText(text)
            self.subtitle_label.setVisible(bool(text))

    def set_status(self, text: str, tone: str = 'muted') -> None:
        if self.surface is not None:
            if hasattr(self.surface, 'set_status_text'):
                try:
                    self.surface.set_status_text(text)
                except Exception:
                    pass
            if hasattr(self.surface, 'set_status_tone'):
                try:
                    self.surface.set_status_tone(tone)
                except Exception:
                    pass
            return
        if self.status_label is not None:
            self.status_label.setText(text)
            self.status_label.setProperty('tone', tone)
            self.status_label.setVisible(bool(text))
            self.status_label.style().unpolish(self.status_label)
            self.status_label.style().polish(self.status_label)


class _TonePill(QLabel):
    def __init__(self, text: str = '', tone: str = 'muted', parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('cloudflare_guardianDeckTonePill')
        self.setAlignment(Qt.AlignCenter)
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.setProperty('tone', tone)
        self.setVisible(bool(text))
        self.setText(text)

    def set_pill(self, text: str, tone: str = 'muted') -> None:
        self.setText(text)
        self.setProperty('tone', tone)
        self.setVisible(bool(text))
        self.style().unpolish(self)
        self.style().polish(self)


class _MetricCard(QFrame):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('cloudflare_guardianDeckMetricCard')
        self.setFrameShape(QFrame.NoFrame)
        self.setProperty('tone', 'muted')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 9, 10, 9)
        layout.setSpacing(3)

        self._eyebrow = QLabel(title, self)
        self._eyebrow.setObjectName('cloudflare_guardianDeckMetricEyebrow')
        layout.addWidget(self._eyebrow)

        self._value = QLabel('0', self)
        self._value.setObjectName('cloudflare_guardianDeckMetricValue')
        layout.addWidget(self._value)

        self._caption = QLabel('', self)
        self._caption.setObjectName('cloudflare_guardianDeckMetricCaption')
        self._caption.setWordWrap(True)
        layout.addWidget(self._caption)

        self._detail = QLabel('', self)
        self._detail.setObjectName('cloudflare_guardianDeckMetricDetail')
        self._detail.setWordWrap(True)
        layout.addWidget(self._detail)

    def set_card(self, value: object, caption: str, detail: str = '', *, tone: str = 'muted') -> None:
        self._value.setText(str(value))
        self._caption.setText(caption)
        self._detail.setText(detail)
        self._detail.setVisible(bool(detail))
        self.setProperty('tone', tone)
        self.style().unpolish(self)
        self.style().polish(self)


class _BridgeAmbientRibbon(QWidget):
    """Low-cost ambient signal strip to keep the bridge subtly alive."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('cloudflare_guardianDeckBridgeAmbient')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(8)
        self._phase = 0.0
        self._active = True
        self._tokens = dict(_THEME_DEFAULTS)
        self._timer = QTimer(self)
        self._timer.setInterval(140)
        self._timer.timeout.connect(self._advance)
        self._timer.start()

    def set_active(self, active: bool) -> None:
        self._active = bool(active)
        if self._active:
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def _advance(self) -> None:
        if not self._active:
            return
        self._phase = (self._phase + 0.06) % 1.0
        self.update()

    def set_tokens(self, tokens: Mapping[str, object] | None) -> None:
        if not isinstance(tokens, Mapping):
            return
        for key in (
            'panel',
            'panel_alt',
            'accent',
            'selection',
            'border_soft',
            'text',
        ):
            value = tokens.get(key)
            if value:
                self._tokens[key] = str(value)
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        rect = QRectF(self.rect().adjusted(0, 1, 0, -1))
        if rect.width() <= 0 or rect.height() <= 0:
            return

        base = QColor(self._tokens.get('panel', _THEME_DEFAULTS['panel']))
        base.setAlpha(180 if self._active else 110)
        painter.setPen(Qt.NoPen)
        painter.setBrush(base)
        painter.drawRoundedRect(rect, 4.0, 4.0)

        glow = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
        center = self._phase
        left = max(0.0, center - 0.26)
        right = min(1.0, center + 0.26)
        accent = QColor(self._tokens.get('accent', _THEME_DEFAULTS['accent']))
        low = QColor(accent)
        low.setAlpha(22)
        mid = QColor(accent)
        mid.setAlpha(34)
        high = QColor(accent)
        high.setAlpha(118 if self._active else 56)
        glow.setColorAt(0.0, low)
        glow.setColorAt(left, mid)
        glow.setColorAt(center, high)
        glow.setColorAt(right, mid)
        glow.setColorAt(1.0, low)
        painter.setBrush(glow)
        painter.drawRoundedRect(rect, 4.0, 4.0)

        tracer_x = rect.left() + (rect.width() * center)
        tracer = QRectF(tracer_x - 16.0, rect.top() + 1.0, 32.0, rect.height() - 2.0)
        tracer_color = QColor(self._tokens.get('selection', self._tokens.get('accent', _THEME_DEFAULTS['accent'])))
        tracer_color.setAlpha(96 if self._active else 48)
        painter.setBrush(tracer_color)
        painter.drawRoundedRect(tracer, 3.0, 3.0)


class _TopologyPlaceholder(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('cloudflare_guardianDeckTopologyPlaceholder')
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(6)

        self._title = QLabel('Topology radar is cold until first activation.', self)
        self._title.setObjectName('cloudflare_guardianDeckTopologyPlaceholderTitle')
        self._title.setWordWrap(True)
        layout.addWidget(self._title)

        self._detail = QLabel(
            'Open the Topology tab to construct graph widgets lazily and avoid background churn while hidden.',
            self,
        )
        self._detail.setObjectName('cloudflare_guardianDeckTopologyPlaceholderDetail')
        self._detail.setWordWrap(True)
        layout.addWidget(self._detail)
        layout.addStretch(1)


class _ColdStartPlaceholder(QFrame):
    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        object_name: str,
        title: str,
        detail: str,
    ) -> None:
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        headline = QLabel(title, self)
        headline.setObjectName('cloudflare_guardianDeckColdPlaceholderTitle')
        headline.setWordWrap(True)
        layout.addWidget(headline)
        subtitle = QLabel(detail, self)
        subtitle.setObjectName('cloudflare_guardianDeckColdPlaceholderDetail')
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)
        layout.addStretch(1)


class _FallbackSlate(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('cloudflare_guardianDeckFallbackSlate')
        self.setFrameShape(QFrame.NoFrame)
        self.setProperty('tone', 'muted')
        self.setProperty('interactive', False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        self._headline = QLabel('', self)
        self._headline.setObjectName('cloudflare_guardianDeckFallbackHeadline')
        self._headline.setWordWrap(True)
        layout.addWidget(self._headline)

        self._detail = QLabel('', self)
        self._detail.setObjectName('cloudflare_guardianDeckFallbackDetail')
        self._detail.setWordWrap(True)
        layout.addWidget(self._detail)

        self._footer = QLabel('', self)
        self._footer.setObjectName('cloudflare_guardianDeckFallbackFooter')
        self._footer.setWordWrap(True)
        layout.addWidget(self._footer)
        layout.addStretch(1)

    def set_copy(self, headline: str, detail: str, footer: str = '', *, tone: str = 'muted') -> None:
        self._headline.setText(headline)
        self._detail.setText(detail)
        self._footer.setText(footer)
        self._footer.setVisible(bool(footer))
        self.setProperty('tone', tone)
        self.style().unpolish(self)
        self.style().polish(self)


class CloudflareGuardianDeckShell(QWidget):
    """Dock-local orchestrator for the Cloudflare Guardian Diagnostics sibling slices."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName('cloudflare_guardianDeckShellRoot')
        self.setProperty('visualRole', 'plugin-dock-root')
        self.setProperty('visualTier', 'themed')
        self.setProperty('premium', True)

        self._plugin_context = None
        self._dispatcher = None
        self._container = None
        self._event_bus = None
        self._main_window = None
        self._host_runtime = DeckHostRuntimeCoordinator()
        self._snapshot_payload_fn: Callable[[Any], Any] | None = None
        self._state_adapter = None
        self._compatibility_notes: list[str] = []
        self._runtime = DeckRuntimeCoordinator(logger=self._trace_runtime)
        self._snapshot: dict[str, Any] = self._empty_snapshot()
        self._runtime.push_snapshot(self._snapshot)
        self._theme_tokens = dict(_THEME_DEFAULTS)

        self._surface_cls = self._optional_symbol(*_WIDGET_MODULES['deck_surface'])
        self._theme_bridge_cls = self._optional_symbol(*_WIDGET_MODULES['theme_bridge'])
        self._motion_cls = self._optional_symbol(*_WIDGET_MODULES['motion'])
        self._state_adapter_cls = self._optional_symbol(*_WIDGET_MODULES['state_adapter'])
        self._command_bar_cls = self._optional_symbol(*_WIDGET_MODULES['command_bar'])
        self._action_rail_cls = self._optional_symbol(*_WIDGET_MODULES['action_rail'])
        self._context_spine_cls = self._optional_symbol(*_WIDGET_MODULES['context_spine'])
        self._repo_pulse_cls = self._optional_symbol(*_WIDGET_MODULES['repo_pulse'])
        self._graph_radar_cls = self._optional_symbol(*_WIDGET_MODULES['graph_radar'])

        self._command_bar = None
        self._action_rail = None
        self._context_spine = self._instantiate_optional(self._context_spine_cls)
        self._repo_pulse = self._instantiate_optional(self._repo_pulse_cls)
        self._graph_radar = None
        self._animator = self._instantiate_optional(self._motion_cls)

        self._hero_title_label: QLabel | None = None
        self._hero_subtitle_label: QLabel | None = None
        self._hero_runtime_pill: _TonePill | None = None
        self._hero_repo_pill: _TonePill | None = None
        self._hero_graph_pill: _TonePill | None = None
        self._hero_summary_label: QLabel | None = None
        self._hero_focus_label: QLabel | None = None
        self._bridge_ambient: _BridgeAmbientRibbon | None = None
        self._bridge_tabs_summary: QLabel | None = None
        self._availability_label: QLabel | None = None
        self._compatibility_label: QLabel | None = None
        self._section_bindings: dict[str, _SectionBinding] = {}
        self._metric_cards: dict[str, _MetricCard] = {}
        self._tabs: QTabWidget | None = None
        self._tab_scrolls: dict[str, QScrollArea] = {}
        self._tab_layouts: dict[str, QVBoxLayout] = {}
        self._tab_dirty: set[str] = self._runtime.tab_dirty
        self._active_tab_id = self._runtime.active_tab_id
        self._topology_summary_label: QLabel | None = None
        self._workbench_strip_label: QLabel | None = None
        self._controls_layout: QBoxLayout | None = None
        self._command_section_root: QWidget | None = None
        self._action_section_root: QWidget | None = None
        self._briefing_context_root: QWidget | None = None
        self._briefing_pulse_root: QWidget | None = None
        self._topology_radar_root: QWidget | None = None
        self._topology_placeholder: _TopologyPlaceholder | None = None
        self._workbench_command_placeholder: _ColdStartPlaceholder | None = None
        self._workbench_action_placeholder: _ColdStartPlaceholder | None = None
        self._metric_signature: dict[str, tuple[object, ...]] = {}
        self._layout_mode: str = ''

        self._build_layout()
        self._apply_local_styles()
        self._wire_widget_contracts()
        self._refresh_shell_chrome()

    def bind_plugin_context(self, context: Any) -> None:
        self._plugin_context = context
        if context is None:
            return

        self._host_runtime.bind_plugin_context(context)
        self._dispatcher = self._host_runtime.dispatcher
        self._container = getattr(context, 'container', None)
        self._event_bus = getattr(context, 'event_bus', None)
        self._main_window = self._safe_container_get('main_window')
        self._snapshot_payload_fn = self._resolve_snapshot_payload_fn()
        self._host_runtime.set_snapshot_payload_fn(self._snapshot_payload_fn)
        self._theme_tokens = self._resolve_theme_tokens()

        self._attach_optional_state_adapter()
        self._push_dispatcher_to_controls()
        self._push_theme_to_visuals()
        self._push_snapshot(self._snapshot)
        self._apply_local_styles()

    def refresh_from_state(self) -> dict[str, Any]:
        snapshot = self._build_current_snapshot()
        self._push_snapshot(snapshot)
        return dict(self._snapshot)

    def set_skin(self, tokens: Any) -> None:
        self._theme_tokens = self._resolve_theme_tokens(tokens)
        self._push_theme_to_visuals()
        self._apply_local_styles()
        self._refresh_shell_chrome()
        self._update_tab_activity(runtime_visible=self.isVisible())

    def set_theme_tokens(self, tokens: Any) -> None:
        self.set_skin(tokens)

    def shutdown(self) -> None:
        if self._state_adapter is not None and hasattr(self._state_adapter, 'shutdown'):
            try:
                self._state_adapter.shutdown()
            except Exception:
                pass
        self._state_adapter = None
        self._host_runtime.set_state_adapter(None)
        if self._animator is not None and hasattr(self._animator, 'stop'):
            try:
                self._animator.stop()
            except Exception:
                pass

    def compatibility_notes(self) -> list[str]:
        return list(self._compatibility_notes)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._apply_layout_mode()

    def _apply_layout_mode(self, *, force: bool = False) -> None:
        controls = self._controls_layout
        if controls is None:
            return

        compact = self.width() < _COMPACT_BREAKPOINT_PX
        next_mode = 'compact' if compact else 'wide'
        if not force and next_mode == self._layout_mode:
            return
        self._layout_mode = next_mode
        self.setProperty('compactMode', 'true' if compact else 'false')
        if self._tabs is not None:
            self._tabs.setProperty('compactMode', 'true' if compact else 'false')
        self._repolish_widget(self)

        if compact:
            controls.setDirection(QBoxLayout.TopToBottom)
            controls.setSpacing(8)
            if self._command_section_root is not None:
                self._command_section_root.setMinimumHeight(286)
            if self._action_section_root is not None:
                self._action_section_root.setMinimumHeight(254)
        else:
            controls.setDirection(QBoxLayout.LeftToRight)
            controls.setSpacing(12)
            if self._command_section_root is not None:
                self._command_section_root.setMinimumHeight(_SECTION_MIN_HEIGHTS['command_bar'])
            if self._action_section_root is not None:
                self._action_section_root.setMinimumHeight(_SECTION_MIN_HEIGHTS['action_rail'])

    def _build_layout(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 10)
        root.setSpacing(8)

        bridge = self._make_hero_panel()
        bridge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        root.addWidget(bridge, 0)
        root.addWidget(self._make_metric_strip(), 0)

        self._tabs = QTabWidget(self)
        self._tabs.setObjectName('cloudflare_guardianDeckTabs')
        self._tabs.setDocumentMode(True)
        self._tabs.setUsesScrollButtons(False)
        self._tabs.setElideMode(Qt.ElideNone)
        self._tabs.currentChanged.connect(self._on_tab_changed)
        root.addWidget(self._tabs, 1)

        briefing_layout = self._create_tab('briefing', 'Briefing')
        workbench_layout = self._create_tab('workbench', 'Workbench')
        topology_layout = self._create_tab('topology', 'Topology')

        self._briefing_context_root = self._create_section(
            section_id='context_spine',
            title='Context Spine',
            subtitle='Canonical status reading lane for repo, query, preview, and runtime posture.',
            content_widget=self._context_spine,
            missing_note='context_spine.py is absent in this lane package, so snapshot delivery is preserved but the shell does not impersonate repo context widgets.',
        ).root
        self._briefing_pulse_root = self._create_section(
            section_id='repo_pulse',
            title='Repo Pulse',
            subtitle='Deterministic counters and startup pressure signals from canonical snapshot state.',
            content_widget=self._repo_pulse,
            missing_note='repo_pulse.py is absent in this lane package, so the shell keeps repository pulse messaging local and sparse-data safe.',
        ).root
        if self._briefing_context_root is not None:
            self._briefing_context_root.setMinimumHeight(_SECTION_MIN_HEIGHTS['context_spine'])
            briefing_layout.addWidget(self._briefing_context_root)
        if self._briefing_pulse_root is not None:
            self._briefing_pulse_root.setMinimumHeight(_SECTION_MIN_HEIGHTS['repo_pulse'])
            briefing_layout.addWidget(self._briefing_pulse_root)
        briefing_layout.addWidget(self._make_assembly_panel())
        briefing_layout.addStretch(1)

        workbench_strip = QFrame(self)
        workbench_strip.setObjectName('cloudflare_guardianDeckWorkbenchStrip')
        workbench_strip.setFrameShape(QFrame.NoFrame)
        strip_layout = QHBoxLayout(workbench_strip)
        strip_layout.setContentsMargins(12, 10, 12, 10)
        strip_layout.setSpacing(8)
        self._workbench_strip_label = QLabel('', workbench_strip)
        self._workbench_strip_label.setObjectName('cloudflare_guardianDeckWorkbenchStripText')
        self._workbench_strip_label.setWordWrap(True)
        strip_layout.addWidget(self._workbench_strip_label)
        workbench_layout.addWidget(workbench_strip)

        controls_row = QWidget(self)
        controls_row.setObjectName('cloudflare_guardianDeckControlsRow')
        controls_row.setProperty('visualRole', 'deck-row')
        controls_row.setProperty('visualTier', 'themed')
        self._controls_layout = QHBoxLayout(controls_row)
        self._controls_layout.setContentsMargins(0, 0, 0, 0)
        self._controls_layout.setSpacing(12)

        self._workbench_command_placeholder = _ColdStartPlaceholder(
            self,
            object_name='cloudflare_guardianDeckWorkbenchCommandPlaceholder',
            title='Command lane is cold until Workbench activation.',
            detail='CloudflareGuardian defers command-surface construction to reduce startup pressure and hidden-state churn.',
        )
        self._command_section_root = self._create_section(
            section_id='command_bar',
            title='Command Bar',
            subtitle='Operational command lane with dispatcher-backed execution and filtered search.',
            content_widget=self._workbench_command_placeholder,
            missing_note='command_bar.py is absent in this lane package, so the shell keeps the slot warm with canonical command metadata and no substitute discovery.',
        ).root
        self._workbench_action_placeholder = _ColdStartPlaceholder(
            self,
            object_name='cloudflare_guardianDeckWorkbenchActionPlaceholder',
            title='Action lane is cold until Workbench activation.',
            detail='The action rail is instantiated only when Workbench becomes foreground, keeping hidden tabs near-cold.',
        )
        self._action_section_root = self._create_section(
            section_id='action_rail',
            title='Action Rail',
            subtitle='High-frequency action lane that exposes deterministic operation intents.',
            content_widget=self._workbench_action_placeholder,
            missing_note='action_rail.py is absent in this lane package, so the shell keeps action intent visible without creating a parallel control system.',
        ).root
        if self._command_section_root is not None:
            self._command_section_root.setMinimumHeight(_SECTION_MIN_HEIGHTS['command_bar'])
            self._controls_layout.addWidget(self._command_section_root, 3)
        if self._action_section_root is not None:
            self._action_section_root.setMinimumHeight(_SECTION_MIN_HEIGHTS['action_rail'])
            self._controls_layout.addWidget(self._action_section_root, 2)
        command_binding = self._section_bindings.get('command_bar')
        if command_binding is not None:
            command_binding.has_real_content = False
            command_binding.set_status('cold start ready', 'muted')
            command_binding.set_subtitle('Command lane is instantiated lazily on first Workbench activation.')
        action_binding = self._section_bindings.get('action_rail')
        if action_binding is not None:
            action_binding.has_real_content = False
            action_binding.set_status('cold start ready', 'muted')
            action_binding.set_subtitle('Action lane is instantiated lazily on first Workbench activation.')
        workbench_layout.addWidget(controls_row, 1)

        topology_summary = QFrame(self)
        topology_summary.setObjectName('cloudflare_guardianDeckTopologySummary')
        topology_summary.setFrameShape(QFrame.NoFrame)
        topology_layout_box = QVBoxLayout(topology_summary)
        topology_layout_box.setContentsMargins(12, 10, 12, 10)
        topology_layout_box.setSpacing(4)
        topology_title = QLabel('Topology focus', topology_summary)
        topology_title.setObjectName('cloudflare_guardianDeckTopologySummaryTitle')
        topology_layout_box.addWidget(topology_title)
        self._topology_summary_label = QLabel('', topology_summary)
        self._topology_summary_label.setObjectName('cloudflare_guardianDeckTopologySummaryText')
        self._topology_summary_label.setWordWrap(True)
        topology_layout_box.addWidget(self._topology_summary_label)
        topology_layout.addWidget(topology_summary)

        self._topology_placeholder = _TopologyPlaceholder(self)
        self._topology_radar_root = self._create_section(
            section_id='graph_radar',
            title='Graph Radar',
            subtitle='Topology lane. Canonical graph fields only: nodes, edges, hotspots, focus_node_id.',
            content_widget=self._topology_placeholder,
            missing_note='graph_radar.py is absent in this lane package, so Topology stays placeholder-only and preserves empty-valid graph fields.',
        ).root
        if self._topology_radar_root is not None:
            self._topology_radar_root.setMinimumHeight(_SECTION_MIN_HEIGHTS['graph_radar'])
            topology_layout.addWidget(self._topology_radar_root, 1)
        radar_binding = self._section_bindings.get('graph_radar')
        if radar_binding is not None:
            radar_binding.set_status('cold start ready', 'muted')
            radar_binding.set_subtitle('Graph radar is constructed on first Topology activation.')
        topology_layout.addStretch(1)

        if self._tabs is not None:
            self._tabs.setCurrentIndex(0)
        self._active_tab_id = 'briefing'
        self._tab_dirty = {'briefing', 'workbench', 'topology'}
        self._apply_layout_mode(force=True)
        self._update_tab_activity(runtime_visible=True)

    def _create_tab(self, tab_id: str, title: str) -> QVBoxLayout:
        if self._tabs is None:
            raise RuntimeError('Tab host is not initialized')
        page = QWidget(self._tabs)
        page.setObjectName(f'cloudflare_guardianDeckTabPage_{tab_id}')
        page_root = QVBoxLayout(page)
        page_root.setContentsMargins(0, 0, 0, 0)
        page_root.setSpacing(0)

        scroll = QScrollArea(page)
        scroll.setObjectName(f'cloudflare_guardianDeckTabScroll_{tab_id}')
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.verticalScrollBar().setSingleStep(24)
        scroll.verticalScrollBar().setPageStep(220)
        page_root.addWidget(scroll, 1)

        content = QWidget(scroll)
        content.setObjectName(f'cloudflare_guardianDeckTabContent_{tab_id}')
        scroll.setWidget(content)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(6, 8, 6, 16)
        content_layout.setSpacing(12)

        self._tab_scrolls[tab_id] = scroll
        self._tab_layouts[tab_id] = content_layout
        self._tabs.addTab(page, title)
        return content_layout

    def _make_assembly_panel(self) -> QWidget:
        assembly_panel = QFrame(self)
        assembly_panel.setObjectName('cloudflare_guardianDeckAssemblyPanel')
        assembly_panel.setFrameShape(QFrame.NoFrame)
        assembly_panel.setProperty('visualRole', 'deck-status-strip')
        assembly_panel.setProperty('visualTier', 'themed')
        assembly_layout = QVBoxLayout(assembly_panel)
        assembly_layout.setContentsMargins(16, 14, 16, 14)
        assembly_layout.setSpacing(6)

        assembly_title = QLabel('Assembly posture', assembly_panel)
        assembly_title.setObjectName('cloudflare_guardianDeckAssemblyTitle')
        assembly_layout.addWidget(assembly_title)

        self._availability_label = QLabel('', assembly_panel)
        self._availability_label.setObjectName('cloudflare_guardianDeckAssemblyAvailability')
        self._availability_label.setWordWrap(True)
        assembly_layout.addWidget(self._availability_label)

        self._compatibility_label = QLabel('', assembly_panel)
        self._compatibility_label.setObjectName('cloudflare_guardianDeckAssemblyCompatibility')
        self._compatibility_label.setWordWrap(True)
        assembly_layout.addWidget(self._compatibility_label)
        return assembly_panel

    def _on_tab_changed(self, index: int) -> None:
        next_tab = self._runtime.set_active_tab_from_index(int(index))
        self._active_tab_id = next_tab
        if next_tab == 'workbench':
            self._ensure_workbench_controls()
        if next_tab == 'topology':
            self._ensure_topology_radar()
        if next_tab in self._tab_dirty:
            self._apply_tab_refresh(next_tab)
        self._update_tab_activity(runtime_visible=self.isVisible())
        self._refresh_shell_chrome()
        if self.isVisible():
            self._animate_tab_entry(next_tab)

    def _apply_tab_refresh(self, tab_id: str) -> None:
        snapshot = dict(self._snapshot)
        if tab_id == 'workbench':
            self._ensure_workbench_controls()
            self._refresh_workbench(snapshot)
        elif tab_id == 'topology':
            self._ensure_topology_radar()
            self._refresh_topology(snapshot)
        else:
            self._refresh_briefing(snapshot)
        self._runtime.mark_refreshed(tab_id)

    def _ensure_workbench_controls(self) -> None:
        command_binding = self._section_bindings.get('command_bar')
        action_binding = self._section_bindings.get('action_rail')

        if self._command_bar is None:
            command_widget = self._instantiate_optional(self._command_bar_cls)
            if command_widget is not None:
                self._command_bar = command_widget
                self._push_dispatcher_to_controls()
                self._apply_theme_to_widget(self._command_bar)
                if command_binding is not None and command_binding.surface is not None:
                    if self._maybe_call(command_binding.surface, 'set_content_widget', self._command_bar):
                        command_binding.has_real_content = True
                        command_binding.set_status('ready', 'success')
                elif self._workbench_command_placeholder is not None:
                    self._replace_placeholder_with_widget(self._workbench_command_placeholder, self._command_bar)
                self._tab_dirty.add('workbench')

        if self._action_rail is None:
            action_widget = self._instantiate_optional(self._action_rail_cls)
            if action_widget is not None:
                self._action_rail = action_widget
                self._push_dispatcher_to_controls()
                self._apply_theme_to_widget(self._action_rail)
                if action_binding is not None and action_binding.surface is not None:
                    if self._maybe_call(action_binding.surface, 'set_content_widget', self._action_rail):
                        action_binding.has_real_content = True
                        action_binding.set_status('ready', 'success')
                elif self._workbench_action_placeholder is not None:
                    self._replace_placeholder_with_widget(self._workbench_action_placeholder, self._action_rail)
                self._tab_dirty.add('workbench')

    @staticmethod
    def _replace_placeholder_with_widget(placeholder: QWidget, widget: QWidget) -> None:
        parent = placeholder.parentWidget()
        if parent is None:
            return
        layout = parent.layout()
        if layout is None:
            return
        try:
            layout.replaceWidget(placeholder, widget)
            placeholder.setParent(None)
            widget.setParent(parent)
            widget.show()
        except Exception:
            return

    def _ensure_topology_radar(self) -> QWidget | None:
        if self._graph_radar is not None:
            return self._graph_radar
        radar = self._instantiate_optional(self._graph_radar_cls)
        if radar is None:
            return None

        self._graph_radar = radar
        self._apply_theme_to_widget(radar)
        self._maybe_call(radar, 'set_animation_enabled', False)

        binding = self._section_bindings.get('graph_radar')
        attached = False
        if binding is not None and binding.surface is not None:
            attached = self._maybe_call(binding.surface, 'set_content_widget', radar)
            if attached:
                binding.has_real_content = True

        if not attached and self._topology_placeholder is not None:
            parent = self._topology_placeholder.parentWidget()
            layout = parent.layout() if parent is not None else None
            if layout is not None:
                try:
                    layout.replaceWidget(self._topology_placeholder, radar)
                    self._topology_placeholder.setParent(None)
                    radar.setParent(parent)
                    radar.show()
                    attached = True
                except Exception:
                    attached = False

        if attached:
            self._tab_dirty.add('topology')
        return self._graph_radar

    def _update_tab_activity(self, *, runtime_visible: bool) -> None:
        graph_active = runtime_visible and (self._active_tab_id == 'topology')
        if self._graph_radar is not None:
            self._maybe_call(self._graph_radar, 'set_animation_enabled', graph_active)
        active_tab = self._active_tab_id if runtime_visible else ''
        for section_id, binding in self._section_bindings.items():
            surface = binding.surface
            if surface is None:
                continue
            owner = self._section_owner_tab(section_id)
            self._maybe_call(surface, 'set_animation_enabled', owner == active_tab)
        if self._bridge_ambient is not None:
            self._bridge_ambient.set_active(runtime_visible)

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self._runtime.set_runtime_visible(True)
        self._update_tab_activity(runtime_visible=True)

    def hideEvent(self, event) -> None:  # type: ignore[override]
        super().hideEvent(event)
        self._runtime.set_runtime_visible(False)
        self._update_tab_activity(runtime_visible=False)

    @staticmethod
    def _section_owner_tab(section_id: str) -> str:
        return DeckRuntimeCoordinator.SECTION_OWNER.get(section_id, '')

    def _animate_tab_entry(self, tab_id: str) -> None:
        if self._animator is None:
            return
        scroll = self._tab_scrolls.get(tab_id)
        if scroll is not None and isinstance(scroll.widget(), QWidget):
            self._animator.fade_widget(
                scroll.widget(),
                key=f'tab-enter:{tab_id}',
                start=0.88,
                end=1.0,
                duration_ms=180,
            )
        if self._bridge_tabs_summary is not None:
            self._animator.fade_widget(
                self._bridge_tabs_summary,
                key='bridge-tab-indicator',
                start=0.7,
                end=1.0,
                duration_ms=160,
            )

    def _make_hero_panel(self) -> QWidget:
        panel = QFrame(self)
        panel.setObjectName('cloudflare_guardianDeckHeroPanel')
        panel.setFrameShape(QFrame.NoFrame)
        panel.setProperty('visualRole', 'deck-hero')
        panel.setProperty('visualTier', 'themed')
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(6)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(10)

        headline_column = QVBoxLayout()
        headline_column.setContentsMargins(0, 0, 0, 0)
        headline_column.setSpacing(3)

        eyebrow = QLabel('Cloudflare Guardian Diagnostics workstation bridge', panel)
        eyebrow.setObjectName('cloudflare_guardianDeckHeroEyebrow')
        headline_column.addWidget(eyebrow)

        self._hero_title_label = QLabel('Cloudflare Guardian Diagnostics shell ready', panel)
        self._hero_title_label.setObjectName('cloudflare_guardianDeckHeroTitle')
        self._hero_title_label.setWordWrap(True)
        headline_column.addWidget(self._hero_title_label)

        self._hero_subtitle_label = QLabel('', panel)
        self._hero_subtitle_label.setObjectName('cloudflare_guardianDeckHeroSubtitle')
        self._hero_subtitle_label.setWordWrap(True)
        headline_column.addWidget(self._hero_subtitle_label)

        self._hero_summary_label = QLabel('', panel)
        self._hero_summary_label.setObjectName('cloudflare_guardianDeckHeroSummary')
        self._hero_summary_label.setWordWrap(True)
        headline_column.addWidget(self._hero_summary_label)

        top_row.addLayout(headline_column, 1)

        badge_column = QVBoxLayout()
        badge_column.setContentsMargins(0, 0, 0, 0)
        badge_column.setSpacing(4)
        self._hero_runtime_pill = _TonePill(parent=panel)
        self._hero_repo_pill = _TonePill(parent=panel)
        self._hero_graph_pill = _TonePill(parent=panel)
        badge_column.addWidget(self._hero_runtime_pill, 0, Qt.AlignRight)
        badge_column.addWidget(self._hero_repo_pill, 0, Qt.AlignRight)
        badge_column.addWidget(self._hero_graph_pill, 0, Qt.AlignRight)
        top_row.addLayout(badge_column)

        layout.addLayout(top_row)

        bridge_strip = QFrame(panel)
        bridge_strip.setObjectName('cloudflare_guardianDeckBridgeStrip')
        bridge_strip.setFrameShape(QFrame.NoFrame)
        strip_layout = QHBoxLayout(bridge_strip)
        strip_layout.setContentsMargins(0, 0, 0, 0)
        strip_layout.setSpacing(8)
        self._hero_focus_label = QLabel('', bridge_strip)
        self._hero_focus_label.setObjectName('cloudflare_guardianDeckHeroFocus')
        self._hero_focus_label.setWordWrap(True)
        strip_layout.addWidget(self._hero_focus_label, 1)
        self._bridge_tabs_summary = QLabel('Briefing / Workbench / Topology', bridge_strip)
        self._bridge_tabs_summary.setObjectName('cloudflare_guardianDeckBridgeTabsSummary')
        self._bridge_tabs_summary.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        strip_layout.addWidget(self._bridge_tabs_summary, 0)
        layout.addWidget(bridge_strip)

        self._bridge_ambient = _BridgeAmbientRibbon(panel)
        layout.addWidget(self._bridge_ambient)
        return panel

    def _make_metric_strip(self) -> QWidget:
        strip = QFrame(self)
        strip.setObjectName('cloudflare_guardianDeckMetricStrip')
        strip.setFrameShape(QFrame.NoFrame)
        strip.setProperty('visualRole', 'deck-row')
        strip.setProperty('visualTier', 'themed')
        layout = QGridLayout(strip)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        positions = (
            ('repo', 'Repository', 0, 0),
            ('search', 'Search', 0, 1),
            ('preview', 'Preview', 1, 0),
            ('graph', 'Graph', 1, 1),
        )
        for key, title, row, col in positions:
            card = _MetricCard(title, strip)
            card.setMinimumHeight(102)
            self._metric_cards[key] = card
            layout.addWidget(card, row, col)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)
        for row in (0, 1):
            layout.setRowStretch(row, 1)
        return strip

    def _create_section(
        self,
        *,
        section_id: str,
        title: str,
        subtitle: str,
        content_widget: QWidget | None,
        missing_note: str,
    ) -> _SectionBinding:
        fallback = None
        has_real_content = content_widget is not None
        if content_widget is None:
            fallback = _FallbackSlate(self)
            fallback.set_copy(
                f'{title} is waiting for its sibling lane.',
                missing_note,
                'The shell keeps this slot deliberate so the merged plugin feels intentional instead of empty.',
                tone='warning',
            )
            body_widget = fallback
        else:
            body_widget = content_widget

        if self._surface_cls is not None:
            surface = self._instantiate_optional(self._surface_cls)
            if surface is not None:
                attached = False
                if hasattr(surface, 'setObjectName'):
                    surface.setObjectName(self._section_object_name(section_id))
                self._maybe_call(surface, 'set_title', title)
                self._maybe_call(surface, 'set_subtitle', subtitle)
                self._maybe_call(surface, 'set_status_text', 'Ready' if has_real_content else 'Waiting for sibling lane')
                self._maybe_call(surface, 'set_status_tone', 'success' if has_real_content else 'warning')
                self._maybe_call(surface, 'set_theme_tokens', dict(self._theme_tokens))
                attached = self._maybe_call(surface, 'set_content_widget', body_widget)
                if attached:
                    try:
                        surface.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                    except Exception:
                        pass
                    minimum_height = _SECTION_MIN_HEIGHTS.get(section_id)
                    if minimum_height:
                        try:
                            surface.setMinimumHeight(int(minimum_height))
                        except Exception:
                            pass
                    binding = _SectionBinding(
                        root=surface,
                        surface=surface,
                        fallback=fallback,
                        has_real_content=has_real_content,
                    )
                    self._section_bindings[section_id] = binding
                    return binding

        panel = QFrame(self)
        panel.setObjectName(self._section_object_name(section_id))
        panel.setFrameShape(QFrame.NoFrame)
        panel.setProperty('visualRole', 'deck-section')
        panel.setProperty('visualTier', 'themed')
        panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        minimum_height = _SECTION_MIN_HEIGHTS.get(section_id)
        if minimum_height:
            panel.setMinimumHeight(int(minimum_height))

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(7)

        title_label = QLabel(title, panel)
        title_label.setObjectName(f'{panel.objectName()}Title')
        title_label.setProperty('slot', 'title')
        layout.addWidget(title_label)

        subtitle_label = QLabel(subtitle, panel)
        subtitle_label.setObjectName(f'{panel.objectName()}Subtitle')
        subtitle_label.setProperty('slot', 'subtitle')
        subtitle_label.setWordWrap(True)
        layout.addWidget(subtitle_label)

        status_label = QLabel('', panel)
        status_label.setObjectName(f'{panel.objectName()}Status')
        status_label.setProperty('slot', 'status')
        status_label.setProperty('tone', 'muted')
        layout.addWidget(status_label)

        layout.addWidget(body_widget, 1)
        binding = _SectionBinding(
            root=panel,
            title_label=title_label,
            subtitle_label=subtitle_label,
            status_label=status_label,
            fallback=fallback,
            has_real_content=has_real_content,
        )
        binding.set_status('Ready' if has_real_content else 'Waiting for sibling lane', 'success' if has_real_content else 'warning')
        self._section_bindings[section_id] = binding
        return binding

    def _wire_widget_contracts(self) -> None:
        self._push_dispatcher_to_controls()
        self._push_theme_to_visuals()
        self._push_snapshot(self._snapshot)

    def _push_dispatcher_to_controls(self) -> None:
        for widget in (self._command_bar, self._action_rail):
            if widget is None:
                continue
            setter = getattr(widget, 'set_dispatcher', None)
            if callable(setter):
                try:
                    setter(self._dispatcher)
                except Exception:
                    pass

    def _apply_theme_to_widget(self, widget: QWidget | None) -> None:
        if widget is None:
            return
        if self._maybe_call(widget, 'set_skin', self._theme_tokens):
            return
        self._maybe_call(widget, 'set_theme_tokens', self._theme_tokens)

    def _push_theme_to_visuals(self) -> None:
        for widget in (
            self._command_bar,
            self._action_rail,
            self._context_spine,
            self._repo_pulse,
            self._graph_radar,
        ):
            self._apply_theme_to_widget(widget)
        for binding in self._section_bindings.values():
            if binding.surface is not None and isinstance(binding.surface, QWidget):
                self._apply_theme_to_widget(binding.surface)
        if self._graph_radar is not None:
            self._maybe_call(
                self._graph_radar,
                'set_animation_enabled',
                bool(self.isVisible() and self._active_tab_id == 'topology'),
            )
        if self._bridge_ambient is not None:
            self._bridge_ambient.set_tokens(self._theme_tokens)

    def _attach_optional_state_adapter(self) -> None:
        if self._state_adapter is not None or self._state_adapter_cls is None:
            return

        adapter = self._instantiate_optional(self._state_adapter_cls)
        if adapter is None:
            return

        attach_context = getattr(adapter, 'attach_context', None)
        if callable(attach_context):
            try:
                attach_context(
                    main_window=self._main_window,
                    container=self._container,
                    event_bus=self._event_bus,
                )
            except Exception:
                return
        self._state_adapter = adapter
        self._host_runtime.set_state_adapter(adapter)

    def _build_current_snapshot(self) -> dict[str, Any]:
        return self._host_runtime.build_current_snapshot(
            normalize_snapshot=self._normalize_snapshot_with_payload_fn,
        )

    def _push_snapshot(self, snapshot: Any) -> None:
        normalized = self._normalize_snapshot(snapshot)
        changed = self._runtime.push_snapshot(normalized)
        self._snapshot = dict(self._runtime.snapshot)
        if changed:
            self._refresh_shell_chrome()
            self._runtime.mark_all_tabs_dirty()
        elif not self._tab_dirty:
            self._update_tab_activity(runtime_visible=self.isVisible())
            return
        self._apply_tab_refresh(self._active_tab_id)
        self._update_tab_activity(runtime_visible=self.isVisible())

    def _push_snapshot_to_consumer(self, consumer: QWidget | None, snapshot: dict[str, Any]) -> None:
        if consumer is None:
            return
        if self._maybe_call(consumer, 'set_snapshot', dict(snapshot)):
            return
        if self._maybe_call(consumer, 'refresh_now', dict(snapshot)):
            self._note_compatibility(f'{type(consumer).__name__}: refresh_now(snapshot) compatibility fallback used because set_snapshot was unavailable.')

    def _push_snapshot_to_radar(self, radar: QWidget | None, snapshot: dict[str, Any]) -> None:
        if radar is None:
            return
        if self._maybe_call(radar, 'set_snapshot', dict(snapshot)):
            return
        if self._maybe_call(
            radar,
            'set_graph_data',
            list(snapshot['nodes']),
            list(snapshot['edges']),
            snapshot['focus_node_id'],
        ):
            self._maybe_call(radar, 'set_focus_node', snapshot['focus_node_id'])
            self._note_compatibility('CloudflareGuardianGraphRadar: set_graph_data(nodes, edges, focus_node_id) compatibility fallback used because set_snapshot was unavailable.')
            return
        if self._maybe_call(radar, 'refresh_now', dict(snapshot)):
            self._note_compatibility('CloudflareGuardianGraphRadar: refresh_now(snapshot) compatibility fallback used because canonical routes were unavailable.')

    def _build_command_specs(self, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        return self._host_runtime.build_command_specs(snapshot)

    def _build_action_specs(self, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
        return self._host_runtime.build_action_specs(snapshot)

    def _command_spec(
        self,
        name: str,
        title: str,
        description: str,
        *,
        shortcut: str,
        keywords: list[str],
        enabled: bool,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return _build_command_spec(
            name,
            title,
            description,
            shortcut=shortcut,
            keywords=keywords,
            enabled=enabled,
            payload=payload,
        )

    def _action_spec(
        self,
        action_id: str,
        title: str,
        description: str,
        *,
        keywords: list[str],
        enabled: bool,
        payload: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        return _build_action_spec(
            action_id,
            title,
            description,
            keywords=keywords,
            enabled=enabled,
            payload=payload,
        )

    def _normalize_snapshot(self, snapshot: Any) -> dict[str, Any]:
        return self._normalize_snapshot_with_payload_fn(snapshot, self._snapshot_payload_fn)

    @staticmethod
    def _normalize_snapshot_with_payload_fn(
        snapshot: Any,
        snapshot_payload_fn: Callable[[Any], Any] | None,
    ) -> dict[str, Any]:
        return _normalize_snapshot_payload(
            snapshot,
            snapshot_payload_fn=snapshot_payload_fn,
        )

    def _refresh_shell_chrome(self) -> None:
        snapshot = self._snapshot
        available_slices = self._available_slice_names()
        missing_slices = self._missing_slice_names()

        status_text = snapshot['status_text'] or 'Cloudflare Guardian Diagnostics bridge online'
        subtitle = snapshot['subtitle'] or self._default_subtitle(snapshot)
        summary = self._hero_detail(snapshot, available_slices)
        focus = self._hero_focus(snapshot)
        if self._hero_title_label is not None:
            self._hero_title_label.setText(status_text)
        if self._hero_subtitle_label is not None:
            self._hero_subtitle_label.setText(subtitle)
        if self._hero_summary_label is not None:
            self._hero_summary_label.setText(summary)
        if self._hero_focus_label is not None:
            self._hero_focus_label.setText(focus)

        if self._hero_runtime_pill is not None:
            runtime_tone = 'success' if self._state_adapter is not None else 'warning'
            runtime_text = 'state adapter attached' if self._state_adapter is not None else 'state adapter missing'
            self._hero_runtime_pill.set_pill(runtime_text, runtime_tone)
        if self._hero_repo_pill is not None:
            repo_text = 'repo ready' if snapshot['repo_ready'] else 'repo not ready'
            repo_tone = 'success' if snapshot['repo_ready'] else 'warning'
            self._hero_repo_pill.set_pill(repo_text, repo_tone)
        if self._hero_graph_pill is not None:
            nodes_count = len(snapshot['nodes'])
            graph_tone = 'accent' if nodes_count else 'muted'
            graph_text = f'graph {nodes_count} nodes' if nodes_count else 'graph empty-valid'
            self._hero_graph_pill.set_pill(graph_text, graph_tone)
        if self._bridge_tabs_summary is not None:
            active = self._active_tab_id.capitalize()
            self._bridge_tabs_summary.setText(f'Active tab: {active}')
        if self._workbench_strip_label is not None:
            self._workbench_strip_label.setText(
                f"query '{snapshot['query_text'] or 'idle'}' • preview '{snapshot['current_preview_relpath'] or 'none'}' • "
                f"results {snapshot['results_count']} • bookmarks {snapshot['bookmarks_count']}"
            )
        if self._topology_summary_label is not None:
            self._topology_summary_label.setText(
                f"nodes={len(snapshot['nodes'])} • edges={len(snapshot['edges'])} • hotspots={len(snapshot['hotspots'])} • "
                f"focus={snapshot['focus_node_id'] or 'none'}"
            )

        self._refresh_metric_cards(snapshot)

        if self._availability_label is not None:
            self._availability_label.setText(
                'Available slices: '
                + (', '.join(available_slices) if available_slices else 'none')
                + ' | Missing in this lane package: '
                + (', '.join(missing_slices) if missing_slices else 'none')
            )
        if self._compatibility_label is not None:
            self._compatibility_label.setText(
                'Compatibility posture: '
                + ( ' ; '.join(self._compatibility_notes) if self._compatibility_notes else 'canonical routes only in this runtime pass.' )
            )

    def _refresh_metric_cards(self, snapshot: dict[str, Any]) -> None:
        next_signature: dict[str, tuple[object, ...]] = {}
        repo_label = snapshot['repo_name'] or 'No repo bound yet'
        repo_detail = snapshot['startup_status'] or 'startup idle'
        repo_tone = 'success' if snapshot['repo_ready'] else 'warning'
        next_signature['repo'] = (
            snapshot['index_file_count'],
            repo_label,
            snapshot['index_ext_count'],
            snapshot['index_elapsed_sec'],
            repo_detail,
            repo_tone,
        )
        self._metric_cards['repo'].set_card(
            snapshot['index_file_count'],
            repo_label,
            f"ext {snapshot['index_ext_count']} • elapsed {self._format_elapsed(snapshot['index_elapsed_sec'])} • {repo_detail}",
            tone=repo_tone,
        )

        search_caption = snapshot['query_text'] or 'No active query'
        search_detail = f"scope {snapshot['active_scope'] or 'all'} • ext {snapshot['active_extension'] or 'any'}"
        search_tone = 'accent' if snapshot['results_count'] else 'muted'
        next_signature['search'] = (
            snapshot['results_count'],
            search_caption,
            search_detail,
            search_tone,
        )
        self._metric_cards['search'].set_card(snapshot['results_count'], search_caption, search_detail, tone=search_tone)

        preview_caption = snapshot['current_preview_relpath'] or 'No preview target'
        preview_detail = snapshot['current_preview_kind'] or 'waiting for preview'
        preview_tone = 'success' if snapshot['current_preview_relpath'] else 'muted'
        next_signature['preview'] = (
            snapshot['bookmarks_count'],
            preview_caption,
            preview_detail,
            preview_tone,
        )
        self._metric_cards['preview'].set_card(snapshot['bookmarks_count'], preview_caption, preview_detail, tone=preview_tone)

        graph_caption = f"edges {len(snapshot['edges'])} | hotspots {len(snapshot['hotspots'])}"
        graph_detail = snapshot['focus_node_id'] or 'No focus node. Graph fields remain empty-valid.'
        graph_tone = 'accent' if snapshot['nodes'] else 'muted'
        next_signature['graph'] = (
            len(snapshot['nodes']),
            graph_caption,
            graph_detail,
            graph_tone,
        )
        self._metric_cards['graph'].set_card(len(snapshot['nodes']), graph_caption, graph_detail, tone=graph_tone)
        changed = [key for key, value in next_signature.items() if self._metric_signature.get(key) != value]
        self._metric_signature = next_signature
        if changed:
            self._animate_refresh(changed)

    def _refresh_briefing(self, snapshot: dict[str, Any]) -> None:
        for consumer in (self._context_spine, self._repo_pulse):
            self._push_snapshot_to_consumer(consumer, snapshot)

        context_binding = self._section_bindings.get('context_spine')
        pulse_binding = self._section_bindings.get('repo_pulse')
        if context_binding is not None:
            snapshot_summary = f"repo {snapshot['repo_name'] or 'unknown'} | results {snapshot['results_count']} | warnings {snapshot['warning_count']}"
            context_binding.set_status(
                'snapshot pushed via set_snapshot' if context_binding.has_real_content else 'snapshot consumer pending',
                'success' if context_binding.has_real_content else 'warning',
            )
            if context_binding.fallback is not None:
                context_binding.fallback.set_copy(
                    'Context lane absent, canonical snapshot still normalized.',
                    snapshot_summary,
                    'No alias keys leak downstream. Extra mapping keys are dropped during shell normalization.',
                    tone='accent' if snapshot['repo_ready'] else 'warning',
                )
        if pulse_binding is not None:
            pulse_binding.set_status(
                'repo pulse ready' if pulse_binding.has_real_content else 'repo pulse pending',
                'success' if pulse_binding.has_real_content else 'warning',
            )
            if pulse_binding.fallback is not None:
                pulse_binding.fallback.set_copy(
                    'Repo pulse lane absent, local shell still exposes meaningful state.',
                    f"startup {snapshot['startup_status'] or 'idle'} | bookmarks {snapshot['bookmarks_count']} | plugin_count {snapshot['plugin_count']}",
                    'This is informational chrome only. The shell does not replace the sibling widget.',
                    tone='accent' if snapshot['bookmarks_count'] else 'muted',
                )

    def _refresh_workbench(self, snapshot: dict[str, Any]) -> None:
        self._ensure_workbench_controls()
        command_specs = self._build_command_specs(snapshot)
        if self._command_bar is not None:
            self._maybe_call(self._command_bar, 'set_command_specs', command_specs)
            self._maybe_call(self._command_bar, 'update_context', dict(snapshot))

        action_specs = self._build_action_specs(snapshot)
        if self._action_rail is not None:
            self._maybe_call(self._action_rail, 'set_actions', action_specs)
            self._maybe_call(self._action_rail, 'update_context', dict(snapshot))
            self._maybe_call(self._action_rail, 'set_busy', False)

        command_binding = self._section_bindings.get('command_bar')
        action_binding = self._section_bindings.get('action_rail')
        if command_binding is not None:
            ready_commands = sum(1 for spec in command_specs if spec['enabled'])
            command_binding.set_status(f'{ready_commands} command(s) ready', 'success' if ready_commands else 'warning')
            command_binding.set_subtitle('Operational command lane. Hidden while Briefing/Topology are active.')
            if command_binding.fallback is not None:
                command_binding.fallback.set_copy(
                    'Command lane absent, command contract preserved.',
                    f'The shell still emits {len(command_specs)} canonical command specs with first-seen-wins naming and no host-side discovery.',
                    'When command_bar.py lands, set_command_specs(...) and update_context(...) become hot immediately.',
                    tone='warning',
                )

        if action_binding is not None:
            ready_actions = sum(1 for spec in action_specs if spec['enabled'])
            action_binding.set_status(f'{ready_actions} action(s) ready', 'success' if ready_actions else 'warning')
            action_binding.set_subtitle('High-frequency action lane, activated only while Workbench is foreground.')
            if action_binding.fallback is not None:
                action_binding.fallback.set_copy(
                    'Action lane absent, interaction intent remains deterministic.',
                    'The shell keeps high-frequency actions visible through canonical action specs only, never by probing menus, toolbars, or controllers.',
                    'This preserves merge realism while still making the slot feel intentional.',
                    tone='warning',
                )

    def _refresh_topology(self, snapshot: dict[str, Any]) -> None:
        self._ensure_topology_radar()
        self._push_snapshot_to_radar(self._graph_radar, snapshot)
        radar_binding = self._section_bindings.get('graph_radar')
        if radar_binding is None:
            return
        nodes_count = len(snapshot['nodes'])
        edges_count = len(snapshot['edges'])
        if self._graph_radar is None:
            radar_binding.set_status('topology radar unavailable', 'warning')
            radar_binding.set_subtitle('Graph radar class is unavailable in this runtime.')
            if self._topology_placeholder is not None:
                self._topology_placeholder.setVisible(True)
            return
        graph_status = f'{nodes_count} node(s) | {edges_count} edge(s) | focus {snapshot["focus_node_id"] or "none"}'
        radar_binding.set_status(graph_status if nodes_count else 'empty-valid graph payload', 'accent' if nodes_count else 'muted')
        radar_binding.set_subtitle('Topology lane. Graph activation is deferred while this tab is hidden.')
        if radar_binding.fallback is not None:
            radar_binding.fallback.set_copy(
                'Graph lane absent, graph semantics remain honest.',
                'The shell forwards canonical graph keys only and keeps nodes, edges, hotspots, and focus_node_id empty-valid when the baseline offers no graph producer.',
                'No shell-local aliases, synthetic hotspots, or fake topology are introduced.',
                tone='muted' if not nodes_count else 'accent',
            )

    def _animate_refresh(self, metric_keys: list[str] | None = None) -> None:
        if self._animator is None or not self.isVisible():
            return
        keys = metric_keys or ['repo', 'search', 'preview', 'graph']
        for key in keys:
            card = self._metric_cards.get(key)
            if card is None:
                continue
            try:
                self._animator.fade_widget(card, key=f'metric:{key}', start=0.86, end=1.0, duration_ms=150)
            except Exception:
                return

    def _resolve_snapshot_payload_fn(self) -> Callable[[Any], Any] | None:
        module_name, _ = _WIDGET_MODULES['state_adapter']
        try:
            module = import_module(f'{__package__}.{module_name}')
        except Exception:
            return None
        candidate = getattr(module, 'snapshot_payload', None)
        if callable(candidate):
            return candidate
        return None

    def _resolve_theme_tokens(self, tokens: Any | None = None) -> dict[str, str]:
        theme_tokens = dict(_THEME_DEFAULTS)
        source = tokens
        if source is None and self._main_window is not None:
            source = getattr(self._main_window, '_skin_tokens', None)

        if self._theme_bridge_cls is not None:
            bridge = None
            coerce = getattr(self._theme_bridge_cls, 'coerce', None)
            if callable(coerce):
                try:
                    bridge = coerce(source)
                except Exception:
                    bridge = None
            if bridge is None:
                try:
                    bridge = self._theme_bridge_cls(source)
                except Exception:
                    bridge = None
            if bridge is not None:
                tokens_method = getattr(bridge, 'tokens', None)
                if callable(tokens_method):
                    try:
                        resolved = tokens_method()
                    except Exception:
                        resolved = None
                    if isinstance(resolved, Mapping):
                        for key, value in resolved.items():
                            if key in theme_tokens and value:
                                theme_tokens[key] = str(value)

        if isinstance(source, Mapping):
            for key, value in source.items():
                if key in theme_tokens and value:
                    theme_tokens[key] = str(value)
        elif source is not None:
            for key in tuple(theme_tokens.keys()):
                try:
                    value = getattr(source, key)
                except Exception:
                    continue
                if value:
                    theme_tokens[key] = str(value)

        return theme_tokens

    def _dispatcher_has(self, name: str) -> bool:
        return self._host_runtime.dispatcher_has(name)

    def _available_slice_names(self) -> list[str]:
        names: list[str] = []
        for name, widget, symbol in (
            ('command_bar', self._command_bar, self._command_bar_cls),
            ('action_rail', self._action_rail, self._action_rail_cls),
            ('context_spine', self._context_spine, self._context_spine_cls),
            ('repo_pulse', self._repo_pulse, self._repo_pulse_cls),
            ('state_adapter', self._state_adapter, self._state_adapter_cls),
        ):
            if widget is not None:
                names.append(name)
            elif symbol is not None and name in {'command_bar', 'action_rail'}:
                names.append(f'{name}(lazy)')
        if self._graph_radar is not None:
            names.append('graph_radar')
        elif self._graph_radar_cls is not None:
            names.append('graph_radar(lazy)')
        return names

    def _missing_slice_names(self) -> list[str]:
        return [
            name
            for name, widget in (
                ('command_bar', self._command_bar_cls),
                ('action_rail', self._action_rail_cls),
                ('context_spine', self._context_spine),
                ('repo_pulse', self._repo_pulse),
                ('graph_radar', self._graph_radar_cls),
                ('state_adapter', self._state_adapter),
                ('deck_surface', self._surface_cls),
                ('theme_bridge', self._theme_bridge_cls),
                ('motion', self._motion_cls),
            )
            if widget is None
        ]

    def _default_subtitle(self, snapshot: dict[str, Any]) -> str:
        if self._state_adapter is None:
            return 'State adapter is absent in this lane package, so the shell is running on empty-valid canonical defaults.'
        if snapshot['repo_ready']:
            return 'Canonical snapshot is flowing through the shell and sibling slots are being driven without host-side guessing.'
        return 'Shell wiring is live, but the host snapshot still reports a sparse or not-ready repository posture.'

    def _hero_detail(self, snapshot: dict[str, Any], available_slices: list[str]) -> str:
        details = [
            f"active slices: {', '.join(available_slices) if available_slices else 'none'}",
            f"query '{snapshot['query_text'] or 'idle'}'",
            f"warnings {snapshot['warning_count']} • plugins {snapshot['plugin_count']} • bookmarks {snapshot['bookmarks_count']}",
        ]
        return ' • '.join(details)

    def _hero_focus(self, snapshot: dict[str, Any]) -> str:
        preview = snapshot['current_preview_relpath'] or 'none'
        focus = snapshot['focus_node_id'] or 'none'
        scope = snapshot['active_scope'] or 'all'
        ext = snapshot['active_extension'] or 'any'
        return f"repo '{snapshot['repo_name'] or 'detached'}' • preview '{preview}' • focus '{focus}' • scope '{scope}' • ext '{ext}'"

    def _safe_container_get(self, name: str) -> Any:
        container = self._container
        if container is None or not hasattr(container, 'get'):
            return None
        try:
            return container.get(name)
        except Exception:
            return None

    def _optional_symbol(self, module_name: str, symbol_name: str) -> Any:
        try:
            module = import_module(f'{__package__}.{module_name}')
        except Exception:
            return None
        return getattr(module, symbol_name, None)

    def _instantiate_optional(self, cls: Any) -> Any:
        if cls is None:
            return None
        for args in ((), (self,),):
            try:
                return cls(*args)
            except TypeError:
                continue
            except Exception:
                return None
        return None

    def _maybe_call(self, target: Any, method_name: str, *args: Any) -> bool:
        method = getattr(target, method_name, None)
        if not callable(method):
            return False
        try:
            method(*args)
            return True
        except Exception:
            return False

    def _note_compatibility(self, message: str) -> None:
        if message not in self._compatibility_notes:
            self._compatibility_notes.append(message)

    def _trace_runtime(self, message: str) -> None:
        note = f"runtime:{message}"
        if note not in self._compatibility_notes:
            self._compatibility_notes.append(note)

    @staticmethod
    def _repolish_widget(widget: QWidget) -> None:
        style = widget.style()
        if style is None:
            return
        try:
            style.unpolish(widget)
            style.polish(widget)
        except Exception:
            return
        widget.update()

    def _apply_local_styles(self) -> None:
        t = self._theme_tokens
        pane_bg = self._rgba(t['bg'], 188)
        tab_bg = self._rgba(t['panel'], 226)
        tab_bg_selected = self._rgba(t['panel_alt'], 238)
        scroll_track = self._rgba(t['bg'], 120)
        scroll_handle = self._rgba(t.get('scrollbar', t['accent']), 166)
        scroll_handle_hover = self._rgba(t.get('scrollbar_hover', t['accent']), 212)
        strip_bg = self._rgba(t['panel_alt'], 188)
        success_bg = self._rgba(t['success'], 28)
        success_border = self._rgba(t['success'], 56)
        warning_bg = self._rgba(t['warning'], 30)
        warning_border = self._rgba(t['warning'], 58)
        danger_bg = self._rgba(t['danger'], 30)
        danger_border = self._rgba(t['danger'], 58)
        tab_focus = self._rgba(t['focus_ring'], 230)
        self.setStyleSheet(
            """
            QWidget#cloudflare_guardianDeckShellRoot {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 %(bg)s,
                    stop: 0.45 %(bg_alt)s,
                    stop: 1 %(bg_elevated)s
                );
            }
            QTabWidget#cloudflare_guardianDeckTabs::pane {
                border: 1px solid %(border)s;
                border-radius: 14px;
                background: %(pane_bg)s;
                padding: 8px;
            }
            QTabWidget#cloudflare_guardianDeckTabs QTabBar::tab {
                background: %(tab_bg)s;
                border: 1px solid %(border)s;
                border-bottom-color: %(border_soft)s;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 6px 12px;
                margin-right: 6px;
                color: %(text_muted)s;
                font-size: 11px;
                font-weight: 600;
            }
            QTabWidget#cloudflare_guardianDeckTabs QTabBar::tab:selected {
                background: %(tab_bg_selected)s;
                color: %(text)s;
                border-color: %(border_strong)s;
            }
            QTabWidget#cloudflare_guardianDeckTabs QTabBar::tab:hover:!selected {
                color: %(text)s;
                border-color: %(border_strong)s;
            }
            QTabWidget#cloudflare_guardianDeckTabs QTabBar::tab:focus {
                border-color: %(tab_focus)s;
            }
            QWidget#cloudflare_guardianDeckShellRoot[compactMode="true"] QTabWidget#cloudflare_guardianDeckTabs QTabBar::tab {
                padding: 5px 9px;
                margin-right: 4px;
                font-size: 10px;
            }
            QScrollArea#cloudflare_guardianDeckTabScroll_briefing,
            QScrollArea#cloudflare_guardianDeckTabScroll_workbench,
            QScrollArea#cloudflare_guardianDeckTabScroll_topology,
            QWidget#cloudflare_guardianDeckTabContent_briefing,
            QWidget#cloudflare_guardianDeckTabContent_workbench,
            QWidget#cloudflare_guardianDeckTabContent_topology,
            QWidget#cloudflare_guardianDeckControlsRow,
            QFrame#cloudflare_guardianDeckMetricStrip {
                background: transparent;
                border: none;
            }
            QScrollArea#cloudflare_guardianDeckTabScroll_briefing QScrollBar:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_workbench QScrollBar:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_topology QScrollBar:vertical {
                background: %(scroll_track)s;
                width: 10px;
                border-radius: 5px;
                margin: 6px 2px;
            }
            QScrollArea#cloudflare_guardianDeckTabScroll_briefing QScrollBar::handle:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_workbench QScrollBar::handle:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_topology QScrollBar::handle:vertical {
                background: %(scroll_handle)s;
                min-height: 36px;
                border-radius: 5px;
            }
            QScrollArea#cloudflare_guardianDeckTabScroll_briefing QScrollBar::handle:vertical:hover,
            QScrollArea#cloudflare_guardianDeckTabScroll_workbench QScrollBar::handle:vertical:hover,
            QScrollArea#cloudflare_guardianDeckTabScroll_topology QScrollBar::handle:vertical:hover {
                background: %(scroll_handle_hover)s;
            }
            QScrollArea#cloudflare_guardianDeckTabScroll_briefing QScrollBar::add-line:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_briefing QScrollBar::sub-line:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_briefing QScrollBar::add-page:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_briefing QScrollBar::sub-page:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_workbench QScrollBar::add-line:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_workbench QScrollBar::sub-line:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_workbench QScrollBar::add-page:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_workbench QScrollBar::sub-page:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_topology QScrollBar::add-line:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_topology QScrollBar::sub-line:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_topology QScrollBar::add-page:vertical,
            QScrollArea#cloudflare_guardianDeckTabScroll_topology QScrollBar::sub-page:vertical {
                background: transparent;
                border: none;
                height: 0px;
            }
            QFrame#cloudflare_guardianDeckHeroPanel,
            QFrame#cloudflare_guardianDeckAssemblyPanel,
            QFrame#cloudflare_guardianDeck_command_bar,
            QFrame#cloudflare_guardianDeck_action_rail,
            QFrame#cloudflare_guardianDeck_context_spine,
            QFrame#cloudflare_guardianDeck_repo_pulse,
            QFrame#cloudflare_guardianDeck_graph_radar,
            QFrame#cloudflare_guardianDeckMetricCard,
            QFrame#cloudflare_guardianDeckFallbackSlate {
                background: %(panel)s;
                border: 1px solid %(border)s;
                border-radius: 16px;
            }
            QFrame#cloudflare_guardianDeck_graph_radar,
            QFrame#cloudflare_guardianDeckTopologySummary {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 %(code_bg)s,
                    stop: 0.45 %(code_line)s,
                    stop: 1 %(panel)s
                );
                border-color: %(code_line)s;
            }
            QFrame#cloudflare_guardianDeckHeroPanel {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 %(panel_alt)s,
                    stop: 0.55 %(panel)s,
                    stop: 1 %(bg_elevated)s
                );
                border: 1px solid %(border_strong)s;
            }
            QFrame#cloudflare_guardianDeckAssemblyPanel {
                border-radius: 14px;
            }
            QFrame#cloudflare_guardianDeckMetricCard:hover,
            QFrame#cloudflare_guardianDeckFallbackSlate:hover,
            QFrame#cloudflare_guardianDeck_command_bar:hover,
            QFrame#cloudflare_guardianDeck_action_rail:hover,
            QFrame#cloudflare_guardianDeck_context_spine:hover,
            QFrame#cloudflare_guardianDeck_repo_pulse:hover,
            QFrame#cloudflare_guardianDeck_graph_radar:hover {
                background: %(panel_hover)s;
                border-color: %(border_strong)s;
            }
            QLabel#cloudflare_guardianDeckHeroEyebrow,
            QLabel#cloudflare_guardianDeckMetricEyebrow,
            QLabel#cloudflare_guardianDeckAssemblyTitle,
            QLabel#cloudflare_guardianDeckContractHintText {
                color: %(text_soft)s;
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
                text-transform: uppercase;
                background: transparent;
                border: none;
            }
            QLabel#cloudflare_guardianDeckHeroTitle {
                color: %(text)s;
                font-size: 20px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
            QWidget#cloudflare_guardianDeckShellRoot[compactMode="true"] QLabel#cloudflare_guardianDeckHeroTitle {
                font-size: 17px;
            }
            QLabel#cloudflare_guardianDeckHeroSubtitle {
                color: %(text_muted)s;
                font-size: 13px;
                background: transparent;
                border: none;
            }
            QWidget#cloudflare_guardianDeckShellRoot[compactMode="true"] QLabel#cloudflare_guardianDeckHeroSubtitle {
                font-size: 12px;
            }
            QLabel#cloudflare_guardianDeckHeroSummary,
            QLabel#cloudflare_guardianDeckHeroFocus,
            QLabel#cloudflare_guardianDeckBridgeTabsSummary,
            QLabel#cloudflare_guardianDeckAssemblyAvailability,
            QLabel#cloudflare_guardianDeckAssemblyCompatibility,
            QLabel#cloudflare_guardianDeckFallbackDetail,
            QLabel#cloudflare_guardianDeckFallbackFooter,
            QLabel#cloudflare_guardianDeckMetricDetail,
            QLabel#cloudflare_guardianDeckWorkbenchStripText,
            QLabel#cloudflare_guardianDeckTopologySummaryText,
            QLabel[slot="subtitle"],
            QLabel[slot="status"] {
                color: %(text_muted)s;
                font-size: 12px;
                background: transparent;
                border: none;
            }
            QLabel#cloudflare_guardianDeckBridgeTabsSummary {
                color: %(accent)s;
                font-weight: 600;
            }
            QFrame#cloudflare_guardianDeckWorkbenchStrip,
            QFrame#cloudflare_guardianDeckTopologySummary {
                background: %(strip_bg)s;
                border: 1px solid %(border_soft)s;
                border-radius: 12px;
            }
            QFrame#cloudflare_guardianDeckTopologyPlaceholder {
                background: %(strip_bg)s;
                border: 1px dashed %(border_soft)s;
                border-radius: 12px;
            }
            QLabel#cloudflare_guardianDeckTopologyPlaceholderTitle {
                color: %(text)s;
                font-size: 13px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
            QLabel#cloudflare_guardianDeckTopologyPlaceholderDetail {
                color: %(text_muted)s;
                font-size: 12px;
                background: transparent;
                border: none;
            }
            QFrame#cloudflare_guardianDeckWorkbenchCommandPlaceholder,
            QFrame#cloudflare_guardianDeckWorkbenchActionPlaceholder {
                background: %(strip_bg)s;
                border: 1px dashed %(border_soft)s;
                border-radius: 12px;
            }
            QLabel#cloudflare_guardianDeckColdPlaceholderTitle {
                color: %(text)s;
                font-size: 12px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
            QLabel#cloudflare_guardianDeckColdPlaceholderDetail {
                color: %(text_muted)s;
                font-size: 11px;
                background: transparent;
                border: none;
            }
            QLabel#cloudflare_guardianDeckTopologySummaryTitle {
                color: %(text)s;
                font-size: 12px;
                font-weight: 700;
                letter-spacing: 0.3px;
                text-transform: uppercase;
                background: transparent;
                border: none;
            }
            QLabel#cloudflare_guardianDeckMetricValue {
                color: %(text)s;
                font-size: 21px;
                font-weight: 700;
                background: transparent;
                border: none;
            }
            QLabel#cloudflare_guardianDeckMetricCaption,
            QLabel#cloudflare_guardianDeckFallbackHeadline,
            QLabel[slot="title"] {
                color: %(text)s;
                font-size: 13px;
                font-weight: 600;
                background: transparent;
                border: none;
            }
            QLabel#cloudflare_guardianDeckTonePill {
                border-radius: 10px;
                padding: 2px 7px;
                font-size: 10px;
                font-weight: 700;
                background: %(accent_soft)s;
                color: %(text)s;
                border: 1px solid %(border)s;
            }
            QLabel#cloudflare_guardianDeckTonePill[tone="muted"] {
                background: %(panel_active)s;
                color: %(text_muted)s;
                border-color: %(border)s;
            }
            QLabel#cloudflare_guardianDeckTonePill[tone="accent"] {
                background: %(accent_soft)s;
                color: %(accent)s;
                border-color: %(accent_glow)s;
            }
            QLabel#cloudflare_guardianDeckTonePill[tone="success"] {
                background: %(success_bg)s;
                color: %(success)s;
                border-color: %(success_border)s;
            }
            QLabel#cloudflare_guardianDeckTonePill[tone="warning"] {
                background: %(warning_bg)s;
                color: %(warning)s;
                border-color: %(warning_border)s;
            }
            QLabel#cloudflare_guardianDeckTonePill[tone="danger"] {
                background: %(danger_bg)s;
                color: %(danger)s;
                border-color: %(danger_border)s;
            }
            QFrame#cloudflare_guardianDeckContractHint {
                background: %(panel)s;
                border: 1px solid %(border_soft)s;
                border-radius: 11px;
            }
            QFrame#cloudflare_guardianDeckFallbackSlate[tone="warning"],
            QFrame#cloudflare_guardianDeckMetricCard[tone="warning"] {
                border-color: rgba(216, 178, 104, 0.28);
            }
            QFrame#cloudflare_guardianDeckFallbackSlate[tone="accent"],
            QFrame#cloudflare_guardianDeckMetricCard[tone="accent"] {
                border-color: rgba(220, 162, 105, 0.28);
            }
            QFrame#cloudflare_guardianDeckFallbackSlate[tone="success"],
            QFrame#cloudflare_guardianDeckMetricCard[tone="success"] {
                border-color: rgba(93, 196, 143, 0.28);
            }
            QLabel[tone="muted"] {
                color: %(text_muted)s;
            }
            QLabel[tone="accent"] {
                color: %(accent)s;
            }
            QLabel[tone="success"] {
                color: %(success)s;
            }
            QLabel[tone="warning"] {
                color: %(warning)s;
            }
            QLabel[tone="danger"] {
                color: %(danger)s;
            }
            """
            % {
                'bg': t['bg'],
                'bg_alt': t['bg_alt'],
                'bg_elevated': t['bg_elevated'],
                'pane_bg': pane_bg,
                'tab_bg': tab_bg,
                'tab_bg_selected': tab_bg_selected,
                'tab_focus': tab_focus,
                'scroll_track': scroll_track,
                'scroll_handle': scroll_handle,
                'scroll_handle_hover': scroll_handle_hover,
                'panel': t['panel'],
                'panel_alt': t['panel_alt'],
                'panel_hover': t['panel_hover'],
                'panel_active': t['panel_active'],
                'strip_bg': strip_bg,
                'code_bg': t['code_bg'],
                'code_line': t['code_line'],
                'text': t['text'],
                'text_muted': t['text_muted'],
                'text_soft': t['text_soft'],
                'accent': t['accent'],
                'accent_soft': t['accent_soft'],
                'accent_glow': t['accent_glow'],
                'success': t['success'],
                'success_bg': success_bg,
                'success_border': success_border,
                'warning': t['warning'],
                'warning_bg': warning_bg,
                'warning_border': warning_border,
                'danger': t['danger'],
                'danger_bg': danger_bg,
                'danger_border': danger_border,
                'border': t['border'],
                'border_soft': t['border_soft'],
                'border_strong': t['border_strong'],
            }
        )

    @staticmethod
    def _empty_snapshot() -> dict[str, Any]:
        return _snapshot_empty()

    @staticmethod
    def _coerce_mapping(value: Any) -> dict[str, Any]:
        return _snapshot_coerce_mapping(value)

    @staticmethod
    def _coerce_string(value: Any) -> str:
        return _snapshot_coerce_string(value)

    @staticmethod
    def _coerce_bool(value: Any) -> bool:
        return _snapshot_coerce_bool(value)

    @staticmethod
    def _coerce_int(value: Any) -> int:
        return _snapshot_coerce_int(value)

    @staticmethod
    def _coerce_float(value: Any) -> float:
        return _snapshot_coerce_float(value)

    @staticmethod
    def _coerce_list(value: Any) -> list[Any]:
        return _snapshot_coerce_list(value)

    @staticmethod
    def _format_elapsed(value: Any) -> str:
        return _snapshot_format_elapsed(value)

    @staticmethod
    def _section_object_name(section_id: str) -> str:
        normalized = ''.join(ch if ch.isalnum() else '_' for ch in section_id.strip().lower())
        normalized = normalized.strip('_') or 'section'
        return f'cloudflare_guardianDeck_{normalized}'

    @staticmethod
    def _rgba(color_text: object, alpha: int) -> str:
        color = QColor(str(color_text or '').strip())
        if not color.isValid():
            color = QColor(_THEME_DEFAULTS['panel'])
        alpha_value = max(0, min(255, int(alpha)))
        color.setAlpha(alpha_value)
        return f'rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()})'


