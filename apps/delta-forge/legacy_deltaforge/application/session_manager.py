from __future__ import annotations

import copy
import uuid
from dataclasses import is_dataclass, replace
from types import SimpleNamespace
from typing import Any, Callable

from application.state_machine import derive_idle_state, normalize_state

try:
    from domain.models.session import SessionWorkspace as DomainSessionWorkspace
except Exception:
    DomainSessionWorkspace = None


WorkspaceFactory = Callable[..., Any]


def _clone_workspace(workspace: Any) -> Any:
    try:
        if is_dataclass(workspace):
            return replace(workspace)
        return copy.deepcopy(workspace)
    except Exception:
        return copy.copy(workspace)


class SessionManager:
    def __init__(
        self,
        repository: Any | None = None,
        workspace_factory: WorkspaceFactory | None = None,
    ) -> None:
        self._repository = repository
        self._workspace_factory = workspace_factory or DomainSessionWorkspace or SimpleNamespace
        self._sessions: dict[object, Any] = {}
        self._active_session_id: object | None = None

    @property
    def active_session_id(self) -> object | None:
        return self._active_session_id

    @property
    def session_ids(self) -> tuple[object, ...]:
        return tuple(self._sessions.keys())

    def list_workspaces(self) -> tuple[Any, ...]:
        return tuple(self._sessions.values())

    def has_session(self, session_id: object) -> bool:
        return session_id in self._sessions

    def get(self, session_id: object | None = None) -> Any | None:
        resolved_id = self._active_session_id if session_id is None else session_id
        return self._sessions.get(resolved_id)

    def require(self, session_id: object | None = None) -> Any:
        workspace = self.get(session_id)
        if workspace is None:
            raise KeyError(f"Unknown session_id: {session_id!r}")
        return workspace

    def build_workspace(
        self,
        *,
        session_id: object | None = None,
        initial_state: object | None = "IDLE",
        **extra: Any,
    ) -> Any:
        actual_session_id = session_id or f"session-{uuid.uuid4().hex[:8]}"
        payload: dict[str, Any] = {
            "session_id": actual_session_id,
            "state": normalize_state(initial_state),
            "dirty": False,
            "stale": False,
            "busy": False,
            "results": {},
            "event_feed": [],
            "selection": {},
        }
        payload.update(extra)
        payload["state"] = normalize_state(payload.get("state"))
        return self._instantiate_workspace(payload)

    def add(self, session_id: object, workspace: Any, *, make_active: bool = False) -> Any:
        if session_id in self._sessions:
            raise ValueError(f"Session already exists: {session_id!r}")

        self._sessions[session_id] = workspace
        self._persist_save(session_id, workspace)

        if make_active or self._active_session_id is None:
            self._active_session_id = session_id
            self._persist_active_session(session_id)
        return workspace

    def create(self, session_id: object | None = None, *, make_active: bool = True, **extra: Any) -> Any:
        workspace = self.build_workspace(session_id=session_id, **extra)
        actual_session_id = getattr(workspace, "session_id", session_id)
        return self.add(actual_session_id, workspace, make_active=make_active)

    def update(self, session_id: object, workspace: Any) -> Any:
        if session_id not in self._sessions:
            raise KeyError(f"Unknown session_id: {session_id!r}")

        self._sessions[session_id] = workspace
        self._persist_save(session_id, workspace)
        return workspace

    def mutate(self, session_id: object, mutator: Callable[[Any], Any]) -> Any:
        current = self.require(session_id)
        candidate = _clone_workspace(current)
        updated = mutator(candidate)
        return self.update(session_id, updated)

    def switch(self, session_id: object) -> Any:
        workspace = self.require(session_id)
        self._active_session_id = session_id
        self._persist_active_session(session_id)
        return workspace

    def clone(
        self,
        source_session_id: object,
        *,
        new_session_id: object | None = None,
        make_active: bool = True,
    ) -> Any:
        source = self.require(source_session_id)
        cloned = _clone_workspace(source)
        actual_session_id = new_session_id or f"session-{uuid.uuid4().hex[:8]}"

        setattr(cloned, "session_id", actual_session_id)
        setattr(cloned, "busy", False)
        setattr(
            cloned,
            "state",
            derive_idle_state(bool(getattr(cloned, "dirty", False)), bool(getattr(cloned, "stale", False))),
        )

        return self.add(actual_session_id, cloned, make_active=make_active)

    def close(self, session_id: object) -> Any:
        workspace = self.require(session_id)
        removed = self._sessions.pop(session_id)
        self._persist_delete(session_id)

        if self._active_session_id == session_id:
            self._active_session_id = next(iter(self._sessions), None)
            self._persist_active_session(self._active_session_id)
        return removed

    def _instantiate_workspace(self, payload: dict[str, Any]) -> Any:
        factory = self._workspace_factory

        try:
            return factory(**payload)
        except Exception:
            try:
                instance = factory()
            except Exception:
                instance = SimpleNamespace()

            for key, value in payload.items():
                setattr(instance, key, value)
            return instance

    def _persist_save(self, session_id: object, workspace: Any) -> None:
        self._call_repository(("save_session", "save", "put"), session_id, workspace)

    def _persist_delete(self, session_id: object) -> None:
        self._call_repository(("delete_session", "delete", "remove"), session_id)

    def _persist_active_session(self, session_id: object | None) -> None:
        self._call_repository(("set_active_session", "set_active_session_id"), session_id)

    def _call_repository(self, method_names: tuple[str, ...], *args: Any) -> None:
        if self._repository is None:
            return

        for name in method_names:
            method = getattr(self._repository, name, None)
            if callable(method):
                method(*args)
                return


__all__ = ["SessionManager"]
