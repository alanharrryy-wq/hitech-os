from __future__ import annotations

from typing import Any

from application.filesystem_event_bridge import bind_filesystem_changed
from bootstrap.resolver_bridge import resolve_optional



def wire_optional_filesystem_bridge(resolver: Any, *, workspace_facade: Any | None = None) -> bool:
    event_bus = resolve_optional(resolver, 'event_bus', 'create_event_bus')
    session_manager = resolve_optional(resolver, 'session_manager', 'create_session_manager')
    session_actions = resolve_optional(resolver, 'session_actions', 'create_session_actions')

    if event_bus is None or session_manager is None or session_actions is None:
        return False

    bind_filesystem_changed(
        event_bus,
        session_manager,
        session_actions,
        workspace_facade=workspace_facade,
    )
    return True
