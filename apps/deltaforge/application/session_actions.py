from __future__ import annotations

from typing import Any

from application.refresh_policy import (
    begin_refresh as apply_refresh_begin,
    build_refresh_decision,
    fail_refresh as apply_refresh_fail,
    finish_refresh as apply_refresh_finish,
)
from application.selection_service import clear_selection, replace_selection
from application.session_manager import SessionManager
from application.state_machine import assert_transition, derive_idle_state, normalize_state
from application.stale_policy import (
    clear_dirty,
    clear_dirty_and_stale,
    clear_stale,
    mark_dirty,
    mark_stale,
)


class SessionActions:
    def __init__(self, manager: SessionManager, event_bus: Any | None = None) -> None:
        self._manager = manager
        self._event_bus = event_bus

    def create_session(
        self,
        session_id: object | None = None,
        *,
        workspace: Any | None = None,
        make_active: bool = True,
        **extra: Any,
    ) -> Any:
        created = workspace or self._manager.build_workspace(session_id=session_id, **extra)
        actual_session_id = getattr(created, "session_id", session_id)
        created = self._append_event(created, "session.created", {"session_id": actual_session_id})
        self._manager.add(actual_session_id, created, make_active=make_active)
        self._emit("session.created", {"session_id": actual_session_id})
        return created

    def clone_session(
        self,
        source_session_id: object,
        *,
        new_session_id: object | None = None,
        make_active: bool = True,
    ) -> Any:
        cloned = self._manager.clone(source_session_id, new_session_id=new_session_id, make_active=make_active)
        actual_session_id = getattr(cloned, "session_id", new_session_id)
        updated = self._manager.mutate(
            actual_session_id,
            lambda ws: self._append_event(ws, "session.cloned", {"source_session_id": source_session_id}),
        )
        self._emit(
            "session.cloned",
            {"session_id": actual_session_id, "source_session_id": source_session_id},
        )
        return updated

    def activate_session(self, session_id: object) -> Any:
        workspace = self._manager.switch(session_id)
        self._emit("session.activated", {"session_id": session_id})
        return workspace

    def close_session(self, session_id: object) -> Any:
        workspace = self._manager.require(session_id)
        workspace = self._append_event(workspace, "session.closed", {"session_id": session_id})
        self._emit("session.closed", {"session_id": session_id})
        self._manager.update(session_id, workspace)
        return self._manager.close(session_id)

    def set_scope(self, session_id: object, scope: Any) -> Any:
        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(self._assign(ws, scope=scope), "session.scope.updated", {}),
        )
        self._emit("session.scope.updated", {"session_id": session_id})
        return updated

    def set_ops_document(self, session_id: object, ops_document: Any, *, mark_as_dirty: bool = False) -> Any:
        def mutator(ws: Any) -> Any:
            assigned = self._assign(ws, ops_document=ops_document)
            if mark_as_dirty:
                assigned = mark_dirty(assigned)
            return self._append_event(assigned, "session.ops.updated", {"mark_as_dirty": mark_as_dirty})

        updated = self._manager.mutate(session_id, mutator)
        self._emit("session.ops.updated", {"session_id": session_id, "mark_as_dirty": mark_as_dirty})
        return updated

    def mark_dirty(self, session_id: object, *, reason: str = "ops_changed") -> Any:
        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(mark_dirty(ws), "session.marked_dirty", {"reason": reason}),
        )
        self._emit("session.marked_dirty", {"session_id": session_id, "reason": reason})
        return updated

    def mark_stale(self, session_id: object, *, reason: str = "watcher_changed") -> Any:
        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(mark_stale(ws), "session.marked_stale", {"reason": reason}),
        )
        self._emit("session.marked_stale", {"session_id": session_id, "reason": reason})
        return updated

    def handle_filesystem_changed(
        self,
        session_id: object,
        *,
        changed_paths: tuple[object, ...] | list[object] = (),
        reason: str = "filesystem_changed",
    ) -> Any:
        payload = {"reason": reason, "changed_paths": tuple(changed_paths)}
        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(mark_stale(ws), "filesystem_changed", payload),
        )
        self._emit("filesystem_changed", {"session_id": session_id, **payload})
        return updated

    def clear_dirty(self, session_id: object) -> Any:
        return self._manager.mutate(
            session_id,
            lambda ws: self._append_event(clear_dirty(ws), "session.dirty.cleared", {}),
        )

    def clear_stale(self, session_id: object) -> Any:
        return self._manager.mutate(
            session_id,
            lambda ws: self._append_event(clear_stale(ws), "session.stale.cleared", {}),
        )

    def clear_dirty_and_stale(self, session_id: object) -> Any:
        return self._manager.mutate(
            session_id,
            lambda ws: self._append_event(clear_dirty_and_stale(ws), "session.flags.cleared", {}),
        )

    def start_run(self, session_id: object, target_state: object) -> Any:
        target_name = normalize_state(target_state)

        def mutator(ws: Any) -> Any:
            current_state = getattr(ws, "state", "IDLE")
            setattr(ws, "state", assert_transition(current_state, target_name))
            setattr(ws, "busy", True)
            return self._append_event(ws, "session.run.started", {"target_state": target_name})

        updated = self._manager.mutate(session_id, mutator)
        self._emit("session.run.started", {"session_id": session_id, "target_state": target_name})
        return updated

    def complete_run(
        self,
        session_id: object,
        *,
        surface: str | None = None,
        result: Any | None = None,
    ) -> Any:
        def mutator(ws: Any) -> Any:
            if surface is not None:
                results = self._results_mapping(ws)
                results[surface] = result
                setattr(ws, "results", results)

            setattr(ws, "busy", False)
            setattr(
                ws,
                "state",
                derive_idle_state(bool(getattr(ws, "dirty", False)), bool(getattr(ws, "stale", False))),
            )
            return self._append_event(ws, "session.run.completed", {"surface": surface})

        updated = self._manager.mutate(session_id, mutator)
        self._emit("session.run.completed", {"session_id": session_id, "surface": surface})
        return updated

    def fail_run(self, session_id: object, *, error: object | None = None) -> Any:
        def mutator(ws: Any) -> Any:
            setattr(ws, "busy", False)
            setattr(ws, "state", "FAILED")
            if error is not None:
                setattr(ws, "last_error", str(error))
            return self._append_event(ws, "session.run.failed", {"error": None if error is None else str(error)})

        updated = self._manager.mutate(session_id, mutator)
        self._emit("session.run.failed", {"session_id": session_id, "error": None if error is None else str(error)})
        return updated

    def begin_refresh(self, session_id: object, *, force: bool = False) -> Any:
        current = self._manager.require(session_id)
        decision = build_refresh_decision(current, force=force)

        if not decision.should_refresh:
            return current

        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(
                apply_refresh_begin(ws, force=force),
                "session.refresh.started",
                {"reason": decision.reason, "force": force},
            ),
        )
        self._emit(
            "session.refresh.started",
            {"session_id": session_id, "reason": decision.reason, "force": force},
        )
        return updated

    def finish_refresh(
        self,
        session_id: object,
        *,
        refreshed_scope: Any | None = None,
        refreshed_results: Any | None = None,
    ) -> Any:
        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(
                apply_refresh_finish(
                    ws,
                    refreshed_scope=refreshed_scope,
                    refreshed_results=refreshed_results,
                ),
                "session.refresh.completed",
                {},
            ),
        )
        self._emit("session.refresh.completed", {"session_id": session_id})
        return updated

    def fail_refresh(self, session_id: object, *, error: object | None = None) -> Any:
        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(
                apply_refresh_fail(ws, error=error),
                "session.refresh.failed",
                {"error": None if error is None else str(error)},
            ),
        )
        self._emit("session.refresh.failed", {"session_id": session_id, "error": None if error is None else str(error)})
        return updated

    def update_selection(self, session_id: object, **updates: Any) -> Any:
        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(
                replace_selection(ws, **updates),
                "session.selection.changed",
                {"keys": tuple(sorted(updates.keys()))},
            ),
        )
        self._emit("session.selection.changed", {"session_id": session_id, "keys": tuple(sorted(updates.keys()))})
        return updated

    def clear_selection(self, session_id: object) -> Any:
        updated = self._manager.mutate(
            session_id,
            lambda ws: self._append_event(clear_selection(ws), "session.selection.cleared", {}),
        )
        self._emit("session.selection.cleared", {"session_id": session_id})
        return updated

    def set_results(self, session_id: object, surface: str, value: Any) -> Any:
        def mutator(ws: Any) -> Any:
            results = self._results_mapping(ws)
            results[surface] = value
            setattr(ws, "results", results)
            return self._append_event(ws, "session.results.updated", {"surface": surface})

        updated = self._manager.mutate(session_id, mutator)
        self._emit("session.results.updated", {"session_id": session_id, "surface": surface})
        return updated

    def clear_results(self, session_id: object, *, surfaces: tuple[str, ...] | None = None) -> Any:
        def mutator(ws: Any) -> Any:
            if surfaces is None:
                setattr(ws, "results", {})
            else:
                results = self._results_mapping(ws)
                for surface_name in surfaces:
                    results.pop(surface_name, None)
                setattr(ws, "results", results)
            return self._append_event(ws, "session.results.cleared", {"surfaces": surfaces})

        updated = self._manager.mutate(session_id, mutator)
        self._emit("session.results.cleared", {"session_id": session_id, "surfaces": surfaces})
        return updated

    def _assign(self, workspace: Any, **updates: Any) -> Any:
        for key, value in updates.items():
            setattr(workspace, key, value)
        return workspace

    def _results_mapping(self, workspace: Any) -> dict[str, Any]:
        current = getattr(workspace, "results", None)
        return dict(current) if isinstance(current, dict) else {}

    def _append_event(self, workspace: Any, name: str, payload: dict[str, Any]) -> Any:
        current_feed = getattr(workspace, "event_feed", None)
        feed = list(current_feed) if isinstance(current_feed, (list, tuple)) else []
        feed.append(
            {
                "name": name,
                "session_id": getattr(workspace, "session_id", None),
                "payload": payload,
            }
        )
        setattr(workspace, "event_feed", feed)
        return workspace

    def _emit(self, name: str, payload: dict[str, Any]) -> None:
        if self._event_bus is None:
            return

        for method_name in ("emit", "publish", "dispatch"):
            method = getattr(self._event_bus, method_name, None)
            if not callable(method):
                continue

            try:
                method(name, payload)
                return
            except TypeError:
                try:
                    method(payload)
                    return
                except TypeError:
                    continue


__all__ = ["SessionActions"]
