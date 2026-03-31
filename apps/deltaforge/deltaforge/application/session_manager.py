from __future__ import annotations

from dataclasses import dataclass
from itertools import count

from deltaforge.domain.models import ScopeSelection, SessionWorkspace
from deltaforge.domain.session_states import SessionState


@dataclass(slots=True)
class SessionCollection:
    ordered_ids: list[str]
    by_id: dict[str, SessionWorkspace]
    current_session_id: str = ""


class SessionManager:
    def __init__(self) -> None:
        self._counter = count(1)
        self._sessions = SessionCollection(ordered_ids=[], by_id={})

    @property
    def current_session_id(self) -> str:
        return self._sessions.current_session_id

    @property
    def sessions(self) -> list[SessionWorkspace]:
        return [self._sessions.by_id[item] for item in self._sessions.ordered_ids]

    def current(self) -> SessionWorkspace | None:
        if not self._sessions.current_session_id:
            return None
        return self._sessions.by_id.get(self._sessions.current_session_id)

    def get(self, session_id: str) -> SessionWorkspace | None:
        return self._sessions.by_id.get(session_id)

    def create_session(self, title: str = "") -> SessionWorkspace:
        session_number = next(self._counter)
        session_id = f"s{session_number:03d}"
        resolved_title = title or f"Session {session_number}"

        session = SessionWorkspace(session_id=session_id, title=resolved_title)
        self._sessions.by_id[session_id] = session
        self._sessions.ordered_ids.append(session_id)
        self._sessions.current_session_id = session_id
        return session

    def clone_session(self, source_session_id: str) -> SessionWorkspace | None:
        source = self.get(source_session_id)
        if source is None:
            return None

        session_number = next(self._counter)
        cloned_id = f"s{session_number:03d}"
        cloned_title = f"Session {session_number}"
        cloned = source.clone_for_new_session(session_id=cloned_id, title=cloned_title)

        self._sessions.by_id[cloned_id] = cloned
        self._sessions.ordered_ids.append(cloned_id)
        self._sessions.current_session_id = cloned_id
        return cloned

    def activate(self, session_id: str) -> SessionWorkspace | None:
        session = self.get(session_id)
        if session is None:
            return None
        self._sessions.current_session_id = session_id
        return session

    def close_session(self, session_id: str) -> SessionWorkspace | None:
        if session_id not in self._sessions.by_id:
            return None

        self._sessions.by_id.pop(session_id)
        self._sessions.ordered_ids = [item for item in self._sessions.ordered_ids if item != session_id]

        if not self._sessions.ordered_ids:
            self._sessions.current_session_id = ""
            return None

        if self._sessions.current_session_id == session_id:
            self._sessions.current_session_id = self._sessions.ordered_ids[-1]

        return self._sessions.by_id[self._sessions.current_session_id]

    def update_scope(self, session_id: str, targets: list[str], root_dir: str) -> SessionWorkspace | None:
        session = self.get(session_id)
        if session is None:
            return None

        session.scope = ScopeSelection(targets=targets, root_dir=root_dir)
        session.stale = False
        session.dirty = False
        session.state = SessionState.SCOPE_LOADED if targets else SessionState.EMPTY
        return session

    def clear_scope(self, session_id: str) -> SessionWorkspace | None:
        session = self.get(session_id)
        if session is None:
            return None

        session.scope.clear()
        session.state = SessionState.EMPTY
        session.stale = False
        session.dirty = False
        return session

    def set_state(self, session_id: str, state: SessionState) -> SessionWorkspace | None:
        session = self.get(session_id)
        if session is None:
            return None
        session.state = state
        return session

    def mark_stale(self, session_id: str) -> SessionWorkspace | None:
        session = self.get(session_id)
        if session is None:
            return None
        session.stale = True
        session.dirty = True
        session.state = SessionState.DIRTY_OR_STALE
        return session
