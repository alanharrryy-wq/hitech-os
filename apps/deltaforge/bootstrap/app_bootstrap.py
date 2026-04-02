from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, Sequence

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import QApplication

from application.controllers.ui_command_controller import UiCommandController
from application.session_actions import SessionActions
from application.session_manager import SessionManager
from application.workspace_facade import WorkspaceFacade
from bootstrap.event_wiring import wire_optional_filesystem_bridge
from bootstrap.resolver_bridge import resolve_command_controller, resolve_workspace_facade
from infrastructure.event_bus_in_memory import InMemoryEventBus
from ui.theme import apply_theme
from ui.window.main_window import DeltaForgeMainWindow, WindowBindings


class DependencyResolverLike(Protocol):
    def create_workspace_facade(self) -> Any: ...
    def create_command_controller(self, workspace_facade: Any) -> Any: ...


@dataclass(slots=True)
class BootstrapConfig:
    organization_name: str = 'HITECH'
    application_name: str = 'DeltaForge'
    theme_name: str = 'dark'
    argv: Sequence[str] | None = None



def create_application(config: BootstrapConfig | None = None) -> QApplication:
    config = config or BootstrapConfig()
    QCoreApplication.setOrganizationName(config.organization_name)
    QCoreApplication.setApplicationName(config.application_name)
    app = QApplication.instance()
    if app is not None:
        return app
    return QApplication(list(config.argv or []))



def build_main_window(
    *,
    workspace_facade: Any,
    command_controller: Any,
    config: BootstrapConfig | None = None,
) -> DeltaForgeMainWindow:
    config = config or BootstrapConfig()
    app = create_application(config)
    window = DeltaForgeMainWindow(
        WindowBindings(
            workspace_facade=workspace_facade,
            command_controller=command_controller,
            initial_theme=config.theme_name,
        )
    )
    apply_theme(app, window, config.theme_name)
    return window



def build_from_resolver(
    resolver: DependencyResolverLike,
    config: BootstrapConfig | None = None,
) -> DeltaForgeMainWindow:
    workspace_facade = resolve_workspace_facade(resolver)
    command_controller = resolve_command_controller(resolver, workspace_facade)
    wire_optional_filesystem_bridge(resolver, workspace_facade=workspace_facade)
    return build_main_window(
        workspace_facade=workspace_facade,
        command_controller=command_controller,
        config=config,
    )



def bootstrap(
    *,
    workspace_facade: Any,
    command_controller: Any,
    config: BootstrapConfig | None = None,
) -> int:
    app = create_application(config)
    window = build_main_window(
        workspace_facade=workspace_facade,
        command_controller=command_controller,
        config=config,
    )
    window.show()
    return app.exec()


def run(config: BootstrapConfig | None = None) -> int:
    manager = SessionManager()
    event_bus = InMemoryEventBus()
    actions = SessionActions(manager, event_bus=event_bus)
    facade = WorkspaceFacade(manager)
    controller = UiCommandController(manager, actions, facade)
    actions.create_session(make_active=True)
    return bootstrap(
        workspace_facade=facade,
        command_controller=controller,
        config=config,
    )
