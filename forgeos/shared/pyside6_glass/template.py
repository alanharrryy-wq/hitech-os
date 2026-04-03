from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .chrome import WindowChromeBar
from .config import GlassTemplateConfig, resolve_template_config
from .contracts import (
    DEFAULT_THEME_ID,
    PANEL_ROLES,
    SUPPORTED_PANEL_STATES,
    SUPPORTED_TAB_DENSITY,
    SUPPORTED_TAB_ICON_MODES,
    SUPPORTED_TAB_PLACEMENT,
    SUPPORTED_TAB_STATES,
    SUPPORTED_TAB_VARIANTS,
)
from .controls import create_button
from .icons import get_icon
from .persistence import GlassWorkspaceState
from .scene import build_glass_dialog_scene
from .theme import build_stylesheet


def _normalize_tab_state(state: str) -> str:
    normalized = str(state or "").strip().lower()
    if normalized in SUPPORTED_TAB_STATES:
        return normalized
    return "visible"


def _normalize_panel_role(role: str) -> str:
    normalized = str(role or "").strip().lower()
    if normalized in PANEL_ROLES:
        return normalized
    return "workspace"


def _normalize_panel_state(state: str) -> str:
    normalized = str(state or "").strip().lower()
    if normalized in SUPPORTED_PANEL_STATES:
        return normalized
    return "visible"


def _choice(value: str, allowed: tuple[str, ...], fallback: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in allowed:
        return normalized
    return fallback


def _polish_widget(widget: QWidget) -> None:
    style = widget.style()
    if style is None:
        return
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def _layout_parent_widget(layout: QLayout | None) -> QWidget | None:
    if layout is None:
        return None
    parent = layout.parent()
    return parent if isinstance(parent, QWidget) else None


@dataclass(slots=True, frozen=True)
class GlassWorkspaceTabSpec:
    tab_id: str
    title: str
    state: str = "visible"
    tooltip: str = ""
    icon_name: str | None = None
    icon_pack: str | None = None
    icon_namespace: str | None = None
    status: str = ""
    badge: str = ""
    favorite: bool = False
    pinned: bool = False
    family: str = ""
    lazy_factory: Callable[[], QWidget] | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class GlassPanelSpec:
    panel_id: str
    title: str
    role: str = "workspace"
    subtitle: str = ""
    state: str = "visible"
    card_kind: str = "true"
    status: str = ""
    icon_name: str | None = None
    icon_pack: str | None = None
    min_size: tuple[int, int] | None = None
    preferred_size: tuple[int, int] | None = None
    max_size: tuple[int, int] | None = None
    priority: int = 100
    group: str = ""
    collapsible: bool = True
    deferred_factory: Callable[[], QWidget] | None = None
    toolbar_enabled: bool = True
    footer_enabled: bool = False
    metadata: dict[str, str] = field(default_factory=dict)


class GlassWorkspaceTabs(QTabWidget):
    """Tabs as workspace primitive with metadata, lazy loading and visibility states."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        tabs_closable: bool = False,
        movable: bool = False,
        document_mode: bool = True,
        placement: str = "top",
        density: str = "comfortable",
        variant: str = "glass",
        icon_mode: str = "icon_text",
        hide_if_single_visible: bool = False,
        overflow_scroll_buttons: bool = True,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("GlassWorkspaceTabs")
        self.setTabsClosable(tabs_closable)
        self.setMovable(movable)
        self.setDocumentMode(document_mode)
        self.setUsesScrollButtons(bool(overflow_scroll_buttons))
        self._tab_ids: list[str] = []
        self._tab_states: dict[str, str] = {}
        self._tab_specs: dict[str, GlassWorkspaceTabSpec] = {}
        self._lazy_factories: dict[str, Callable[[], QWidget]] = {}
        self._lazy_ready: dict[str, bool] = {}
        self._tab_badges: dict[str, str] = {}
        self._tab_meta: dict[str, dict[str, str]] = {}
        self._hide_if_single_visible = bool(hide_if_single_visible)
        self._tab_density = _choice(density, SUPPORTED_TAB_DENSITY, "comfortable")
        self._tab_variant = _choice(variant, SUPPORTED_TAB_VARIANTS, "glass")
        self._icon_mode = _choice(icon_mode, SUPPORTED_TAB_ICON_MODES, "icon_text")
        self._max_tab_title_chars = 26
        self.set_tab_placement(placement)
        self.setProperty("tabDensity", self._tab_density)
        self.setProperty("tabVariant", self._tab_variant)
        self.setProperty("tabIconMode", self._icon_mode)

        tab_bar = self.tabBar()
        tab_bar.setExpanding(False)
        tab_bar.setElideMode(Qt.ElideRight)
        tab_bar.setDrawBase(False)
        tab_moved = getattr(tab_bar, "tabMoved", None)
        if tab_moved is not None:
            tab_moved.connect(self._on_tab_moved)
        self.currentChanged.connect(self._on_current_changed)
        self.tabCloseRequested.connect(self._on_tab_close_requested)

    def set_tab_placement(self, placement: str) -> None:
        normalized = _choice(placement, SUPPORTED_TAB_PLACEMENT, "top")
        mapping = {
            "top": QTabWidget.North,
            "bottom": QTabWidget.South,
            "left": QTabWidget.West,
            "right": QTabWidget.East,
        }
        self.setTabPosition(mapping[normalized])
        self.setProperty("tabPlacement", normalized)
        _polish_widget(self)

    def set_tab_variant(self, variant: str) -> None:
        self._tab_variant = _choice(variant, SUPPORTED_TAB_VARIANTS, "glass")
        self.setProperty("tabVariant", self._tab_variant)
        _polish_widget(self)

    def set_tab_density(self, density: str) -> None:
        self._tab_density = _choice(density, SUPPORTED_TAB_DENSITY, "comfortable")
        self.setProperty("tabDensity", self._tab_density)
        _polish_widget(self)

    def set_tab_icon_mode(self, mode: str) -> None:
        self._icon_mode = _choice(mode, SUPPORTED_TAB_ICON_MODES, "icon_text")
        self.setProperty("tabIconMode", self._icon_mode)
        self._refresh_all_tab_labels()
        _polish_widget(self)

    def set_hide_if_single_visible(self, enabled: bool) -> None:
        self._hide_if_single_visible = bool(enabled)
        self._refresh_tab_bar_visibility()

    def add_workspace_tab(
        self,
        spec: GlassWorkspaceTabSpec,
        widget: QWidget | None,
        *,
        make_current: bool = False,
    ) -> int:
        tab_id = str(spec.tab_id or "").strip()
        if not tab_id:
            raise ValueError("tab_id is required")

        existing = self.index_of(tab_id)
        if existing >= 0:
            self.removeTab(existing)
            del self._tab_ids[existing]

        tab_widget = widget
        if tab_widget is None:
            tab_widget = QWidget(self)
            tab_widget.setObjectName(f"glass_tab_placeholder_{tab_id}")

        index = self.addTab(tab_widget, self._tab_label(spec))
        self._tab_ids.insert(index, tab_id)
        self._tab_specs[tab_id] = spec
        self._tab_badges[tab_id] = str(spec.badge or "")
        self._tab_meta[tab_id] = dict(spec.metadata or {})
        self.set_tab_state(tab_id, spec.state)

        if spec.tooltip:
            self.setTabToolTip(index, spec.tooltip)
        else:
            self.setTabToolTip(index, str(spec.title or tab_id))
        if spec.icon_name:
            icon = get_icon(spec.icon_name, namespace=spec.icon_namespace, pack=spec.icon_pack)
            if not icon.isNull() and self._icon_mode != "text_only":
                self.setTabIcon(index, icon)
        if self._icon_mode == "icon_only":
            self.setTabText(index, "")
            if not spec.tooltip:
                self.setTabToolTip(index, spec.title)

        if spec.lazy_factory is not None:
            self._lazy_factories[tab_id] = spec.lazy_factory
            self._lazy_ready[tab_id] = False

        if make_current and self._is_tab_state_selectable(self._tab_states.get(tab_id, "visible")):
            self.setCurrentIndex(index)
            self._ensure_tab_content_loaded(tab_id)
        self._refresh_tab_bar_visibility()
        return index

    def remove_workspace_tab(self, tab_id: str) -> bool:
        index = self.index_of(tab_id)
        if index < 0:
            return False
        removed_id = self._tab_ids[index]
        self.removeTab(index)
        del self._tab_ids[index]
        self._tab_states.pop(removed_id, None)
        self._tab_specs.pop(removed_id, None)
        self._lazy_factories.pop(removed_id, None)
        self._lazy_ready.pop(removed_id, None)
        self._tab_badges.pop(removed_id, None)
        self._tab_meta.pop(removed_id, None)
        self._refresh_tab_bar_visibility()
        return True

    def index_of(self, tab_id: str) -> int:
        normalized = str(tab_id or "").strip()
        if not normalized:
            return -1
        for idx, value in enumerate(self._tab_ids):
            if value == normalized:
                return idx
        return -1

    def set_tab_state(self, tab_id: str, state: str) -> None:
        index = self.index_of(tab_id)
        if index < 0:
            return
        normalized = _normalize_tab_state(state)
        self._tab_states[tab_id] = normalized
        visible = normalized != "hidden"
        enabled = normalized not in {"hidden", "disabled"}

        tab_bar = self.tabBar()
        tab_bar.setTabEnabled(index, enabled)
        self._set_tab_visible(index, visible)
        tab_bar.setTabData(index, {"state": normalized})
        self._sync_tab_label(index, tab_id)

        if not visible and self.currentIndex() == index:
            fallback = self._first_selectable_tab_index()
            if fallback >= 0:
                self.setCurrentIndex(fallback)
        self._refresh_tab_bar_visibility()

    def tab_state(self, tab_id: str) -> str:
        return self._tab_states.get(str(tab_id or "").strip(), "visible")

    def set_active_tab(self, tab_id: str) -> bool:
        index = self.index_of(tab_id)
        if index < 0:
            return False
        state = self._tab_states.get(tab_id, "visible")
        if not self._is_tab_state_selectable(state):
            return False
        self.setCurrentIndex(index)
        self._ensure_tab_content_loaded(tab_id)
        return True

    def visible_tab_ids(self) -> list[str]:
        return [tab_id for tab_id in self._tab_ids if self._tab_states.get(tab_id, "visible") != "hidden"]

    def tab_ids(self) -> tuple[str, ...]:
        return tuple(self._tab_ids)

    def snapshot_states(self) -> dict[str, str]:
        return {tab_id: self._tab_states.get(tab_id, "visible") for tab_id in self._tab_ids}

    def snapshot_order(self) -> list[str]:
        return list(self._tab_ids)

    def set_tab_badge(self, tab_id: str, badge: str | int | None) -> None:
        key = str(tab_id or "").strip()
        if not key:
            return
        self._tab_badges[key] = str(badge or "")
        index = self.index_of(key)
        if index >= 0:
            self._sync_tab_label(index, key)

    def set_tab_metadata(self, tab_id: str, metadata: dict[str, str] | None) -> None:
        key = str(tab_id or "").strip()
        if not key:
            return
        self._tab_meta[key] = dict(metadata or {})

    def next_tab(self) -> None:
        if self.count() < 2:
            return
        self.setCurrentIndex((self.currentIndex() + 1) % self.count())

    def previous_tab(self) -> None:
        if self.count() < 2:
            return
        self.setCurrentIndex((self.currentIndex() - 1) % self.count())

    def active_tab_id(self) -> str | None:
        index = self.currentIndex()
        if index < 0 or index >= len(self._tab_ids):
            return None
        return self._tab_ids[index]

    def restore_states(self, tab_states: dict[str, str], *, active_tab_id: str | None = None) -> None:
        for tab_id, state in tab_states.items():
            self.set_tab_state(tab_id, state)
        if active_tab_id:
            self.set_active_tab(active_tab_id)
        self._refresh_tab_bar_visibility()

    def restore_order(self, order: list[str] | tuple[str, ...]) -> None:
        desired = [item for item in order if item in self._tab_ids]
        if not desired:
            return
        # reorder by moving tabs to desired sequence
        for target_index, tab_id in enumerate(desired):
            current_index = self.index_of(tab_id)
            if current_index < 0 or current_index == target_index:
                continue
            self.tabBar().moveTab(current_index, target_index)
            self._on_tab_moved(current_index, target_index)

    def _first_selectable_tab_index(self) -> int:
        for idx, tab_id in enumerate(self._tab_ids):
            if self._is_tab_state_selectable(self._tab_states.get(tab_id, "visible")):
                return idx
        return -1

    def _is_tab_state_selectable(self, state: str) -> bool:
        return state in {"visible", "pending", "warning"}

    def _on_tab_moved(self, from_index: int, to_index: int) -> None:
        if not (0 <= from_index < len(self._tab_ids)):
            return
        if not (0 <= to_index < len(self._tab_ids)):
            return
        tab_id = self._tab_ids.pop(from_index)
        self._tab_ids.insert(to_index, tab_id)

    def _on_current_changed(self, index: int) -> None:
        if not (0 <= index < len(self._tab_ids)):
            return
        self._ensure_tab_content_loaded(self._tab_ids[index])

    def _on_tab_close_requested(self, index: int) -> None:
        if not (0 <= index < len(self._tab_ids)):
            return
        tab_id = self._tab_ids[index]
        spec = self._tab_specs.get(tab_id)
        if spec is not None and spec.pinned:
            return
        self.remove_workspace_tab(tab_id)

    def _ensure_tab_content_loaded(self, tab_id: str) -> None:
        if self._lazy_ready.get(tab_id):
            return
        factory = self._lazy_factories.get(tab_id)
        if factory is None:
            return
        index = self.index_of(tab_id)
        if index < 0:
            return
        widget = factory()
        if widget is None:
            return
        placeholder = self.widget(index)
        self.removeTab(index)
        self.insertTab(index, widget, self._tab_label(self._tab_specs[tab_id]))
        if self._icon_mode == "icon_only":
            self.setTabText(index, "")
        spec = self._tab_specs.get(tab_id)
        if spec and spec.icon_name and self._icon_mode != "text_only":
            icon = get_icon(spec.icon_name, namespace=spec.icon_namespace, pack=spec.icon_pack)
            if not icon.isNull():
                self.setTabIcon(index, icon)
        self._lazy_ready[tab_id] = True
        if placeholder is not None:
            placeholder.deleteLater()
        self.setCurrentIndex(index)

    def _tab_label(self, spec: GlassWorkspaceTabSpec) -> str:
        base = str(spec.title or "Tab").strip()
        if len(base) > self._max_tab_title_chars:
            base = f"{base[: self._max_tab_title_chars - 1].rstrip()}…"
        if self._icon_mode == "icon_only":
            return ""
        badge = str(self._tab_badges.get(spec.tab_id, spec.badge or "")).strip()
        if badge:
            base = f"{base} [{badge}]"
        return base

    def _sync_tab_label(self, index: int, tab_id: str) -> None:
        spec = self._tab_specs.get(tab_id)
        if spec is None:
            return
        label = self._tab_label(spec)
        if self._icon_mode == "icon_only":
            label = ""
        self.setTabText(index, label)
        state = self._tab_states.get(tab_id, "visible")
        tooltip = str(spec.tooltip or spec.title or tab_id).strip()
        if state != "visible":
            tooltip = f"{tooltip}\nstate: {state}"
        self.setTabToolTip(index, tooltip)

    def _refresh_all_tab_labels(self) -> None:
        for index, tab_id in enumerate(self._tab_ids):
            self._sync_tab_label(index, tab_id)

    def _refresh_tab_bar_visibility(self) -> None:
        if not self._hide_if_single_visible:
            self.tabBar().setVisible(True)
            return
        self.tabBar().setVisible(len(self.visible_tab_ids()) > 1)

    def _set_tab_visible(self, index: int, visible: bool) -> None:
        set_on_widget = getattr(self, "setTabVisible", None)
        if callable(set_on_widget):
            set_on_widget(index, visible)
            return
        tab_bar = self.tabBar()
        set_on_bar = getattr(tab_bar, "setTabVisible", None)
        if callable(set_on_bar):
            set_on_bar(index, visible)
            return
        if not visible:
            tab_bar.setTabEnabled(index, False)


class GlassPanelFrame(QFrame):
    """Role-aware panel container with title/subtitle + content layout."""

    def __init__(self, spec: GlassPanelSpec, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._panel_id = str(spec.panel_id)
        self._panel_state = _normalize_panel_state(spec.state)
        self._panel_role = _normalize_panel_role(spec.role)
        self._deferred_factory = spec.deferred_factory
        self._deferred_loaded = False
        self._toolbar_enabled = bool(spec.toolbar_enabled)
        self._footer_enabled = bool(spec.footer_enabled)
        self.setAccessibleName(f"glass_panel_{self._panel_id}")
        self.setProperty("card", str(spec.card_kind or "true"))
        self.setProperty("panelRole", self._panel_role)
        self.setProperty("panelState", self._panel_state)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(3)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(4)
        self._title_icon = QLabel("", self)
        self._title_icon.setFixedWidth(18)
        self._title_icon.setVisible(False)
        self._title_label = QLabel(spec.title, self)
        self._title_label.setProperty("role", "panel_title")
        self._title_label.setAccessibleName(f"glass_panel_title_{self._panel_id}")
        if spec.icon_name:
            icon = get_icon(spec.icon_name, pack=spec.icon_pack)
            if not icon.isNull():
                self._title_icon.setPixmap(icon.pixmap(16, 16))
                self._title_icon.setVisible(True)
        self._status_label = QLabel(str(spec.status or ""), self)
        self._status_label.setProperty("role", "caption")
        self._status_label.setVisible(bool(spec.status))
        header.addWidget(self._title_icon, 0, Qt.AlignTop)
        header.addWidget(self._title_label, 1)
        header.addWidget(self._status_label, 0, Qt.AlignRight)

        self._subtitle_label = QLabel(spec.subtitle, self)
        self._subtitle_label.setProperty("role", "panel_subtitle")
        self._subtitle_label.setAccessibleName(f"glass_panel_subtitle_{self._panel_id}")
        self._subtitle_label.setWordWrap(True)
        self._subtitle_label.setVisible(bool(spec.subtitle))

        self._toolbar_layout = QHBoxLayout()
        self._toolbar_layout.setContentsMargins(0, 0, 0, 0)
        self._toolbar_layout.setSpacing(4)
        self._toolbar_host = QWidget(self)
        self._toolbar_host.setLayout(self._toolbar_layout)
        self._toolbar_host.setVisible(self._toolbar_enabled)

        self._content_host = QFrame(self)
        self._content_host.setObjectName(f"glass_panel_content_{self._panel_id}")
        self._content_host.setProperty("card", "clear")
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(4)
        self._content_host.setLayout(self._content_layout)

        self._footer_layout = QHBoxLayout()
        self._footer_layout.setContentsMargins(0, 0, 0, 0)
        self._footer_layout.setSpacing(4)
        self._footer_host = QWidget(self)
        self._footer_host.setLayout(self._footer_layout)
        self._footer_host.setVisible(self._footer_enabled)

        outer.addLayout(header)
        outer.addWidget(self._subtitle_label)
        outer.addWidget(self._toolbar_host)
        outer.addWidget(self._content_host, 1)
        outer.addWidget(self._footer_host)

        if spec.min_size:
            self.setMinimumSize(max(0, int(spec.min_size[0])), max(0, int(spec.min_size[1])))
        if spec.max_size:
            self.setMaximumSize(max(0, int(spec.max_size[0])), max(0, int(spec.max_size[1])))
        if spec.preferred_size:
            self.resize(max(0, int(spec.preferred_size[0])), max(0, int(spec.preferred_size[1])))
        if self._panel_state == "deferred":
            self._render_deferred_placeholder()

    @property
    def panel_id(self) -> str:
        return self._panel_id

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    @property
    def content_host(self) -> QWidget:
        return self._content_host

    def set_panel_title(self, title: str) -> None:
        self._title_label.setText(str(title))

    def set_panel_subtitle(self, subtitle: str) -> None:
        value = str(subtitle or "")
        self._subtitle_label.setText(value)
        self._subtitle_label.setVisible(bool(value))

    def set_panel_status(self, status: str) -> None:
        value = str(status or "")
        self._status_label.setText(value)
        self._status_label.setVisible(bool(value))

    def toolbar_layout(self) -> QHBoxLayout:
        return self._toolbar_layout

    def footer_layout(self) -> QHBoxLayout:
        return self._footer_layout

    def set_toolbar_visible(self, visible: bool) -> None:
        self._toolbar_enabled = bool(visible)
        self._toolbar_host.setVisible(self._toolbar_enabled)

    def set_footer_visible(self, visible: bool) -> None:
        self._footer_enabled = bool(visible)
        self._footer_host.setVisible(self._footer_enabled)

    def set_panel_role(self, role: str) -> None:
        self._panel_role = _normalize_panel_role(role)
        self.setProperty("panelRole", self._panel_role)
        _polish_widget(self)

    def set_panel_state(self, state: str) -> None:
        self._panel_state = _normalize_panel_state(state)
        self.setProperty("panelState", self._panel_state)
        _polish_widget(self)
        self._apply_state_behavior()

    def load_deferred_content(self) -> None:
        if self._deferred_loaded:
            return
        if self._deferred_factory is None:
            return
        widget = self._deferred_factory()
        if widget is None:
            return
        self.set_content_widget(widget)
        self._deferred_loaded = True

    def _render_deferred_placeholder(self) -> None:
        self.clear_content()
        placeholder = QLabel("Deferred panel. Content will be created on demand.", self)
        placeholder.setProperty("role", "panel_subtitle")
        placeholder.setWordWrap(True)
        self.add_content_widget(placeholder)

    def _apply_state_behavior(self) -> None:
        if self._panel_state == "hidden":
            self.setVisible(False)
            return
        if self._panel_state == "collapsed":
            self.setVisible(True)
            self._toolbar_host.setVisible(False)
            self._footer_host.setVisible(False)
            self._set_content_visible(False)
            return
        if self._panel_state == "deferred":
            self.setVisible(True)
            self._render_deferred_placeholder()
            return
        if self._panel_state == "disabled":
            self.setVisible(True)
            self.setEnabled(False)
            return
        self.setEnabled(True)
        self.setVisible(True)
        self._set_content_visible(True)
        self._toolbar_host.setVisible(self._toolbar_enabled)
        self._footer_host.setVisible(self._footer_enabled)
        if self._panel_state in {"visible", "background", "hold"}:
            self.load_deferred_content()

    def _set_content_visible(self, visible: bool) -> None:
        for idx in range(self._content_layout.count()):
            item = self._content_layout.itemAt(idx)
            widget = item.widget()
            if widget is not None:
                widget.setVisible(bool(visible))

    def clear_content(self) -> None:
        self._clear_layout(self._content_layout)

    def set_content_widget(self, widget: QWidget) -> None:
        self.clear_content()
        self.add_content_widget(widget, stretch=1)

    def add_content_widget(self, widget: QWidget, stretch: int = 0) -> None:
        if widget is None:
            raise ValueError("content widget is required")
        if widget is self or widget is self._content_host:
            raise ValueError("panel cannot mount itself as content")
        if widget.isAncestorOf(self._content_host):
            raise ValueError("cannot mount ancestor widget into descendant-owned panel layout")

        old_parent = widget.parentWidget()
        old_layout = old_parent.layout() if isinstance(old_parent, QWidget) else None
        if isinstance(old_layout, QLayout):
            old_layout.removeWidget(widget)
        widget.setParent(self._content_host)
        self._content_layout.addWidget(widget, max(0, int(stretch)))

    def _clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.setParent(None)
                continue
            if child_layout is not None:
                self._clear_layout(child_layout)


@dataclass(slots=True)
class GlassLayoutController:
    splitters: dict[str, QSplitter]
    default_sizes: dict[str, list[int]]

    def register_splitter(
        self,
        key: str,
        splitter: QSplitter,
        *,
        default_sizes: list[int] | tuple[int, ...] | None = None,
    ) -> None:
        normalized = str(key or "").strip().lower()
        if not normalized:
            raise ValueError("splitter key is required")
        self.splitters[normalized] = splitter
        if default_sizes is not None:
            self.default_sizes[normalized] = [max(0, int(size)) for size in default_sizes]
            splitter.setSizes(self.default_sizes[normalized])

    def set_sizes(self, key: str, sizes: list[int] | tuple[int, ...]) -> None:
        splitter = self.splitters.get(str(key or "").strip().lower())
        if splitter is None:
            return
        splitter.setSizes([max(0, int(size)) for size in sizes])

    def set_collapsed(self, key: str, index: int, collapsed: bool) -> None:
        splitter = self.splitters.get(str(key or "").strip().lower())
        if splitter is None:
            return
        sizes = splitter.sizes()
        if not sizes or not (0 <= index < len(sizes)):
            return
        if collapsed:
            sizes[index] = 0
            splitter.setSizes(sizes)
            return

        defaults = self.default_sizes.get(str(key or "").strip().lower(), [])
        if defaults and index < len(defaults):
            sizes[index] = max(0, defaults[index])
        else:
            sizes[index] = max(1, splitter.size().width() // max(1, len(sizes)))
        splitter.setSizes(sizes)

    def snapshot(self) -> dict[str, list[int]]:
        return {key: splitter.sizes() for key, splitter in self.splitters.items()}

    def restore(self, payload: dict[str, list[int] | tuple[int, ...]]) -> None:
        for key, sizes in payload.items():
            self.set_sizes(key, list(sizes))

    def reset_defaults(self) -> None:
        for key, sizes in self.default_sizes.items():
            self.set_sizes(key, list(sizes))


class GlassPanelSlotHost(QFrame):
    """Dedicated child host that owns nested slot insertion layout."""

    def __init__(self, panel_id: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName(f"glass_panel_slot_host_{str(panel_id or '').strip().lower() or 'slot'}")
        self.setProperty("card", "clear")
        self._host_layout = QVBoxLayout(self)
        self._host_layout.setContentsMargins(0, 0, 0, 0)
        self._host_layout.setSpacing(6)

    @property
    def host_layout(self) -> QVBoxLayout:
        return self._host_layout


@dataclass(slots=True)
class GlassTemplateSlots:
    hero_slot: QVBoxLayout
    main_slot: QVBoxLayout
    side_slot: QVBoxLayout
    footer_slot: QHBoxLayout
    status_slot: QVBoxLayout
    workspace_tabs: GlassWorkspaceTabs | None = None


@dataclass(slots=True)
class GlassTemplateCards:
    shell: QFrame
    hero: QFrame
    main: QFrame
    side: QFrame
    footer: QFrame
    status: QFrame
    body: QWidget


@dataclass(slots=True)
class GlassTemplateActions:
    cancel_button: QPushButton | None
    submit_button: QPushButton | None


class GlassPanelTemplate(QWidget):
    """Reusable glass shell with tabs, role-aware panels, and layout control."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        *,
        config: GlassTemplateConfig | None = None,
        preset: str | None = None,
        title: str | None = None,
        subtitle: str | None = None,
        eyebrow: str | None = None,
        variant: str | None = None,
        theme_id: str | None = None,
        density: str | None = None,
        typography_scale: str | None = None,
        with_chrome: bool | None = None,
        show_side: bool | None = None,
        show_footer: bool | None = None,
        show_status: bool | None = None,
        include_default_actions: bool | None = None,
        cancel_text: str | None = None,
        submit_text: str | None = None,
        cancel_variant: str | None = None,
        submit_variant: str | None = None,
        apply_stylesheet: bool | None = None,
        enable_workspace_tabs: bool | None = None,
        default_tab_id: str | None = None,
        default_tab_title: str | None = None,
    ) -> None:
        super().__init__(parent)
        resolved = resolve_template_config(config, preset=preset)

        self._title = str(title if title is not None else resolved.title)
        self._subtitle = str(subtitle if subtitle is not None else resolved.subtitle)
        self._eyebrow = str(eyebrow if eyebrow is not None else resolved.eyebrow)
        self._variant = str(variant if variant is not None else resolved.variant)
        self._theme_id = str(theme_id if theme_id is not None else resolved.theme.theme_id or DEFAULT_THEME_ID)
        self._density = str(density if density is not None else resolved.theme.density)
        self._typography_scale = str(typography_scale if typography_scale is not None else resolved.theme.typography.scale)
        self._show_side = bool(show_side if show_side is not None else resolved.regions.show_side)
        self._show_footer = bool(show_footer if show_footer is not None else resolved.regions.show_footer)
        self._show_status = bool(show_status if show_status is not None else resolved.regions.show_status)
        self._with_chrome = bool(with_chrome if with_chrome is not None else resolved.with_chrome)
        self._include_default_actions = bool(
            include_default_actions
            if include_default_actions is not None
            else resolved.actions.include_default_actions
        )
        self._cancel_text = str(cancel_text if cancel_text is not None else resolved.actions.cancel_text)
        self._submit_text = str(submit_text if submit_text is not None else resolved.actions.submit_text)
        self._cancel_variant = str(cancel_variant if cancel_variant is not None else resolved.actions.cancel_variant)
        self._submit_variant = str(submit_variant if submit_variant is not None else resolved.actions.submit_variant)
        self._apply_stylesheet = bool(
            apply_stylesheet if apply_stylesheet is not None else resolved.apply_stylesheet
        )
        self._enable_workspace_tabs = bool(
            enable_workspace_tabs if enable_workspace_tabs is not None else resolved.tabs.enabled
        )
        self._tabs_movable = bool(resolved.tabs.movable)
        self._tabs_closable = bool(resolved.tabs.closable)
        self._tabs_document_mode = bool(resolved.tabs.document_mode)
        self._tabs_placement = str(resolved.tabs.placement)
        self._tabs_density = str(resolved.tabs.density)
        self._tabs_variant = str(resolved.tabs.variant)
        self._tabs_icon_mode = str(resolved.tabs.icon_mode)
        self._tabs_hide_single = bool(resolved.tabs.hide_if_single_visible)
        self._tabs_overflow_scroll = bool(resolved.tabs.overflow_scroll_buttons)
        self._default_tab_id = str(default_tab_id if default_tab_id is not None else resolved.tabs.default_tab_id)
        self._default_tab_title = str(
            default_tab_title if default_tab_title is not None else resolved.tabs.default_tab_title
        )
        self._default_main_side_sizes = list(resolved.regions.main_side_sizes)
        self._layout_named_presets = dict(resolved.layout.named_layouts)
        self._active_layout_name = str(resolved.layout.active_layout or "main_side")
        self._allow_layout_switch = bool(resolved.layout.allow_runtime_switch)
        self._allow_layout_save = bool(resolved.layout.allow_user_layout_save)
        self._edit_mode_enabled = bool(resolved.layout.edit_mode_enabled)
        self._primary_shortcut = str(resolved.actions.primary_shortcut or "Ctrl+Return")
        self._secondary_shortcut = str(resolved.actions.secondary_shortcut or "Esc")
        self._icon_scale = float(resolved.theme.visual_scale.icon_scale)
        self._border_strength_scale = float(resolved.theme.visual_scale.border_strength_scale)
        self._surface_opacity_scale = float(resolved.theme.visual_scale.surface_opacity_scale)

        self._title_label: QLabel | None = None
        self._subtitle_label: QLabel | None = None
        self._eyebrow_label: QLabel | None = None
        self._status_label: QLabel | None = None

        self.layout_controller = GlassLayoutController(splitters={}, default_sizes={})
        self._panels: dict[str, GlassPanelFrame] = {}
        self._slot_shell_ids: set[str] = set()
        self.workspace_tabs: GlassWorkspaceTabs | None = None

        self.slots, self.cards, self.actions = self._build()
        self._apply_theme_stylesheet()

    def _card(self, card_kind: str) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame(self)
        card.setProperty("card", card_kind)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(6, 5, 6, 5)
        card_layout.setSpacing(4)
        return card, card_layout

    def _build(self) -> tuple[GlassTemplateSlots, GlassTemplateCards, GlassTemplateActions]:
        outer, content, self._glass_backdrop = build_glass_dialog_scene(
            self,
            theme_id=self._theme_id,
            variant=self._variant,
            apply_stylesheet=False,
        )
        outer.setSpacing(0)

        scene_layout = QVBoxLayout(content)
        scene_layout.setContentsMargins(2, 2, 2, 2)
        scene_layout.setSpacing(0)

        shell = QFrame(self)
        shell.setObjectName("Shell")
        shell.setProperty("variant", self._variant)
        scene_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(4, 4, 4, 4)
        shell_layout.setSpacing(4)

        if self._with_chrome:
            host = self.window() if isinstance(self.window(), QWidget) else self
            chrome = WindowChromeBar(host, title=self._title)
            shell_layout.addWidget(chrome)

        hero_card, hero_layout = self._card("hero")
        shell_layout.addWidget(hero_card)
        self._eyebrow_label = QLabel(self._eyebrow, hero_card)
        self._eyebrow_label.setProperty("role", "eyebrow")
        self._eyebrow_label.setAccessibleName("glass_hero_eyebrow")
        self._title_label = QLabel(self._title, hero_card)
        self._title_label.setProperty("role", "title")
        self._title_label.setAccessibleName("glass_hero_title")
        self._subtitle_label = QLabel(self._subtitle, hero_card)
        self._subtitle_label.setProperty("role", "subtitle")
        self._subtitle_label.setAccessibleName("glass_hero_subtitle")
        self._subtitle_label.setWordWrap(True)
        hero_layout.addWidget(self._eyebrow_label)
        hero_layout.addWidget(self._title_label)
        hero_layout.addWidget(self._subtitle_label)

        body = QWidget(shell)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(2)

        tabs: GlassWorkspaceTabs | None = None
        body_host_layout: QVBoxLayout = body_layout
        if self._enable_workspace_tabs:
            tabs = GlassWorkspaceTabs(
                shell,
                tabs_closable=self._tabs_closable,
                movable=self._tabs_movable,
                document_mode=self._tabs_document_mode,
                placement=self._tabs_placement,
                density=self._tabs_density,
                variant=self._tabs_variant,
                icon_mode=self._tabs_icon_mode,
                hide_if_single_visible=self._tabs_hide_single,
                overflow_scroll_buttons=self._tabs_overflow_scroll,
            )
            body_layout.addWidget(tabs, 1)
            workspace_page = QWidget(tabs)
            workspace_layout = QVBoxLayout(workspace_page)
            workspace_layout.setContentsMargins(0, 0, 0, 0)
            workspace_layout.setSpacing(2)
            tabs.add_workspace_tab(
                GlassWorkspaceTabSpec(
                    tab_id=self._default_tab_id,
                    title=self._default_tab_title,
                    state="visible",
                    icon_name="layers",
                ),
                workspace_page,
                make_current=True,
            )
            body_host_layout = workspace_layout
            self.workspace_tabs = tabs

        split = QSplitter(Qt.Horizontal, body)
        split.setChildrenCollapsible(False)
        body_host_layout.addWidget(split, 1)

        main_panel = GlassPanelFrame(
            GlassPanelSpec(
                panel_id="main",
                title="Main Panel",
                role="workspace",
                subtitle="Primary work context.",
                card_kind="true",
            ),
            split,
        )
        side_panel = GlassPanelFrame(
            GlassPanelSpec(
                panel_id="side",
                title="Side Panel",
                role="detail",
                subtitle="Secondary or inspection context.",
                card_kind="muted",
            ),
            split,
        )
        split.addWidget(main_panel)
        split.addWidget(side_panel)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        main_panel.setProperty("slotShell", True)
        side_panel.setProperty("slotShell", True)
        self._slot_shell_ids = {"main", "side"}
        main_slot_host = GlassPanelSlotHost("main", main_panel)
        side_slot_host = GlassPanelSlotHost("side", side_panel)
        main_panel.set_content_widget(main_slot_host)
        side_panel.set_content_widget(side_slot_host)
        self.layout_controller.register_splitter(
            "main_side",
            split,
            default_sizes=self._default_main_side_sizes,
        )
        for layout_name, payload in self._layout_named_presets.items():
            self.layout_controller.default_sizes.setdefault(
                f"named::{layout_name}",
                [int(v) for v in payload.get("main_side", self._default_main_side_sizes)]
                if isinstance(payload, dict)
                else list(self._default_main_side_sizes),
            )
        if not self._show_side:
            self.layout_controller.set_collapsed("main_side", 1, True)

        footer = QFrame(self)
        footer.setProperty("card", "footer")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(6, 4, 6, 4)
        footer_layout.setSpacing(4)
        shell_layout.addWidget(footer)
        if not self._show_footer or not self._include_default_actions:
            footer.hide()

        status = QFrame(self)
        status.setProperty("card", "muted")
        status.setProperty("panelRole", "aux")
        status_layout = QVBoxLayout(status)
        status_layout.setContentsMargins(6, 4, 6, 4)
        status_layout.setSpacing(4)
        shell_layout.addWidget(status)
        status.hide()

        shell_layout.insertWidget(shell_layout.count() - 2, body, 1)

        self._status_label = QLabel("", status)
        self._status_label.setProperty("role", "hint")
        self._status_label.setAccessibleName("glass_status_message")
        self._status_label.setWordWrap(True)
        self._status_label.hide()
        status_layout.addWidget(self._status_label)

        cancel_button: QPushButton | None = None
        submit_button: QPushButton | None = None
        if self._show_footer:
            footer_layout.addStretch(1)
            if self._include_default_actions:
                cancel_button = create_button(
                    self._cancel_text,
                    self._cancel_variant,
                    parent=footer,
                    icon_name="x",
                    icon_size="small",
                )
                submit_button = create_button(
                    self._submit_text,
                    self._submit_variant,
                    parent=footer,
                    icon_name="check",
                    icon_size="small",
                )
                cancel_button.setShortcut(self._secondary_shortcut)
                submit_button.setShortcut(self._primary_shortcut)
                cancel_button.setAccessibleName("glass_action_cancel")
                submit_button.setAccessibleName("glass_action_submit")
                footer_layout.addWidget(cancel_button, 0, Qt.AlignRight)
                footer_layout.addWidget(submit_button, 0, Qt.AlignRight)

        self._panels["main"] = main_panel
        self._panels["side"] = side_panel

        slots = GlassTemplateSlots(
            hero_slot=hero_layout,
            main_slot=main_slot_host.host_layout,
            side_slot=side_slot_host.host_layout,
            footer_slot=footer_layout,
            status_slot=status_layout,
            workspace_tabs=tabs,
        )
        cards = GlassTemplateCards(
            shell=shell,
            hero=hero_card,
            main=main_panel,
            side=side_panel,
            footer=footer,
            status=status,
            body=body,
        )
        actions = GlassTemplateActions(
            cancel_button=cancel_button,
            submit_button=submit_button,
        )
        return slots, cards, actions

    def _apply_theme_stylesheet(self) -> None:
        if not self._apply_stylesheet:
            return
        self.setStyleSheet(
            build_stylesheet(
                self._theme_id,
                density=self._density,
                typography_scale=self._typography_scale,
                tab_density=self._tabs_density,
                tab_variant=self._tabs_variant,
                border_strength_scale=self._border_strength_scale,
                surface_opacity_scale=self._surface_opacity_scale,
            )
        )
        backdrop = getattr(self, "_glass_backdrop", None)
        if backdrop is not None and hasattr(backdrop, "apply_theme"):
            try:
                backdrop.apply_theme(self._theme_id)
            except Exception:
                pass

    def set_theme(self, theme_id: str) -> None:
        self._theme_id = str(theme_id or DEFAULT_THEME_ID)
        self._apply_theme_stylesheet()

    def set_density(self, density: str) -> None:
        self._density = str(density or "comfortable")
        self._apply_theme_stylesheet()

    def set_typography_scale(self, scale: str) -> None:
        self._typography_scale = str(scale or "md")
        self._apply_theme_stylesheet()

    def set_tab_placement(self, placement: str) -> None:
        self._tabs_placement = str(placement or "top")
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_tab_placement(self._tabs_placement)

    def set_tab_variant(self, variant: str) -> None:
        self._tabs_variant = str(variant or "glass")
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_tab_variant(self._tabs_variant)
        self._apply_theme_stylesheet()

    def set_tab_density(self, density: str) -> None:
        self._tabs_density = str(density or "comfortable")
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_tab_density(self._tabs_density)
        self._apply_theme_stylesheet()

    def set_tab_icon_mode(self, icon_mode: str) -> None:
        self._tabs_icon_mode = str(icon_mode or "icon_text")
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_tab_icon_mode(self._tabs_icon_mode)

    def set_hide_single_tab_bar(self, enabled: bool) -> None:
        self._tabs_hide_single = bool(enabled)
        if self.workspace_tabs is not None:
            self.workspace_tabs.set_hide_if_single_visible(enabled)

    def set_title(self, title: str) -> None:
        self._title = str(title)
        if self._title_label is not None:
            self._title_label.setText(self._title)

    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle = str(subtitle)
        if self._subtitle_label is not None:
            self._subtitle_label.setText(self._subtitle)

    def set_eyebrow(self, eyebrow: str) -> None:
        self._eyebrow = str(eyebrow)
        if self._eyebrow_label is not None:
            self._eyebrow_label.setText(self._eyebrow)

    def set_status_text(self, text: str | None) -> None:
        if self._status_label is None:
            return
        value = (text or "").strip()
        if value:
            self._status_label.setText(value)
            self._status_label.show()
            self.cards.status.show()
            return
        self._status_label.hide()
        self.cards.status.hide()

    def set_side_visible(self, visible: bool) -> None:
        self.cards.side.setVisible(bool(visible))
        self.layout_controller.set_collapsed("main_side", 1, not bool(visible))

    def set_footer_visible(self, visible: bool) -> None:
        self.cards.footer.setVisible(bool(visible))

    def set_status_visible(self, visible: bool) -> None:
        self.cards.status.setVisible(bool(visible))

    def set_submit_enabled(self, enabled: bool) -> None:
        if self.actions.submit_button is not None:
            self.actions.submit_button.setEnabled(bool(enabled))

    def bind_cancel(self, callback: Callable[[], None]) -> None:
        if self.actions.cancel_button is not None:
            self.actions.cancel_button.clicked.connect(callback)

    def bind_submit(self, callback: Callable[[], None]) -> None:
        if self.actions.submit_button is not None:
            self.actions.submit_button.clicked.connect(callback)

    def add_footer_action(
        self,
        text: str,
        variant: str = "secondary",
        *,
        align: str = "right",
        on_click: Callable[[], None] | None = None,
        minimum_width: int | None = None,
        icon_name: str | None = None,
    ) -> QPushButton:
        self.cards.footer.show()
        button = create_button(
            text,
            variant,
            on_click=on_click,
            parent=self.cards.footer,
            minimum_width=minimum_width,
            icon_name=icon_name,
        )
        if align.strip().lower() == "left":
            self.slots.footer_slot.insertWidget(0, button, 0, Qt.AlignLeft)
        else:
            self.slots.footer_slot.addWidget(button, 0, Qt.AlignRight)
        return button

    def add_workspace_tab(
        self,
        *,
        tab_id: str,
        title: str,
        widget: QWidget | None = None,
        state: str = "visible",
        tooltip: str = "",
        icon_name: str | None = None,
        icon_namespace: str | None = None,
        icon_pack: str | None = None,
        status: str = "",
        badge: str = "",
        favorite: bool = False,
        pinned: bool = False,
        family: str = "",
        lazy_factory: Callable[[], QWidget] | None = None,
        metadata: dict[str, str] | None = None,
        make_current: bool = False,
    ) -> int:
        if self.workspace_tabs is None:
            raise RuntimeError("workspace tabs are disabled for this template")
        return self.workspace_tabs.add_workspace_tab(
            GlassWorkspaceTabSpec(
                tab_id=tab_id,
                title=title,
                state=state,
                tooltip=tooltip,
                icon_name=icon_name,
                icon_namespace=icon_namespace,
                icon_pack=icon_pack,
                status=status,
                badge=badge,
                favorite=favorite,
                pinned=pinned,
                family=family,
                lazy_factory=lazy_factory,
                metadata=dict(metadata or {}),
            ),
            widget,
            make_current=make_current,
        )

    def remove_workspace_tab(self, tab_id: str) -> bool:
        if self.workspace_tabs is None:
            return False
        return self.workspace_tabs.remove_workspace_tab(tab_id)

    def set_workspace_tab_state(self, tab_id: str, state: str) -> None:
        if self.workspace_tabs is None:
            return
        self.workspace_tabs.set_tab_state(tab_id, state)

    def set_active_workspace_tab(self, tab_id: str) -> bool:
        if self.workspace_tabs is None:
            return False
        return self.workspace_tabs.set_active_tab(tab_id)

    def create_panel(
        self,
        *,
        panel_id: str,
        title: str,
        target_slot: str = "main",
        role: str = "workspace",
        subtitle: str = "",
        state: str = "visible",
        card_kind: str = "muted",
        status: str = "",
        icon_name: str | None = None,
        icon_pack: str | None = None,
        min_size: tuple[int, int] | None = None,
        preferred_size: tuple[int, int] | None = None,
        max_size: tuple[int, int] | None = None,
        priority: int = 100,
        group: str = "",
        collapsible: bool = True,
        deferred_factory: Callable[[], QWidget] | None = None,
        toolbar_enabled: bool = True,
        footer_enabled: bool = False,
        metadata: dict[str, str] | None = None,
    ) -> GlassPanelFrame:
        normalized_slot = str(target_slot or "").strip().lower()
        if normalized_slot not in {"main", "side", "status"}:
            raise ValueError("target_slot must be main, side, or status")
        container_layout = {
            "main": self.slots.main_slot,
            "side": self.slots.side_slot,
            "status": self.slots.status_slot,
        }[normalized_slot]
        container_parent = _layout_parent_widget(container_layout) or self
        panel = GlassPanelFrame(
            GlassPanelSpec(
                panel_id=panel_id,
                title=title,
                role=role,
                subtitle=subtitle,
                state=state,
                card_kind=card_kind,
                status=status,
                icon_name=icon_name,
                icon_pack=icon_pack,
                min_size=min_size,
                preferred_size=preferred_size,
                max_size=max_size,
                priority=priority,
                group=group,
                collapsible=collapsible,
                deferred_factory=deferred_factory,
                toolbar_enabled=toolbar_enabled,
                footer_enabled=footer_enabled,
                metadata=dict(metadata or {}),
            ),
            container_parent,
        )
        container_layout.addWidget(panel)
        self._panels[panel_id] = panel
        return panel

    def panel_ids(self) -> tuple[str, ...]:
        return tuple(self._panels.keys())

    def panel(self, panel_id: str) -> GlassPanelFrame | None:
        return self._panels.get(str(panel_id or "").strip())

    def panel_is_slot_shell(self, panel_id: str) -> bool:
        normalized = str(panel_id or "").strip()
        if not normalized:
            return False
        panel = self.panel(normalized)
        return bool(panel is not None and panel.property("slotShell"))

    def set_panel_state(self, panel_id: str, state: str) -> None:
        panel = self.panel(panel_id)
        if panel is not None:
            panel.set_panel_state(state)

    def set_panel_role(self, panel_id: str, role: str) -> None:
        panel = self.panel(panel_id)
        if panel is not None:
            panel.set_panel_role(role)

    def set_panel_visible(self, panel_id: str, visible: bool) -> None:
        panel = self.panel(panel_id)
        if panel is not None:
            panel.setVisible(bool(visible))

    def move_panel(self, panel_id: str, *, target_slot: str, index: int | None = None) -> bool:
        panel = self.panel(panel_id)
        if panel is None:
            return False
        if self.panel_is_slot_shell(panel_id):
            return False
        slot = str(target_slot or "").strip().lower()
        slot_map = {
            "main": self.slots.main_slot,
            "side": self.slots.side_slot,
            "status": self.slots.status_slot,
        }
        destination = slot_map.get(slot)
        if destination is None:
            return False
        destination_parent = _layout_parent_widget(destination)
        if destination_parent is not None and (panel is destination_parent or panel.isAncestorOf(destination_parent)):
            return False

        current_parent = panel.parentWidget()
        if current_parent is destination_parent and destination.indexOf(panel) >= 0:
            if index is None:
                return True
            target_index = max(0, min(int(index), max(0, destination.count() - 1)))
            current_index = destination.indexOf(panel)
            if current_index == target_index:
                return True
            destination.removeWidget(panel)
            destination.insertWidget(target_index, panel)
            return True

        parent_widget = panel.parentWidget()
        parent_layout = parent_widget.layout() if isinstance(parent_widget, QWidget) else None
        if isinstance(parent_layout, QLayout):
            parent_layout.removeWidget(panel)
        panel.setParent(None)

        if index is None:
            destination.addWidget(panel)
        else:
            destination.insertWidget(max(0, min(int(index), destination.count())), panel)
        return True

    def set_split_proportions(self, *, main: int, side: int) -> None:
        self.layout_controller.set_sizes("main_side", [max(0, int(main)), max(0, int(side))])

    def register_layout_preset(self, name: str, payload: dict[str, list[int] | tuple[int, ...]]) -> None:
        normalized = str(name or "").strip().lower()
        if not normalized:
            raise ValueError("layout preset name is required")
        self._layout_named_presets[normalized] = dict(payload)

    def list_layout_presets(self) -> tuple[str, ...]:
        return tuple(sorted(self._layout_named_presets.keys()))

    def apply_layout_preset(self, name: str) -> bool:
        normalized = str(name or "").strip().lower()
        payload = self._layout_named_presets.get(normalized)
        if payload is None:
            return False
        self.restore_layout_state(payload)
        self._active_layout_name = normalized
        return True

    def save_layout_preset(self, name: str) -> bool:
        if not self._allow_layout_save:
            return False
        normalized = str(name or "").strip().lower()
        if not normalized:
            return False
        self._layout_named_presets[normalized] = self.snapshot_layout_state()
        return True

    def restore_default_layout(self) -> None:
        self.layout_controller.reset_defaults()

    def collapse_side_panel(self, collapsed: bool) -> None:
        self.layout_controller.set_collapsed("main_side", 1, bool(collapsed))

    def snapshot_layout_state(self) -> dict[str, list[int]]:
        return self.layout_controller.snapshot()

    def restore_layout_state(self, payload: dict[str, list[int] | tuple[int, ...]]) -> None:
        self.layout_controller.restore(payload)

    def export_workspace_state(self, *, metadata: dict | None = None) -> GlassWorkspaceState:
        tab_states: dict[str, str] = {}
        active_tab_id: str | None = None
        tab_order: list[str] = []
        if self.workspace_tabs is not None:
            tab_states = self.workspace_tabs.snapshot_states()
            active_tab_id = self.workspace_tabs.active_tab_id()
            tab_order = self.workspace_tabs.snapshot_order()

        panel_states: dict[str, str] = {}
        panel_visibility: dict[str, bool] = {}
        for panel_id, panel in self._panels.items():
            panel_states[panel_id] = str(panel.property("panelState") or "visible")
            panel_visibility[panel_id] = bool(panel.isVisible())

        return GlassWorkspaceState(
            layout=self.layout_controller.snapshot(),
            selected_layout_preset=self._active_layout_name,
            tab_states=tab_states,
            tab_order=tab_order,
            active_tab_id=active_tab_id,
            panel_states=panel_states,
            panel_visibility=panel_visibility,
            theme_id=self._theme_id,
            density=self._density,
            typography_scale=self._typography_scale,
            metadata=dict(metadata or {}),
        )

    def apply_workspace_state(self, payload: GlassWorkspaceState | dict | None) -> None:
        if payload is None:
            return
        state = payload if isinstance(payload, GlassWorkspaceState) else GlassWorkspaceState.from_payload(payload)
        if state.layout:
            self.restore_layout_state(state.layout)
        if state.selected_layout_preset:
            self._active_layout_name = state.selected_layout_preset
        if self.workspace_tabs is not None and state.tab_states:
            self.workspace_tabs.restore_states(state.tab_states, active_tab_id=state.active_tab_id)
            if state.tab_order:
                self.workspace_tabs.restore_order(state.tab_order)
        for panel_id, panel_state in state.panel_states.items():
            self.set_panel_state(panel_id, panel_state)
        for panel_id, visible in state.panel_visibility.items():
            self.set_panel_visible(panel_id, visible)
        if state.theme_id:
            self.set_theme(state.theme_id)
        if state.density:
            self.set_density(state.density)
        if state.typography_scale:
            self.set_typography_scale(state.typography_scale)

    def clear_slot(self, slot_name: str) -> None:
        normalized = slot_name.strip().lower()
        mapping: dict[str, QLayout] = {
            "hero": self.slots.hero_slot,
            "main": self.slots.main_slot,
            "side": self.slots.side_slot,
            "footer": self.slots.footer_slot,
            "status": self.slots.status_slot,
        }
        layout = mapping.get(normalized)
        if layout is None:
            raise ValueError(f"Unknown slot '{slot_name}'")
        self._clear_layout(layout)

    def _clear_layout(self, layout: QLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.setParent(None)
                continue
            if child_layout is not None:
                self._clear_layout(child_layout)
