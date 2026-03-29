from __future__ import annotations

from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject

from ..event_bus import Events
from .workstation_context import WorkstationContextRuntime


class WorkstationContextBridge(QObject):
    """Project-level context consolidator driven by EventBus signals."""

    def __init__(
        self,
        event_bus,
        context_runtime: WorkstationContextRuntime,
        tool_workspace=None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.event_bus = event_bus
        self.context_runtime = context_runtime
        self.tool_workspace = tool_workspace
        self._unsubscribers: list[object] = []
        self._wire_events()

    def dispose(self) -> None:
        for unsubscribe in self._unsubscribers:
            if callable(unsubscribe):
                try:
                    unsubscribe()
                except Exception:
                    continue
        self._unsubscribers.clear()

    def _wire_events(self) -> None:
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.INDEX_COMPLETED, self._on_index_completed)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.SEARCH_COMPLETED, self._on_search_completed)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.SEARCH_CLEARED, self._on_search_cleared)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.PREVIEW_OPENED, self._on_preview_opened)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.TOOL_ACTIVATED, self._on_tool_activated)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.TOOL_DEACTIVATED, self._on_tool_deactivated)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.STATUS_CHANGED, self._on_status_changed)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.COMMAND_EXECUTED, self._on_command_executed)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.COMMAND_FAILED, self._on_command_failed)
        )
        self._unsubscribers.append(
            self.event_bus.subscribe(Events.SHELL_GROUP_CHANGED, self._on_shell_group_changed)
        )

    def _on_index_completed(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        root = str(payload.get("root") or "").strip()
        file_count = self._to_int(payload.get("file_count"))
        ext_count = self._to_int(payload.get("ext_count"))
        self.context_runtime.update(
            repo_root=root,
            repo_name=Path(root).name if root else "",
            status_text=f"indexed files={file_count} ext={ext_count}",
        )
        self._update_active_tool_local_context(
            repo_root=root,
            repo_name=Path(root).name if root else "",
            indexed_files=file_count,
            indexed_extensions=ext_count,
        )

    def _on_search_completed(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        self.context_runtime.update(
            active_query=str(payload.get("query") or "").strip(),
            results_count=self._to_int(payload.get("results_count")),
            status_text="search-ready",
        )
        self._update_active_tool_local_context(
            active_query=str(payload.get("query") or "").strip(),
            results_count=self._to_int(payload.get("results_count")),
        )

    def _on_search_cleared(self, _payload: Any) -> None:
        self.context_runtime.update(
            active_query="",
            results_count=0,
            status_text="search-cleared",
        )
        self._update_active_tool_local_context(active_query="", results_count=0)

    def _on_preview_opened(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        self.context_runtime.update(
            active_file_relpath=str(payload.get("relpath") or "").strip(),
            status_text="preview-open",
        )
        self._update_active_tool_local_context(
            active_file_relpath=str(payload.get("relpath") or "").strip(),
            active_file_line=self._to_int(payload.get("line")),
        )

    def _on_tool_activated(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        tool_id = str(payload.get("tool_id") or "").strip()
        self.context_runtime.update(
            active_tool_id=tool_id,
            status_text=f"tool-active:{tool_id}",
        )
        self._update_active_tool_local_context(last_activation_reason=str(payload.get("reason") or "").strip())

    def _on_tool_deactivated(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            self.context_runtime.update(active_tool_id="", status_text="tool-inactive")
            return
        tool_id = str(payload.get("tool_id") or "").strip()
        current = self.context_runtime.current.active_tool_id
        if current == tool_id:
            self.context_runtime.update(active_tool_id="", status_text="tool-inactive")

    def _on_status_changed(self, payload: Any) -> None:
        if isinstance(payload, str):
            self.context_runtime.update(status_text=payload.strip())
            return
        if isinstance(payload, dict):
            message = str(payload.get("message") or payload.get("status") or "").strip()
            if message:
                self.context_runtime.update(status_text=message)

    def _on_command_executed(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        name = str(payload.get("name") or "").strip()
        if not name:
            return
        self.context_runtime.update(
            last_command=name,
            status_text=f"command:{name}",
        )
        self._update_active_tool_local_context(
            last_command=name,
            last_command_status="executed",
        )

    def _on_command_failed(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        name = str(payload.get("name") or "").strip()
        if not name:
            return
        error = str(payload.get("error") or "").strip()
        self.context_runtime.update(
            last_command=name,
            status_text=f"command_failed:{name} {error}".strip(),
        )
        self._update_active_tool_local_context(
            last_command=name,
            last_command_status="failed",
            last_command_error=error,
        )

    def _on_shell_group_changed(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        group_id = str(payload.get("group_id") or "").strip()
        if not group_id:
            return
        self.context_runtime.update(
            active_group=group_id,
            status_text=f"group:{group_id.lower()}",
        )
        self._update_active_tool_local_context(active_group=group_id)

    @staticmethod
    def _to_int(value: object) -> int:
        try:
            return int(value or 0)
        except (TypeError, ValueError):
            return 0

    def _update_active_tool_local_context(self, **changes: Any) -> None:
        if self.tool_workspace is None:
            return
        active_tool_id = getattr(self.tool_workspace, "active_tool_id", None)
        if not active_tool_id:
            return
        updater = getattr(self.tool_workspace, "update_tool_local_context", None)
        if not callable(updater):
            return
        try:
            updater(str(active_tool_id), reason="context-bridge", **changes)
        except Exception:
            return


__all__ = ["WorkstationContextBridge"]

