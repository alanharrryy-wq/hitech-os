from types import SimpleNamespace

from application.session_manager import SessionManager
from application.workspace_facade import WorkspaceFacade


def _workspace(**overrides):
    base = {
        "session_id": "s-1",
        "state": "DIRTY_OR_STALE",
        "dirty": True,
        "stale": False,
        "busy": False,
        "results": {},
        "event_feed": [],
        "selection": {"view": "workspace", "surface": "events"},
        "scope": SimpleNamespace(
            kind="multi_file",
            root_dir="F:/repos/hitech-os/apps/deltaforge",
            source="picker",
            resolved_paths=("a.py", "b.py"),
            watch_paths=("F:/repos/hitech-os/apps/deltaforge",),
        ),
        "ops_document": {"content": '{"ops": []}', "items": [{"label": "validate"}]},
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_workspace_facade_exposes_widget_compatible_projections() -> None:
    manager = SessionManager(workspace_factory=SimpleNamespace)
    manager.add("s-1", _workspace(), make_active=True)

    facade = WorkspaceFacade(manager)

    tabs = facade.get_session_tabs_projection()
    command_bar = facade.get_command_bar_projection("s-1")
    workspace = facade.get_workspace_projection("s-1")

    assert tabs[0]["session_id"] == "s-1"
    assert tabs[0]["current"] is True
    assert command_bar["root_dir"].endswith("deltaforge")
    assert command_bar["mode"] == "workspace"
    assert command_bar["busy"] is False
    assert isinstance(workspace["targets"], list)
    assert isinstance(workspace["ops"], list)
    assert "grouped_preview" in workspace
    assert "results" in workspace
