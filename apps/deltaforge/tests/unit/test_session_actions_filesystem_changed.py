from types import SimpleNamespace

from application.session_actions import SessionActions
from application.session_manager import SessionManager


def test_handle_filesystem_changed_marks_session_stale() -> None:
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
    )

    updated = actions.handle_filesystem_changed("s-1", changed_paths=["a.py", "b.py"])

    assert updated.stale is True
    assert updated.state == "DIRTY_OR_STALE"
    assert updated.event_feed[-1]["name"] == "filesystem_changed"
    assert updated.event_feed[-1]["payload"]["changed_paths"] == ("a.py", "b.py")
