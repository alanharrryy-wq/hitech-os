from types import SimpleNamespace

from application.filesystem_event_bridge import bind_filesystem_changed
from application.session_actions import SessionActions
from application.session_manager import SessionManager
from infrastructure.event_bus_in_memory import InMemoryEventBus


def test_bind_filesystem_changed_routes_to_active_session() -> None:
    manager = SessionManager(workspace_factory=SimpleNamespace)
    actions = SessionActions(manager)
    actions.create_session(
        session_id="s-1",
        workspace=SimpleNamespace(
            session_id="s-1",
            state="IDLE",
            dirty=False,
            stale=False,
            busy=False,
            results={},
            event_feed=[],
            selection={},
        ),
        make_active=True,
    )

    bus = InMemoryEventBus()
    unsubscribe = bind_filesystem_changed(bus, manager, actions)
    bus.emit("filesystem_changed", [{"path": "a.py"}, {"path": "b.py"}])

    current = manager.require("s-1")
    assert current.stale is True
    assert current.event_feed[-1]["payload"]["changed_paths"] == ("a.py", "b.py")
    unsubscribe()
