from types import SimpleNamespace

from application.session_actions import SessionActions
from application.session_manager import SessionManager


def test_session_actions_update_selection_and_results() -> None:
    manager = SessionManager(workspace_factory=SimpleNamespace)
    actions = SessionActions(manager)

    actions.create_session(session_id="s-1")
    actions.update_selection("s-1", targets=["alpha.py"], surface="plan", view="diff")
    actions.set_results("s-1", "plan", {"files": 1})

    current = manager.require("s-1")

    assert current.selection["targets"] == ("alpha.py",)
    assert current.selection["surface"] == "plan"
    assert current.selection["view"] == "diff"
    assert current.results["plan"] == {"files": 1}
    assert current.event_feed[-1]["name"] == "session.results.updated"
