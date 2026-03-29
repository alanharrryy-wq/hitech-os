from __future__ import annotations

from typing import Any

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QLabel, QProgressBar, QStatusBar

from ..event_bus import Events

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


class StatusStripBuilder:
    """Build the shell status strip and expose stable status widgets."""

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        self.main = main_window
        self._unsubscribers: list[object] = []

    def build(self) -> None:
        status = QStatusBar(self.main)
        status.setObjectName('statusStripSurface')
        status.setProperty('visualRole', 'status-surface')
        status.setProperty('visualTier', 'themed')
        status.setSizeGripEnabled(False)

        self.main.progress_bar = QProgressBar(self.main)
        self.main.progress_bar.setObjectName('statusProgressSurface')
        self.main.progress_bar.setProperty('visualRole', 'status-surface')
        self.main.progress_bar.setProperty('visualTier', 'themed')
        self.main.progress_bar.setFixedWidth(196)
        self.main.progress_bar.setTextVisible(False)
        self.main.progress_bar.hide()
        status.addPermanentWidget(self.main.progress_bar)

        self.main.status_activity_label = QLabel("activity: idle", self.main)
        self.main.status_activity_label.setObjectName('statusActivitySurface')
        self.main.status_activity_label.setProperty('visualRole', 'status-surface')
        self.main.status_activity_label.setProperty('visualTier', 'themed')
        status.addPermanentWidget(self.main.status_activity_label)

        self.main.status_group_label = QLabel("group: explore", self.main)
        self.main.status_group_label.setObjectName('statusGroupSurface')
        self.main.status_group_label.setProperty('visualRole', 'status-surface')
        self.main.status_group_label.setProperty('visualTier', 'themed')
        status.addPermanentWidget(self.main.status_group_label)

        self.main.status_tool_label = QLabel("tool: none", self.main)
        self.main.status_tool_label.setObjectName('statusToolSurface')
        self.main.status_tool_label.setProperty('visualRole', 'status-surface')
        self.main.status_tool_label.setProperty('visualTier', 'themed')
        status.addPermanentWidget(self.main.status_tool_label)

        self.main.status_repo_label = QLabel("repo: not selected", self.main)
        self.main.status_repo_label.setObjectName('statusRepoSurface')
        self.main.status_repo_label.setProperty('visualRole', 'status-surface')
        self.main.status_repo_label.setProperty('visualTier', 'themed')
        status.addPermanentWidget(self.main.status_repo_label)

        self.main.status_scope_label = QLabel("scope: all", self.main)
        self.main.status_scope_label.setObjectName('statusScopeSurface')
        self.main.status_scope_label.setProperty('visualRole', 'status-surface')
        self.main.status_scope_label.setProperty('visualTier', 'themed')
        status.addPermanentWidget(self.main.status_scope_label)

        self.main.status_summary = QLabel("0 files", self.main)
        self.main.status_summary.setObjectName('statusSummarySurface')
        self.main.status_summary.setProperty('visualRole', 'status-surface')
        self.main.status_summary.setProperty('visualTier', 'themed')
        status.addPermanentWidget(self.main.status_summary)

        status.showMessage("Ready. Workstation initialized.", 2200)
        self.main.setStatusBar(status)
        self._wire_runtime_status_events()

    def dispose(self) -> None:
        while self._unsubscribers:
            unsub = self._unsubscribers.pop()
            if callable(unsub):
                try:
                    unsub()
                except Exception:
                    pass

    def _wire_runtime_status_events(self) -> None:
        bus = getattr(self.main, "event_bus", None)
        if bus is None or not hasattr(bus, "subscribe"):
            return

        for event_name in (
            Events.WORKSTATION_CONTEXT_CHANGED,
            Events.PROCESS_SESSION_STATE_CHANGED,
            Events.TOOL_LIFECYCLE_TRANSITION,
        ):
            try:
                unsub = bus.subscribe(
                    event_name,
                    lambda payload, _event_name=event_name: self._on_runtime_event(_event_name, payload),
                )
                self._unsubscribers.append(unsub)
            except Exception:
                continue

    def _on_runtime_event(self, event_name: str, payload: Any) -> None:
        if event_name == Events.WORKSTATION_CONTEXT_CHANGED and isinstance(payload, dict):
            self._apply_context_payload(payload)
            return
        if event_name == Events.PROCESS_SESSION_STATE_CHANGED and isinstance(payload, dict):
            state = str(payload.get("state") or "").strip().lower()
            if state:
                self.main.status_activity_label.setText(f"activity: {state}")
            return
        if event_name == Events.TOOL_LIFECYCLE_TRANSITION and isinstance(payload, dict):
            action = str(payload.get("action") or "").strip().lower()
            if action:
                self.main.status_activity_label.setText(f"activity: tool-{action}")

    def _apply_context_payload(self, payload: dict[str, Any]) -> None:
        status_text = str(payload.get("status_text") or "").strip()
        if status_text:
            self.main.status_activity_label.setText(f"activity: {status_text}")

        active_tool_id = str(payload.get("active_tool_id") or "").strip()
        self.main.status_tool_label.setText(f"tool: {active_tool_id or 'none'}")

        active_group = str(payload.get("active_group") or "").strip()
        if active_group:
            self.main.status_group_label.setText(f"group: {active_group}")

        repo_name = str(payload.get("repo_name") or "").strip()
        repo_root = str(payload.get("repo_root") or "").strip()
        repo_display = repo_name or repo_root or "not selected"
        self.main.status_repo_label.setText(f"repo: {repo_display}")

        scope = str(payload.get("active_scope") or "").strip() or "all"
        ext = str(payload.get("active_extension") or "").strip()
        if ext:
            self.main.status_scope_label.setText(f"scope: {scope} | ext: {ext}")
        else:
            self.main.status_scope_label.setText(f"scope: {scope}")

        results_count = payload.get("results_count")
        if results_count is not None:
            try:
                count = int(results_count)
            except (TypeError, ValueError):
                count = 0
            self.main.status_summary.setText(f"{count} results")
