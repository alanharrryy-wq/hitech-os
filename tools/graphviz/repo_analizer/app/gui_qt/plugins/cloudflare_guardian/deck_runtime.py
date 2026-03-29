from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(slots=True)
class DeckRuntimeState:
    active_tab_id: str = "briefing"
    tab_dirty: set[str] = field(default_factory=lambda: {"briefing", "workbench", "topology"})
    runtime_visible: bool = True
    snapshot: dict[str, Any] = field(default_factory=dict)


class DeckRuntimeCoordinator:
    """Non-visual session/tab runtime for CloudflareGuardian deck host mechanics."""

    TAB_FROM_INDEX = {
        0: "briefing",
        1: "workbench",
        2: "topology",
    }
    SECTION_OWNER = {
        "context_spine": "briefing",
        "repo_pulse": "briefing",
        "command_bar": "workbench",
        "action_rail": "workbench",
        "graph_radar": "topology",
    }

    def __init__(self, *, logger: Callable[[str], None] | None = None) -> None:
        self.state = DeckRuntimeState()
        self._logger = logger

    @property
    def active_tab_id(self) -> str:
        return self.state.active_tab_id

    @property
    def tab_dirty(self) -> set[str]:
        return self.state.tab_dirty

    @property
    def snapshot(self) -> dict[str, Any]:
        return self.state.snapshot

    def set_active_tab_from_index(self, index: int) -> str:
        next_tab = self.TAB_FROM_INDEX.get(int(index), "briefing")
        if self.state.active_tab_id != next_tab:
            self._log(f"tab:{self.state.active_tab_id}->{next_tab}")
        self.state.active_tab_id = next_tab
        return next_tab

    def push_snapshot(self, snapshot: dict[str, Any]) -> bool:
        changed = snapshot != self.state.snapshot
        self.state.snapshot = dict(snapshot)
        if changed:
            self._log("snapshot:changed")
            self.mark_all_tabs_dirty()
        return changed

    def mark_all_tabs_dirty(self) -> None:
        self.state.tab_dirty.update({"briefing", "workbench", "topology"})

    def mark_tab_dirty(self, tab_id: str) -> None:
        if tab_id:
            self.state.tab_dirty.add(tab_id)

    def should_refresh(self, tab_id: str) -> bool:
        return tab_id in self.state.tab_dirty

    def mark_refreshed(self, tab_id: str) -> None:
        self.state.tab_dirty.discard(tab_id)

    def set_runtime_visible(self, visible: bool) -> None:
        if self.state.runtime_visible != bool(visible):
            self._log(f"visible:{self.state.runtime_visible}->{bool(visible)}")
        self.state.runtime_visible = bool(visible)

    def section_owner_tab(self, section_id: str) -> str:
        return self.SECTION_OWNER.get(section_id, "")

    def _log(self, message: str) -> None:
        if callable(self._logger):
            try:
                self._logger(message)
            except Exception:
                return


__all__ = [
    "DeckRuntimeCoordinator",
    "DeckRuntimeState",
]

