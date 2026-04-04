from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTabWidget, QWidget

from .contracts import (
    SUPPORTED_TAB_DENSITY,
    SUPPORTED_TAB_ICON_MODES,
    SUPPORTED_TAB_PLACEMENT,
    SUPPORTED_TAB_VARIANTS,
)
from .icons import get_icon
from ._template_helpers import _choice, _normalize_tab_state, _polish_widget
from ._template_specs import GlassWorkspaceTabSpec

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

__all__ = ["GlassWorkspaceTabs"]
