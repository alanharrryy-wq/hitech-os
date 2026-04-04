from __future__ import annotations

from PySide6.QtWidgets import QLayout

from .persistence import GlassWorkspaceState


class _GlassPanelTemplateStateMixin:
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

__all__ = ["_GlassPanelTemplateStateMixin"]
