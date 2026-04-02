from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from application.refresh_policy import build_refresh_decision
from application.selection_service import selection_snapshot
from application.session_manager import SessionManager
from application.state_machine import normalize_state


@dataclass(frozen=True, slots=True)
class WorkspaceStatus:
    session_id: object | None
    root_dir: str
    target_count: int
    state: str
    current_mode: str
    dirty: bool
    stale: bool
    busy: bool


@dataclass(frozen=True, slots=True)
class WorkspaceSelection:
    targets: tuple[Any, ...]
    op: Any | None
    detail: Any | None
    surface: str
    view: str


@dataclass(frozen=True, slots=True)
class WorkspaceSnapshot:
    session_id: object | None
    status: WorkspaceStatus
    selection: WorkspaceSelection
    results: dict[str, Any]
    event_feed: tuple[Any, ...]
    can_refresh: bool


class WorkspaceFacade:
    _DEFAULT_SURFACES = ("events", "validation", "plan", "apply", "rollback")

    def __init__(self, manager: SessionManager) -> None:
        self._manager = manager

    @property
    def active_session_id(self) -> object | None:
        return self._manager.active_session_id

    def get_active_session_id(self) -> object | None:
        return self.active_session_id

    def session_ids(self) -> tuple[object, ...]:
        return self._manager.session_ids

    def snapshot(self, session_id: object | None = None) -> WorkspaceSnapshot:
        workspace = self._manager.require(session_id)
        status = self.status(session_id)
        selection = self.selection(session_id)
        results = self.results_surfaces(session_id)
        event_feed = tuple(getattr(workspace, "event_feed", ()) or ())
        can_refresh = build_refresh_decision(workspace).should_refresh

        return WorkspaceSnapshot(
            session_id=getattr(workspace, "session_id", None),
            status=status,
            selection=selection,
            results=results,
            event_feed=event_feed,
            can_refresh=can_refresh,
        )

    def active_snapshot(self) -> WorkspaceSnapshot:
        return self.snapshot(self._manager.active_session_id)

    def status(self, session_id: object | None = None) -> WorkspaceStatus:
        workspace = self._manager.require(session_id)
        scope = getattr(workspace, "scope", None)
        selection = selection_snapshot(workspace)

        return WorkspaceStatus(
            session_id=getattr(workspace, "session_id", None),
            root_dir=self._scope_root_dir(scope),
            target_count=self._target_count(workspace, scope),
            state=normalize_state(getattr(workspace, "state", "IDLE")),
            current_mode=str(selection.get("view") or "workspace"),
            dirty=bool(getattr(workspace, "dirty", False)),
            stale=bool(getattr(workspace, "stale", False)),
            busy=bool(getattr(workspace, "busy", False)),
        )

    def selection(self, session_id: object | None = None) -> WorkspaceSelection:
        workspace = self._manager.require(session_id)
        current = selection_snapshot(workspace)

        return WorkspaceSelection(
            targets=tuple(current.get("targets", ()) or ()),
            op=current.get("op"),
            detail=current.get("detail"),
            surface=str(current.get("surface") or "events"),
            view=str(current.get("view") or "workspace"),
        )

    def results_surfaces(self, session_id: object | None = None) -> dict[str, Any]:
        workspace = self._manager.require(session_id)
        current = getattr(workspace, "results", None)
        surfaces = {name: None for name in self._DEFAULT_SURFACES}

        if isinstance(current, Mapping):
            surfaces.update(dict(current))

        surfaces["events"] = tuple(getattr(workspace, "event_feed", ()) or ())
        return surfaces

    def status_bar_payload(self, session_id: object | None = None) -> dict[str, Any]:
        status = self.status(session_id)
        return {
            "session_id": status.session_id,
            "root_dir": status.root_dir,
            "target_count": status.target_count,
            "session_state": status.state,
            "state": status.state,
            "current_mode": status.current_mode,
            "mode": status.current_mode,
            "dirty": status.dirty,
            "stale": status.stale,
            "dirty_or_stale": status.dirty or status.stale,
            "busy": status.busy,
        }

    def get_status_projection(self, session_id: object | None = None) -> dict[str, Any]:
        return self.status_bar_payload(session_id)

    def get_session_tabs_projection(self) -> list[dict[str, Any]]:
        sessions: list[dict[str, Any]] = []
        active_session_id = self._manager.active_session_id

        for workspace in self._manager.list_workspaces():
            session_id = getattr(workspace, "session_id", None)
            state = normalize_state(getattr(workspace, "state", "IDLE"))
            dirty = bool(getattr(workspace, "dirty", False))
            stale = bool(getattr(workspace, "stale", False))
            root_dir = self._scope_root_dir(getattr(workspace, "scope", None))
            title = str(getattr(workspace, "title", None) or session_id or "Session")
            sessions.append(
                {
                    "id": session_id,
                    "session_id": session_id,
                    "title": title,
                    "name": title,
                    "badge": self._session_badge(workspace),
                    "state": state,
                    "dirty": dirty,
                    "stale": stale,
                    "tooltip": root_dir or state,
                    "current": session_id == active_session_id,
                    "closable": True,
                }
            )

        return sessions

    def get_command_bar_projection(self, session_id: object | None = None) -> dict[str, Any]:
        workspace = self._manager.require(session_id)
        status = self.get_status_projection(session_id)
        mode = str(status.get("current_mode") or "workspace")
        has_scope = bool(self._target_count(workspace, getattr(workspace, "scope", None)) or status["root_dir"])
        has_ops = bool(self._project_mapping(getattr(workspace, "ops_document", None)).get("content") or self._project_ops(getattr(workspace, "ops_document", None)))
        results = self.results_surfaces(session_id)
        busy = bool(status["busy"])

        return {
            "root_dir": status["root_dir"],
            "mode_label": mode,
            "mode": mode,
            "busy": busy,
            "session_id": status["session_id"],
            "session_state": status["session_state"],
            "actions": {
                "create_session": {"enabled": True},
                "close_session": {"enabled": status["session_id"] is not None},
                "select_session": {"enabled": True},
                "browse_root_dir": {"enabled": not busy},
                "validate_active": {"enabled": has_scope and has_ops and not busy},
                "plan_active": {"enabled": has_scope and has_ops and not busy},
                "apply_active": {"enabled": bool(results.get("plan")) and not busy},
                "rollback_active": {"enabled": bool(results.get("apply")) and not busy},
                "refresh_active": {"enabled": not busy},
                "select_op": {"enabled": True},
                "select_target": {"enabled": True},
            },
        }

    def get_scope_projection(self, session_id: object | None = None) -> dict[str, Any]:
        workspace = self._manager.require(session_id)
        scope = getattr(workspace, "scope", None)
        targets = tuple(getattr(workspace, "targets", None) or getattr(scope, "resolved_paths", None) or ())
        watch_paths = tuple(getattr(scope, "watch_paths", None) or ())

        return {
            "kind": self._mapping_value(scope, "kind"),
            "path": self._scope_root_dir(scope),
            "source": self._mapping_value(scope, "source"),
            "summary": f"{len(targets)} target(s)",
            "targets": [self._target_item(value) for value in targets],
            "watch_paths": [self._target_item(value) for value in watch_paths],
            "metadata": {
                "target_count": len(targets),
                "dirty": bool(getattr(workspace, "dirty", False)),
                "stale": bool(getattr(workspace, "stale", False)),
                "busy": bool(getattr(workspace, "busy", False)),
            },
        }

    def get_workspace_projection(self, session_id: object | None = None) -> dict[str, Any]:
        workspace = self._manager.require(session_id)
        selection = selection_snapshot(workspace)
        results = self.results_surfaces(session_id)
        scope_projection = self.get_scope_projection(session_id)
        ops_items = self._project_ops(getattr(workspace, "ops_document", None))
        grouped_preview = self._project_grouped_preview(results.get("plan"), results.get("diff"))
        detail = selection.get("detail") or self._project_mapping(results.get("plan")).get("summary") or None

        return {
            # widget compatibility keys consumed today by Charlie
            "targets": scope_projection["targets"],
            "ops": ops_items,
            "grouped_preview": grouped_preview,
            "detail": detail,
            "results": results,
            # richer projections for future consumers
            "status": self.get_status_projection(session_id),
            "sessions": self.get_session_tabs_projection(),
            "command_bar": self.get_command_bar_projection(session_id),
            "scope": scope_projection,
            "selection": selection,
            "ops_document": self._project_mapping(getattr(workspace, "ops_document", None)),
            "plan": self._project_surface(results.get("plan")),
            "diff": self._project_surface(results.get("diff") or results.get("plan")),
        }

    def _target_count(self, workspace: Any, scope: Any) -> int:
        targets = getattr(workspace, "targets", None)
        if targets is not None:
            return len(tuple(targets))

        if scope is None:
            return 0

        resolved_paths = getattr(scope, "resolved_paths", None)
        if resolved_paths is not None:
            return len(tuple(resolved_paths))

        watch_paths = getattr(scope, "watch_paths", None)
        if watch_paths is not None:
            return len(tuple(watch_paths))

        return 0

    def _scope_root_dir(self, scope: Any) -> str:
        if scope is None:
            return ""

        for attr_name in ("root_dir", "source", "path"):
            value = getattr(scope, attr_name, "") if not isinstance(scope, Mapping) else scope.get(attr_name, "")
            if value:
                return str(value)
        return ""

    def _session_badge(self, workspace: Any) -> str | None:
        if bool(getattr(workspace, "busy", False)):
            return "busy"
        if bool(getattr(workspace, "dirty", False)):
            return "dirty"
        if bool(getattr(workspace, "stale", False)):
            return "stale"
        return None

    def _target_item(self, value: Any) -> dict[str, Any]:
        if isinstance(value, Mapping):
            payload = dict(value)
            label = payload.get("label") or payload.get("path") or payload.get("name") or payload.get("id") or value
            payload.setdefault("label", str(label))
            return payload
        return {"label": str(value), "path": str(value)}

    def _project_surface(self, value: Any) -> dict[str, Any]:
        projected = self._project_mapping(value)
        if "summary" not in projected and "text" in projected:
            projected["summary"] = projected.get("status") or projected.get("text") or ""
        return projected

    def _project_mapping(self, value: Any) -> dict[str, Any]:
        if isinstance(value, Mapping):
            return dict(value)
        if value is None:
            return {}
        return {
            key: getattr(value, key)
            for key in ("id", "title", "status", "hint", "content", "text", "raw_text", "summary", "items", "files", "groups", "ops")
            if hasattr(value, key)
        }

    def _project_ops(self, value: Any) -> list[dict[str, Any] | str]:
        mapped = self._project_mapping(value)
        for key in ("ops", "items"):
            candidate = mapped.get(key)
            if isinstance(candidate, list):
                return list(candidate)
            if isinstance(candidate, tuple):
                return list(candidate)
        if mapped.get("content"):
            return [{"label": "ops_document", "summary": str(mapped.get("summary") or "loaded"), "content": mapped.get("content")}]
        if mapped.get("text") or mapped.get("raw_text"):
            text = str(mapped.get("text") or mapped.get("raw_text"))
            return [{"label": "ops_document", "summary": text[:120], "content": text}]
        return []

    def _project_grouped_preview(self, *payloads: Any) -> list[dict[str, Any]]:
        for payload in payloads:
            mapped = self._project_mapping(payload)
            candidate = mapped.get("grouped_preview") or mapped.get("groups")
            if isinstance(candidate, list):
                return list(candidate)
            items = mapped.get("items")
            if isinstance(items, list) and items:
                return [{"label": mapped.get("title") or mapped.get("summary") or "Preview", "summary": mapped.get("summary") or "", "items": items}]
            files = mapped.get("files")
            if isinstance(files, list) and files:
                return [{"label": mapped.get("title") or "Files", "summary": mapped.get("summary") or "", "items": files}]
        return []

    def _mapping_value(self, value: Any, key: str) -> str:
        if value is None:
            return ""
        raw = value.get(key, "") if isinstance(value, Mapping) else getattr(value, key, "")
        return "" if raw in (None, "") else str(raw)


__all__ = [
    "WorkspaceFacade",
    "WorkspaceSelection",
    "WorkspaceSnapshot",
    "WorkspaceStatus",
]
