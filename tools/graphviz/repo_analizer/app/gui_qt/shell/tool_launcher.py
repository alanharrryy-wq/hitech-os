from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..event_bus import Events

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


class ToolLauncherPanel(QWidget):
    """Dedicated launcher/switcher surface for product-level tools."""

    ROLE_TOOL_ID = Qt.UserRole + 100
    ROLE_TOOL_ENABLED = Qt.UserRole + 101

    def __init__(self, main_window: RepoAnalyzerMainWindow, parent: QWidget | None = None) -> None:
        super().__init__(parent or main_window)
        self.main = main_window
        self.setObjectName("toolLauncherSurface")
        self.setProperty("visualRole", "panel-surface")
        self.setProperty("visualTier", "themed")

        self._unsubscribers: list[callable] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        title = QLabel("Tools", self)
        title.setObjectName("heroTitleLabel")
        root.addWidget(title)

        subtitle = QLabel(
            "Canonical tool switcher. Exactly one active tool workspace at a time.",
            self,
        )
        subtitle.setObjectName("panelMutedLabel")
        subtitle.setWordWrap(True)
        root.addWidget(subtitle)

        self.list_widget = QListWidget(self)
        self.list_widget.itemActivated.connect(self._on_item_activated)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        root.addWidget(self.list_widget, 1)

        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(0, 0, 0, 0)
        buttons_row.setSpacing(6)

        self.activate_btn = QPushButton("Activate", self)
        self.activate_btn.clicked.connect(self._activate_selected_tool)
        buttons_row.addWidget(self.activate_btn)

        self.close_btn = QPushButton("Close (Hide)", self)
        self.close_btn.clicked.connect(self._close_selected_tool)
        buttons_row.addWidget(self.close_btn)

        self.toggle_enabled_btn = QPushButton("Disable", self)
        self.toggle_enabled_btn.clicked.connect(self._toggle_selected_tool_enabled)
        buttons_row.addWidget(self.toggle_enabled_btn)

        self.reopen_btn = QPushButton("Reopen Last", self)
        self.reopen_btn.clicked.connect(self._reopen_last_tool)
        buttons_row.addWidget(self.reopen_btn)

        self.preferences_btn = QPushButton("Preferences", self)
        self.preferences_btn.clicked.connect(self.main.open_preferences_dialog)
        buttons_row.addWidget(self.preferences_btn)

        root.addLayout(buttons_row)
        self._wire_runtime_events()
        self.refresh()

    def refresh(self) -> None:
        catalog = self.main.service_container.get("tool_catalog")
        tool_workspace = self.main.service_container.get("tool_workspace")
        if catalog is None or tool_workspace is None:
            return

        visible_ids = {entry.tool_id for entry in tool_workspace.list_tools() if entry.visible}
        entries = catalog.list_launch_entries(
            active_tool_id=tool_workspace.active_tool_id,
            visible_tool_ids=visible_ids,
        )

        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for entry in entries:
            label = f"[{entry.category}] {entry.display_name}"
            if entry.active:
                label = f"{label}  [Active]"
            elif entry.visible:
                label = f"{label}  [Visible]"
            if not entry.enabled:
                label = f"{label}  [Disabled]"
            item = QListWidgetItem(label, self.list_widget)
            item.setData(self.ROLE_TOOL_ID, entry.tool_id)
            item.setData(self.ROLE_TOOL_ENABLED, bool(entry.enabled))
            item.setToolTip(entry.description or entry.tool_id)
        self.list_widget.blockSignals(False)
        self._sync_buttons()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        for unsubscribe in self._unsubscribers:
            try:
                unsubscribe()
            except Exception:
                pass
        self._unsubscribers.clear()
        super().closeEvent(event)

    def _wire_runtime_events(self) -> None:
        bus = self.main.event_bus
        for event_name in (
            Events.TOOL_REGISTERED,
            Events.TOOL_ACTIVATED,
            Events.TOOL_DEACTIVATED,
        ):
            unsub = bus.subscribe(event_name, lambda _payload=None: self.refresh())
            self._unsubscribers.append(unsub)

    def _on_item_activated(self, item: QListWidgetItem) -> None:
        tool_id = str(item.data(self.ROLE_TOOL_ID) or "").strip()
        if not tool_id:
            return
        self._activate_tool(tool_id)

    def _activate_selected_tool(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            return
        self._on_item_activated(item)

    def _hide_selected_tool(self) -> None:
        self._close_selected_tool()

    def _close_selected_tool(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            return
        tool_id = str(item.data(self.ROLE_TOOL_ID) or "").strip()
        if not tool_id:
            return
        tool_workspace = self.main.service_container.get("tool_workspace")
        if tool_workspace is None:
            return
        tool_workspace.close_tool(tool_id, reason="launcher-close")
        self.refresh()

    def _reopen_last_tool(self) -> None:
        reopen = getattr(self.main, "reopen_last_tool_via_group", None)
        if callable(reopen):
            reopen(reason="launcher-reopen")
        else:
            tool_workspace = self.main.service_container.get("tool_workspace")
            if tool_workspace is not None:
                tool_workspace.reopen_last_active_tool()
        self.refresh()

    def _toggle_selected_tool_enabled(self) -> None:
        item = self.list_widget.currentItem()
        if item is None:
            return
        tool_id = str(item.data(self.ROLE_TOOL_ID) or "").strip()
        if not tool_id:
            return
        enabled = bool(item.data(self.ROLE_TOOL_ENABLED))
        tool_workspace = self.main.service_container.get("tool_workspace")
        if tool_workspace is None:
            return
        tool_workspace.set_tool_enabled(tool_id, not enabled, reason="launcher-toggle-enabled")
        self.refresh()

    def _activate_tool(self, tool_id: str) -> None:
        tool_workspace = self.main.service_container.get("tool_workspace")
        catalog = self.main.service_container.get("tool_catalog")
        if tool_workspace is None or catalog is None:
            return
        route = getattr(self.main, "activate_group_for_tool", None)
        if callable(route):
            route(tool_id, reason="launcher")
        descriptor = catalog.get_tool(tool_id)
        if descriptor is not None and not descriptor.enabled:
            return
        if tool_workspace.activate_tool(tool_id, reason="launcher"):
            catalog.mark_recent(tool_id)
        self.refresh()

    def _on_selection_changed(self) -> None:
        self._sync_buttons()

    def _sync_buttons(self) -> None:
        item = self.list_widget.currentItem()
        has_item = item is not None
        self.activate_btn.setEnabled(has_item)
        self.close_btn.setEnabled(has_item)
        self.toggle_enabled_btn.setEnabled(has_item)
        if item is None:
            self.toggle_enabled_btn.setText("Disable")
            return
        enabled = bool(item.data(self.ROLE_TOOL_ENABLED))
        self.toggle_enabled_btn.setText("Disable" if enabled else "Enable")
