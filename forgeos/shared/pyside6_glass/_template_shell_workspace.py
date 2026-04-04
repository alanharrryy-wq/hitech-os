from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QLayout, QWidget

from .rendering import apply_surface_role, install_surface_renderer, sync_surface_renderer
from ._template_helpers import _layout_parent_widget
from ._template_panels import GlassPanelFrame
from ._template_specs import GlassPanelSpec, GlassWorkspaceTabSpec


class _GlassPanelTemplateWorkspaceMixin:
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
        apply_surface_role(
            panel,
            role=str(panel.property("visualRole") or f"panel_{panel.property('panelRole') or 'workspace'}"),
            variant="panel",
            emphasis="normal",
            fx_level=str(panel.property("visualFxLevel") or "normal"),
        )
        install_surface_renderer(panel)
        if self._appearance_snapshot is not None:
            sync_surface_renderer(panel, self._appearance_snapshot)
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

__all__ = ["_GlassPanelTemplateWorkspaceMixin"]
