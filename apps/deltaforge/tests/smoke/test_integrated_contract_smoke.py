from __future__ import annotations

from types import SimpleNamespace

from deltaforge.application.controllers.ui_command_controller import UiCommandController
from deltaforge.application.session_actions import SessionActions
from deltaforge.application.session_manager import SessionManager
from deltaforge.application.workspace_facade import WorkspaceFacade
from deltaforge.infrastructure.event_bus_in_memory import InMemoryEventBus



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
