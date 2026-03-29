from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Literal

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QDockWidget

from ..event_bus import Events
from ..tools.models import ToolState

if TYPE_CHECKING:
    from ..main_window import RepoAnalyzerMainWindow


ToolSource = Literal["core", "plugin"]


@dataclass(slots=True)
class ToolSurfaceRecord:
    contribution_id: str
    tool_id: str
    display_name: str
    dock: QDockWidget
    source: ToolSource
    user_facing: bool


@dataclass(frozen=True, slots=True)
class ToolEntry:
    tool_id: str
    display_name: str
    active: bool
    visible: bool
    surface_count: int


class ToolWorkspaceCoordinator(QObject):
    """
    Runtime for the product-facing "Tools" model.

    Internally plugins still provide contributions, but this coordinator normalizes
    docking lifecycle and enables a single-active-tool workflow.
    """

    ACTIVE_TOOL_KEY = "workspace_active_tool_id"
    RESTORE_SNAPSHOT_KEY = "workspace_restore_snapshot_v1"

    def __init__(self, main_window: RepoAnalyzerMainWindow) -> None:
        super().__init__(main_window)
        self.main = main_window
        self._surfaces: dict[str, ToolSurfaceRecord] = {}
        self._tool_order: list[str] = []
        self._tool_display_names: dict[str, str] = {}
        self._dock_visibility_handlers: dict[str, object] = {}
        self._active_tool_id: str | None = self._load_active_tool_id()
        snapshot = self.load_restore_snapshot()
        self._last_active_tool_id: str | None = str(
            snapshot.get("last_active_tool_id") or self._active_tool_id or ""
        ).strip() or self._active_tool_id
        self._single_active_mode: bool = bool(snapshot.get("single_active_mode", True))
        self._suspend_visibility_events = False
        self._tool_states: dict[str, ToolState] = {}
        self._tool_local_context: dict[str, dict[str, Any]] = {}
        self._global_context_snapshot: dict[str, Any] = {}
        self._invariant_guard = False
        self._context_unsubscribe: Callable[[], None] | None = None
        self._subscribe_context_runtime()

    @property
    def active_tool_id(self) -> str | None:
        return self._active_tool_id

    def dispose(self) -> None:
        self.persist_restore_snapshot()
        if callable(self._context_unsubscribe):
            try:
                self._context_unsubscribe()
            except Exception:
                pass
        self._context_unsubscribe = None

    def build_restore_snapshot(self) -> dict[str, Any]:
        return {
            "active_tool_id": self._active_tool_id or "",
            "last_active_tool_id": self._last_active_tool_id or "",
            "single_active_mode": bool(self._single_active_mode),
            "tool_states": dict(self._tool_states),
            "known_tool_order": list(self._tool_order),
        }

    def persist_restore_snapshot(self) -> None:
        try:
            self.main.settings.setValue(self.RESTORE_SNAPSHOT_KEY, self.build_restore_snapshot())
        except Exception:
            return

    def load_restore_snapshot(self) -> dict[str, Any]:
        raw = self.main.settings.value(self.RESTORE_SNAPSHOT_KEY, {})
        if isinstance(raw, dict):
            return dict(raw)
        return {}

    def set_single_active_mode(self, enabled: bool) -> None:
        self._single_active_mode = bool(enabled)
        if self._single_active_mode:
            self._enforce_single_active_invariant(reason="layout-mode")

    def register_core_surface(
        self,
        *,
        contribution_id: str,
        title: str,
        dock: QDockWidget,
    ) -> None:
        self._register_surface(
            contribution_id=contribution_id,
            title=title,
            dock=dock,
            tool_id="shell_core",
            source="core",
            user_facing=False,
        )
        self._set_tool_state("shell_core", "registered", reason="core-surface-register")

    def register_tool_surface(
        self,
        *,
        contribution_id: str,
        title: str,
        dock: QDockWidget,
        tool_id: str | None = None,
        display_name: str | None = None,
        user_facing: bool = True,
    ) -> None:
        normalized_tool_id = self._normalize_tool_id(
            tool_id or self._derive_tool_id(contribution_id)
        )
        self._register_surface(
            contribution_id=contribution_id,
            title=title,
            dock=dock,
            tool_id=normalized_tool_id,
            display_name=display_name or self._humanize_tool_id(normalized_tool_id),
            source="plugin",
            user_facing=user_facing,
        )
        self._register_catalog_tool(
            tool_id=normalized_tool_id,
            display_name=display_name or self._humanize_tool_id(normalized_tool_id),
            source="plugin",
            user_facing=user_facing,
        )
        self._emit_registered(normalized_tool_id)

    def restore_startup_state(self) -> None:
        tool_ids = [entry.tool_id for entry in self.list_tools()]
        if not tool_ids:
            return

        enabled_tool_ids = [tool_id for tool_id in tool_ids if self._is_tool_enabled(tool_id)]
        if not enabled_tool_ids:
            return

        target = self._active_tool_id if self._active_tool_id in enabled_tool_ids else None
        if target is None and self._last_active_tool_id in enabled_tool_ids:
            target = self._last_active_tool_id
        if target is None:
            target = enabled_tool_ids[0]

        if self._single_active_mode:
            if not self.activate_tool(target, reason="startup"):
                for fallback in enabled_tool_ids:
                    if fallback == target:
                        continue
                    if self.activate_tool(fallback, reason="startup-fallback"):
                        break
        else:
            self.show_tool(target, reason="startup")
            self._set_active_tool(target, reason="startup")
        self._enforce_single_active_invariant(reason="startup-restore")

    def activate_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        tool_id = self._normalize_tool_id(tool_id)
        self._publish_lifecycle_event(
            tool_id,
            action="activate",
            reason=reason,
            status="requested",
        )
        if not self._is_tool_enabled(tool_id):
            self._publish_lifecycle_event(
                tool_id,
                action="activate",
                reason=reason,
                status="blocked-disabled",
            )
            return False
        surfaces = [x for x in self._surfaces.values() if x.tool_id == tool_id and x.source == "plugin"]
        if not surfaces:
            self._publish_lifecycle_event(
                tool_id,
                action="activate",
                reason=reason,
                status="blocked-missing-surface",
            )
            return False

        self._suspend_visibility_events = True
        try:
            if self._single_active_mode:
                for record in self._surfaces.values():
                    if record.source != "plugin":
                        continue
                    if record.tool_id == tool_id:
                        self._notify_tool_lifecycle(record.dock, "restore")
                        self._safe_show(record.dock, raise_after=True)
                    else:
                        self._notify_tool_lifecycle(record.dock, "suspend")
                        self._safe_hide(record.dock)
            else:
                for record in surfaces:
                    self._notify_tool_lifecycle(record.dock, "restore")
                    self._safe_show(record.dock, raise_after=False)
        finally:
            self._suspend_visibility_events = False

        self._notify_tool_group_lifecycle(tool_id, "activate")
        self._set_active_tool(tool_id, reason=reason)
        self._enforce_single_active_invariant(reason=f"activate:{reason}")
        self._publish_lifecycle_event(
            tool_id,
            action="activate",
            reason=reason,
            status="applied",
        )
        return True

    def deactivate_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        tool_id = self._normalize_tool_id(tool_id)
        self._publish_lifecycle_event(
            tool_id,
            action="deactivate",
            reason=reason,
            status="requested",
        )
        surfaces = [x for x in self._surfaces.values() if x.tool_id == tool_id and x.source == "plugin"]
        if not surfaces:
            self._publish_lifecycle_event(
                tool_id,
                action="deactivate",
                reason=reason,
                status="blocked-missing-surface",
            )
            return False
        self._suspend_visibility_events = True
        try:
            for record in surfaces:
                self._notify_tool_lifecycle(record.dock, "deactivate")
        finally:
            self._suspend_visibility_events = False
        if self._active_tool_id == tool_id:
            self._clear_active_tool(reason=reason)
        self._set_tool_state(tool_id, "inactive", reason=f"{reason}:deactivate")
        self._enforce_single_active_invariant(reason=f"deactivate:{reason}")
        self._publish_lifecycle_event(
            tool_id,
            action="deactivate",
            reason=reason,
            status="applied",
        )
        return True

    def show_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        if self._single_active_mode:
            return self.activate_tool(tool_id, reason=reason)
        tool_id = self._normalize_tool_id(tool_id)
        if not self._is_tool_enabled(tool_id):
            return False
        surfaces = [x for x in self._surfaces.values() if x.tool_id == tool_id and x.source == "plugin"]
        if not surfaces:
            return False

        self._suspend_visibility_events = True
        try:
            for record in surfaces:
                self._notify_tool_lifecycle(record.dock, "restore")
                self._safe_show(record.dock, raise_after=False)
        finally:
            self._suspend_visibility_events = False
        self._set_active_tool(tool_id, reason=reason)
        return True

    def hide_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        tool_id = self._normalize_tool_id(tool_id)
        self._publish_lifecycle_event(
            tool_id,
            action="hide",
            reason=reason,
            status="requested",
        )
        surfaces = [x for x in self._surfaces.values() if x.tool_id == tool_id and x.source == "plugin"]
        if not surfaces:
            self._publish_lifecycle_event(
                tool_id,
                action="hide",
                reason=reason,
                status="blocked-missing-surface",
            )
            return False

        self._suspend_visibility_events = True
        try:
            for record in surfaces:
                self._notify_tool_lifecycle(record.dock, "hide")
                self._safe_hide(record.dock)
        finally:
            self._suspend_visibility_events = False

        if self._active_tool_id == tool_id:
            self._clear_active_tool(reason=reason)
        self._set_tool_state(tool_id, "hidden", reason=f"{reason}:hide")
        self._enforce_single_active_invariant(reason=f"hide:{reason}")
        self._publish_lifecycle_event(
            tool_id,
            action="hide",
            reason=reason,
            status="applied",
        )
        return True

    def close_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        """
        Product-facing close operation.

        Close means hide + suspend without destroying tool surfaces.
        """
        tool_id = self._normalize_tool_id(tool_id)
        if not self.hide_tool(tool_id, reason=reason):
            return False
        self._set_tool_state(tool_id, "suspended", reason=f"{reason}:close")
        self._publish_lifecycle_event(
            tool_id,
            action="close",
            reason=reason,
            status="applied",
            details={"destructive": False},
        )
        return True

    def unload_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        tool_id = self._normalize_tool_id(tool_id)
        self._publish_lifecycle_event(
            tool_id,
            action="unload",
            reason=reason,
            status="requested",
        )
        surfaces = [x for x in self._surfaces.values() if x.tool_id == tool_id and x.source == "plugin"]
        if not surfaces:
            self._publish_lifecycle_event(
                tool_id,
                action="unload",
                reason=reason,
                status="blocked-missing-surface",
            )
            return False
        self._suspend_visibility_events = True
        try:
            for record in surfaces:
                self._notify_tool_lifecycle(record.dock, "unload")
                self._safe_hide(record.dock)
        finally:
            self._suspend_visibility_events = False

        if self._active_tool_id == tool_id:
            self._clear_active_tool(reason=reason)
        self._set_tool_state(tool_id, "unloaded", reason=f"{reason}:unload")
        self._enforce_single_active_invariant(reason=f"unload:{reason}")
        self._publish_lifecycle_event(
            tool_id,
            action="unload",
            reason=reason,
            status="applied",
        )
        return True

    def destroy_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        tool_id = self._normalize_tool_id(tool_id)
        self._publish_lifecycle_event(
            tool_id,
            action="destroy",
            reason=reason,
            status="requested",
        )
        surfaces = [x for x in self._surfaces.values() if x.tool_id == tool_id and x.source == "plugin"]
        if not surfaces:
            self._publish_lifecycle_event(
                tool_id,
                action="destroy",
                reason=reason,
                status="blocked-missing-surface",
            )
            return False

        self._suspend_visibility_events = True
        try:
            for record in surfaces:
                self._notify_tool_lifecycle(record.dock, "destroy")
                try:
                    record.dock.hide()
                    record.dock.setParent(None)
                    record.dock.deleteLater()
                except RuntimeError:
                    pass
        finally:
            self._suspend_visibility_events = False

        self._surfaces = {cid: rec for cid, rec in self._surfaces.items() if rec.tool_id != tool_id}
        if self._active_tool_id == tool_id:
            self._clear_active_tool(reason=reason)
        self._set_tool_state(tool_id, "destroyed", reason=f"{reason}:destroy")
        self._tool_local_context.pop(tool_id, None)
        self._enforce_single_active_invariant(reason=f"destroy:{reason}")
        self._publish_lifecycle_event(
            tool_id,
            action="destroy",
            reason=reason,
            status="applied",
        )
        return True

    def reopen_last_active_tool(self) -> bool:
        target = self._active_tool_id or self._last_active_tool_id
        if target and not self._is_tool_enabled(target):
            target = None
        if not target:
            entries = [entry for entry in self.list_tools() if self._is_tool_enabled(entry.tool_id)]
            target = entries[0].tool_id if entries else None
        if not target:
            self._publish_lifecycle_event(
                "",
                action="reopen_last",
                reason="reopen",
                status="blocked-no-target",
            )
            return False
        reopened = self.activate_tool(target, reason="reopen")
        self._publish_lifecycle_event(
            target,
            action="reopen_last",
            reason="reopen",
            status="applied" if reopened else "failed",
        )
        return reopened

    def set_tool_enabled(self, tool_id: str, enabled: bool, *, reason: str = "manual") -> bool:
        normalized = self._normalize_tool_id(tool_id)
        catalog = self.main.service_container.get("tool_catalog")
        if catalog is None or not catalog.has_tool(normalized):
            return False
        try:
            catalog.set_enabled(normalized, bool(enabled))
        except Exception:
            return False
        if not enabled:
            self.close_tool(normalized, reason=f"{reason}:disabled")
            self._set_tool_state(normalized, "suspended", reason=f"{reason}:disabled")
        else:
            if self._tool_states.get(normalized) == "destroyed":
                self._set_tool_state(normalized, "registered", reason=f"{reason}:enabled")
            else:
                self._set_tool_state(normalized, "inactive", reason=f"{reason}:enabled")
        self._publish_lifecycle_event(
            normalized,
            action="set_enabled",
            reason=reason,
            status="applied",
            details={"enabled": bool(enabled)},
        )
        self._enforce_single_active_invariant(reason=f"set-enabled:{reason}")
        self._refresh_tool_menu()
        return True

    def list_tools(self) -> tuple[ToolEntry, ...]:
        tool_ids: list[str] = []
        for tool_id in self._tool_order:
            if tool_id == "shell_core":
                continue
            if any(
                record.tool_id == tool_id and record.source == "plugin" and record.user_facing
                for record in self._surfaces.values()
            ):
                tool_ids.append(tool_id)

        entries: list[ToolEntry] = []
        for tool_id in tool_ids:
            records = [
                record
                for record in self._surfaces.values()
                if record.tool_id == tool_id and record.source == "plugin"
            ]
            visible = any(self._is_dock_visible(record.dock) for record in records)
            entries.append(
                ToolEntry(
                    tool_id=tool_id,
                    display_name=self._tool_display_names.get(
                        tool_id,
                        self._humanize_tool_id(tool_id),
                    ),
                    active=tool_id == self._active_tool_id,
                    visible=visible,
                    surface_count=len(records),
                )
            )
        return tuple(entries)

    def list_tool_surfaces(self) -> tuple[ToolSurfaceRecord, ...]:
        return tuple(
            record
            for record in self._surfaces.values()
            if record.source == "plugin" and record.user_facing
        )

    def _register_surface(
        self,
        *,
        contribution_id: str,
        title: str,
        dock: QDockWidget,
        tool_id: str,
        source: ToolSource,
        user_facing: bool,
        display_name: str | None = None,
    ) -> None:
        if not contribution_id:
            raise ValueError("contribution_id cannot be empty")

        normalized_tool_id = self._normalize_tool_id(tool_id)
        resolved_display_name = (display_name or title or normalized_tool_id).strip()

        # Keep docks hide/show safe for reopen.
        dock.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        dock.setProperty("toolId", normalized_tool_id)
        dock.setProperty("toolContributionId", contribution_id)
        dock.setProperty("toolSource", source)

        if contribution_id not in self._dock_visibility_handlers:
            def _on_visibility_changed(visible: bool, cid: str = contribution_id) -> None:
                self._handle_surface_visibility(cid, visible)

            dock.visibilityChanged.connect(_on_visibility_changed)
            self._dock_visibility_handlers[contribution_id] = _on_visibility_changed

        self._surfaces[contribution_id] = ToolSurfaceRecord(
            contribution_id=contribution_id,
            tool_id=normalized_tool_id,
            display_name=resolved_display_name,
            dock=dock,
            source=source,
            user_facing=user_facing,
        )
        self._tool_display_names[normalized_tool_id] = resolved_display_name
        if normalized_tool_id not in self._tool_order:
            self._tool_order.append(normalized_tool_id)
        self._set_tool_state(normalized_tool_id, "registered", reason="surface-register")
        self._push_tool_context(normalized_tool_id, reason="surface-register")

    def _handle_surface_visibility(self, contribution_id: str, visible: bool) -> None:
        if self._suspend_visibility_events:
            return

        record = self._surfaces.get(contribution_id)
        if record is None or record.source != "plugin":
            return

        if visible:
            if self._single_active_mode:
                self.activate_tool(record.tool_id, reason="surface-visible")
            else:
                self._set_active_tool(record.tool_id, reason="surface-visible")
            self._enforce_single_active_invariant(reason="surface-visible")
            return

        if self._active_tool_id != record.tool_id:
            self._enforce_single_active_invariant(reason="surface-hidden-nonactive")
            return
        if self._tool_has_visible_surface(record.tool_id):
            self._enforce_single_active_invariant(reason="surface-hidden-still-visible")
            return
        self._clear_active_tool(reason="surface-hidden")
        self._enforce_single_active_invariant(reason="surface-hidden")

    def _tool_has_visible_surface(self, tool_id: str) -> bool:
        return any(
            record.tool_id == tool_id
            and record.source == "plugin"
            and self._is_dock_visible(record.dock)
            for record in self._surfaces.values()
        )

    def _set_active_tool(self, tool_id: str, *, reason: str) -> None:
        previous = self._active_tool_id
        if previous == tool_id:
            self._set_tool_state(tool_id, "active", reason=f"{reason}:active-keep")
            self._push_tool_context(tool_id, reason=f"active-keep:{reason}")
            return

        self._notify_tool_group_lifecycle(previous or "", "deactivate")
        self._active_tool_id = tool_id
        self._last_active_tool_id = tool_id
        self._persist_active_tool(tool_id)
        self._set_tool_state(tool_id, "active", reason=f"{reason}:active")
        self._mark_recent_tool(tool_id)
        self._sync_workstation_context(active_tool_id=tool_id)
        self._push_tool_context(tool_id, reason=f"activate:{reason}")

        if previous:
            self.main.event_bus.publish(
                Events.TOOL_DEACTIVATED,
                {"tool_id": previous, "reason": reason},
            )
            if previous != tool_id and self._tool_states.get(previous) not in {"destroyed", "unloaded"}:
                self._set_tool_state(previous, "inactive", reason=f"{reason}:previous-inactive")
        self.main.event_bus.publish(
            Events.TOOL_ACTIVATED,
            {"tool_id": tool_id, "reason": reason},
        )
        self._refresh_tool_menu()

    def _clear_active_tool(self, *, reason: str) -> None:
        previous = self._active_tool_id
        if not previous:
            return
        self._active_tool_id = None
        self._persist_active_tool("")
        if self._tool_states.get(previous) not in {"destroyed", "unloaded"}:
            self._set_tool_state(previous, "inactive", reason=f"{reason}:active-cleared")
        self._sync_workstation_context(active_tool_id="")
        self.main.event_bus.publish(
            Events.TOOL_DEACTIVATED,
            {"tool_id": previous, "reason": reason},
        )
        self._refresh_tool_menu()

    def _emit_registered(self, tool_id: str) -> None:
        self.main.event_bus.publish(
            Events.TOOL_REGISTERED,
            {"tool_id": tool_id},
        )
        self._refresh_tool_menu()

    def _load_active_tool_id(self) -> str | None:
        raw = self.main.settings.value(self.ACTIVE_TOOL_KEY, "")
        value = str(raw or "").strip()
        return value or None

    def _persist_active_tool(self, tool_id: str) -> None:
        self.main.settings.setValue(self.ACTIVE_TOOL_KEY, tool_id)

    def _derive_tool_id(self, contribution_id: str) -> str:
        head = str(contribution_id or "").split(".", 1)[0]
        return self._normalize_tool_id(head)

    def _normalize_tool_id(self, value: object) -> str:
        try:
            raw = str(value).strip().lower()
        except RecursionError:
            raw = ""
        except Exception:
            raw = ""
        normalized = "".join(ch if ch.isalnum() else "_" for ch in raw)
        return normalized.strip("_") or "tool"

    def _humanize_tool_id(self, tool_id: str) -> str:
        parts = [part for part in tool_id.split("_") if part]
        return " ".join(part.capitalize() for part in parts) or "Tool"

    def _safe_show(self, dock: QDockWidget, *, raise_after: bool) -> None:
        try:
            dock.show()
            if raise_after:
                dock.raise_()
        except RuntimeError:
            return

    def _safe_hide(self, dock: QDockWidget) -> None:
        try:
            dock.hide()
        except RuntimeError:
            return

    def _is_dock_visible(self, dock: QDockWidget) -> bool:
        try:
            return bool(dock.isVisible())
        except RuntimeError:
            return False

    def _refresh_tool_menu(self) -> None:
        menu_builder = getattr(self.main, "shell_menu_builder", None)
        if menu_builder is None or not hasattr(menu_builder, "refresh_tool_entries"):
            return
        try:
            menu_builder.refresh_tool_entries()
        except Exception:
            return

    def _set_tool_state(self, tool_id: str, state: ToolState, *, reason: str = "internal") -> None:
        normalized = self._normalize_tool_id(tool_id)
        if not normalized:
            return
        previous = self._tool_states.get(normalized)
        if previous == state:
            return
        self._tool_states[normalized] = state
        self._publish_lifecycle_event(
            normalized,
            action="state",
            reason=reason,
            status="changed",
            details={"from_state": previous or "", "to_state": state},
        )
        catalog = self.main.service_container.get("tool_catalog")
        if catalog is not None:
            try:
                catalog.set_state(normalized, state)
            except Exception:
                pass

    def _register_catalog_tool(
        self,
        *,
        tool_id: str,
        display_name: str,
        source: ToolSource,
        user_facing: bool,
    ) -> None:
        catalog = self.main.service_container.get("tool_catalog")
        if catalog is None:
            return
        if catalog.has_tool(tool_id):
            return
        try:
            catalog.register_tool(
                tool_id,
                display_name=display_name,
                description=f"{display_name} tool surface",
                category="other",
                source="plugin" if source == "plugin" else "core",
                enabled=True,
                user_facing=user_facing,
                state=self._tool_states.get(tool_id, "registered"),
            )
        except Exception:
            return

    def _mark_recent_tool(self, tool_id: str) -> None:
        catalog = self.main.service_container.get("tool_catalog")
        if catalog is None:
            return
        try:
            catalog.mark_recent(tool_id)
        except Exception:
            return

    def _is_tool_enabled(self, tool_id: str) -> bool:
        catalog = self.main.service_container.get("tool_catalog")
        if catalog is None:
            return True
        descriptor = catalog.get_tool(tool_id)
        if descriptor is None:
            return True
        return bool(descriptor.enabled)

    def update_tool_local_context(
        self,
        tool_id: str,
        *,
        reason: str = "local-context",
        **changes: Any,
    ) -> dict[str, Any]:
        normalized = self._normalize_tool_id(tool_id)
        current = dict(self._tool_local_context.get(normalized, {}))
        changed = False
        for key, value in changes.items():
            if not str(key).strip():
                continue
            if current.get(key) != value:
                current[str(key)] = value
                changed = True
        if changed:
            self._tool_local_context[normalized] = current
            self._push_tool_context(normalized, reason=reason)
        return dict(self._tool_local_context.get(normalized, {}))

    def get_tool_local_context(self, tool_id: str) -> dict[str, Any]:
        normalized = self._normalize_tool_id(tool_id)
        return dict(self._tool_local_context.get(normalized, {}))

    def clear_tool_local_context(self, tool_id: str, *, reason: str = "local-context-clear") -> None:
        normalized = self._normalize_tool_id(tool_id)
        if normalized not in self._tool_local_context:
            return
        self._tool_local_context.pop(normalized, None)
        self._push_tool_context(normalized, reason=reason)

    def _subscribe_context_runtime(self) -> None:
        bus = getattr(self.main, "event_bus", None)
        if bus is None or not hasattr(bus, "subscribe"):
            return
        try:
            self._context_unsubscribe = bus.subscribe(
                Events.WORKSTATION_CONTEXT_CHANGED,
                self._on_workstation_context_changed,
            )
        except Exception:
            self._context_unsubscribe = None

    def _on_workstation_context_changed(self, payload: Any) -> None:
        if not isinstance(payload, dict):
            return
        self._global_context_snapshot = dict(payload)
        if self._active_tool_id:
            self._push_tool_context(self._active_tool_id, reason="global-context")

    def _push_tool_context(self, tool_id: str, *, reason: str) -> None:
        normalized = self._normalize_tool_id(tool_id)
        payload = {
            "tool_id": normalized,
            "active_tool_id": self._active_tool_id or "",
            "reason": reason,
            "global": dict(self._global_context_snapshot),
            "local": dict(self._tool_local_context.get(normalized, {})),
        }
        for record in self._surfaces.values():
            if record.source != "plugin" or record.tool_id != normalized:
                continue
            widget = record.dock.widget()
            if widget is None:
                continue
            self._dispatch_context_payload(widget, payload)
        self.main.event_bus.publish(Events.TOOL_CONTEXT_UPDATED, payload)

    def _dispatch_context_payload(self, widget: object, payload: dict[str, Any]) -> None:
        for method_name in (
            "set_tool_context",
            "on_tool_context",
            "set_workstation_context",
            "on_workstation_context",
        ):
            method = getattr(widget, method_name, None)
            if not callable(method):
                continue
            try:
                method(dict(payload))
                return
            except TypeError:
                try:
                    method(dict(payload.get("global", {})))
                    return
                except Exception:
                    continue
            except Exception:
                continue

    def _sync_workstation_context(self, **changes: object) -> None:
        context_runtime = self.main.service_container.get("workstation_context")
        if context_runtime is None:
            return
        try:
            context_runtime.update(**changes)
        except Exception:
            return

    def _notify_tool_group_lifecycle(self, tool_id: str, stage: str) -> None:
        if not tool_id:
            return
        for record in self._surfaces.values():
            if record.source != "plugin" or record.tool_id != tool_id:
                continue
            self._notify_tool_lifecycle(record.dock, stage)

    def _notify_tool_lifecycle(self, dock: QDockWidget, stage: str) -> None:
        widget = dock.widget()
        if widget is None:
            return
        method_names = {
            "activate": ("on_tool_activate", "activate", "on_activate"),
            "deactivate": ("on_tool_deactivate", "deactivate", "on_deactivate"),
            "hide": ("on_tool_hide", "on_hide"),
            "suspend": ("on_tool_suspend", "suspend", "on_suspend"),
            "restore": ("on_tool_restore", "restore", "on_restore"),
            "unload": ("on_tool_unload", "unload", "on_unload"),
            "destroy": ("on_tool_destroy", "destroy", "on_destroy"),
        }.get(stage, ())
        for method_name in method_names:
            method = getattr(widget, method_name, None)
            if callable(method):
                try:
                    method()
                except TypeError:
                    try:
                        method(stage)
                    except Exception:
                        continue
                except Exception:
                    continue
                break

    def _publish_lifecycle_event(
        self,
        tool_id: str,
        *,
        action: str,
        reason: str,
        status: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "tool_id": self._normalize_tool_id(tool_id) if tool_id else "",
            "action": action,
            "reason": reason,
            "status": status,
            "active_tool_id": self._active_tool_id or "",
        }
        if details:
            payload.update(details)
        self.main.event_bus.publish(Events.TOOL_LIFECYCLE_TRANSITION, payload)

    def _publish_invariant_corrected(
        self,
        *,
        reason: str,
        target_tool_id: str,
        visible_tool_ids: list[str],
    ) -> None:
        payload = {
            "reason": reason,
            "active_tool_id": self._active_tool_id or "",
            "target_tool_id": target_tool_id,
            "visible_tool_ids": visible_tool_ids,
        }
        self.main.event_bus.publish(Events.TOOL_INVARIANT_CORRECTED, payload)

    def _enforce_single_active_invariant(self, *, reason: str) -> None:
        if not self._single_active_mode or self._invariant_guard:
            return
        self._invariant_guard = True
        corrected = False
        target = ""
        try:
            plugin_records = [
                record for record in self._surfaces.values() if record.source == "plugin"
            ]
            if not plugin_records:
                return

            enabled_tool_ids = sorted(
                {
                    record.tool_id
                    for record in plugin_records
                    if self._is_tool_enabled(record.tool_id)
                }
            )
            if not enabled_tool_ids:
                if self._active_tool_id:
                    self._clear_active_tool(reason=f"invariant:{reason}")
                    corrected = True
                return

            visible_enabled = sorted(
                {
                    record.tool_id
                    for record in plugin_records
                    if self._is_dock_visible(record.dock) and record.tool_id in enabled_tool_ids
                }
            )
            if self._active_tool_id in enabled_tool_ids:
                target = str(self._active_tool_id)
            elif self._last_active_tool_id in visible_enabled:
                target = str(self._last_active_tool_id)
            elif visible_enabled:
                target = visible_enabled[0]
            elif reason.startswith(("startup", "layout", "reopen", "set-enabled", "destroy")):
                target = enabled_tool_ids[0]
            else:
                if self._active_tool_id:
                    self._clear_active_tool(reason=f"invariant:{reason}")
                    corrected = True
                return

            self._suspend_visibility_events = True
            try:
                for record in plugin_records:
                    should_show = record.tool_id == target
                    is_visible = self._is_dock_visible(record.dock)
                    if should_show and not is_visible:
                        self._notify_tool_lifecycle(record.dock, "restore")
                        self._safe_show(record.dock, raise_after=True)
                        corrected = True
                    elif (not should_show) and is_visible:
                        self._notify_tool_lifecycle(record.dock, "suspend")
                        self._safe_hide(record.dock)
                        corrected = True
            finally:
                self._suspend_visibility_events = False

            if target and self._active_tool_id != target:
                self._set_active_tool(target, reason=f"invariant:{reason}")
                corrected = True
        finally:
            self._invariant_guard = False

        if corrected:
            visible_tool_ids = sorted(
                {
                    record.tool_id
                    for record in self._surfaces.values()
                    if record.source == "plugin" and self._is_dock_visible(record.dock)
                }
            )
            self._publish_invariant_corrected(
                reason=reason,
                target_tool_id=target,
                visible_tool_ids=visible_tool_ids,
            )
