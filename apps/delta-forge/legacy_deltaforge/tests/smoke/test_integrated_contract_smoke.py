from __future__ import annotations

from types import SimpleNamespace

from application.controllers.ui_command_controller import UiCommandController
from application.session_actions import SessionActions
from application.session_manager import SessionManager
from application.workspace_facade import WorkspaceFacade
from infrastructure.event_bus_in_memory import InMemoryEventBus



def test_integrated_alpha_bravo_charlie_contracts_line_up() -> None:
    manager = SessionManager(workspace_factory=SimpleNamespace)
    bus = InMemoryEventBus()
    actions = SessionActions(manager, event_bus=bus)
    facade = WorkspaceFacade(manager)
    controller = UiCommandController(manager, actions, facade)

    controller.create_session()
    active = facade.get_active_session_id()
    assert active is not None

    command_bar = facade.get_command_bar_projection(active)
    workspace = facade.get_workspace_projection(active)

    assert 'root_dir' in command_bar
    assert 'busy' in command_bar
    assert 'targets' in workspace
    assert 'ops' in workspace
    assert 'results' in workspace


def test_close_last_session_keeps_active_session() -> None:
    manager = SessionManager(workspace_factory=SimpleNamespace)
    bus = InMemoryEventBus()
    actions = SessionActions(manager, event_bus=bus)
    facade = WorkspaceFacade(manager)
    controller = UiCommandController(manager, actions, facade)

    controller.create_session()
    active = facade.get_active_session_id()
    assert active is not None

    assert controller.close_session(active) is True
    assert facade.get_active_session_id() is not None
    assert len(facade.get_session_tabs_projection()) == 1


def test_browse_root_dir_updates_scope_projection(tmp_path) -> None:
    manager = SessionManager(workspace_factory=SimpleNamespace)
    bus = InMemoryEventBus()
    actions = SessionActions(manager, event_bus=bus)
    facade = WorkspaceFacade(manager)
    controller = UiCommandController(
        manager,
        actions,
        facade,
        directory_picker=lambda **_: str(tmp_path),
    )

    controller.create_session()
    assert controller.browse_root_dir() is True

    active = facade.get_active_session_id()
    assert active is not None
    command_bar = facade.get_command_bar_projection(active)
    scope = facade.get_scope_projection(active)

    assert command_bar["root_dir"] == str(tmp_path)
    assert scope["path"] == str(tmp_path)
