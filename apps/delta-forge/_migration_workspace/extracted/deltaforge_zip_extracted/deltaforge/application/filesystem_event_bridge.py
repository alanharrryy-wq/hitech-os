from __future__ import annotations

from typing import Any, Iterable

from application.session_actions import SessionActions
from application.session_manager import SessionManager


def bind_filesystem_changed(
    event_bus: Any,
    session_manager: SessionManager,
    session_actions: SessionActions,
    *,
    workspace_facade: Any | None = None,
    event_name: str = "filesystem_changed",
):
    """Bind Bravo watcher events to Alpha session state using the active session."""

    def _handler(payload: Any) -> Any:
        session_id = _resolve_active_session_id(workspace_facade, session_manager)
        if session_id is None:
            return None
        changed_paths = _extract_changed_paths(payload)
        return session_actions.handle_filesystem_changed(
            session_id,
            changed_paths=changed_paths,
            reason=event_name,
        )

    subscriber = getattr(event_bus, "subscribe", None) or getattr(event_bus, "on", None)
    if not callable(subscriber):
        raise AttributeError("event_bus must expose subscribe(...) or on(...)")
    return subscriber(event_name, _handler)


def _resolve_active_session_id(workspace_facade: Any | None, session_manager: SessionManager) -> object | None:
    if workspace_facade is not None:
        getter = getattr(workspace_facade, "get_active_session_id", None)
        if callable(getter):
            value = getter()
            if value is not None:
                return value
        value = getattr(workspace_facade, "active_session_id", None)
        if value is not None:
            return value
    return session_manager.active_session_id


def _extract_changed_paths(payload: Any) -> tuple[str, ...]:
    if payload is None:
        return ()
    if isinstance(payload, dict):
        path = payload.get("path")
        return (str(path),) if path else ()
    if isinstance(payload, (str, bytes)):
        return (str(payload),)
    if isinstance(payload, Iterable):
        paths: list[str] = []
        for item in payload:
            if isinstance(item, dict):
                path = item.get("path")
                if path:
                    paths.append(str(path))
            elif item is not None:
                paths.append(str(item))
        return tuple(paths)
    return (str(payload),)


__all__ = ["bind_filesystem_changed"]
