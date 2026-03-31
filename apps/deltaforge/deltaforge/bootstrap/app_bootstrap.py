from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from deltaforge.application.session_manager import SessionManager
from deltaforge.infrastructure import EventBus, FileWatcherService, SettingsStore
from deltaforge.infrastructure.adapters import MockEngineAdapter
from deltaforge.ui.theme import build_app_stylesheet, build_default_theme
from deltaforge.ui.window import DeltaForgeMainWindow


def ensure_app() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv[:1])
        app.setApplicationName("DeltaForge")
        app.setOrganizationName("HITECH-OS")
    return app


def run() -> int:
    app = ensure_app()

    settings_store = SettingsStore()
    settings = settings_store.load()

    theme = build_default_theme()
    app.setStyleSheet(build_app_stylesheet(theme))

    manager = SessionManager()
    bus = EventBus()
    watcher = FileWatcherService(bus, manager)
    engine = MockEngineAdapter()

    window = DeltaForgeMainWindow(
        manager=manager,
        event_bus=bus,
        watcher=watcher,
        engine=engine,
        initial_size=(settings.window_width, settings.window_height),
    )
    window.show()

    exit_code = app.exec()

    settings.window_width = max(window.width(), 1200)
    settings.window_height = max(window.height(), 780)
    current = manager.current()
    if current and current.scope.root_dir:
        settings.last_session_root = current.scope.root_dir
        if current.scope.root_dir not in settings.recent_roots:
            settings.recent_roots = [current.scope.root_dir, *settings.recent_roots][:10]

    settings_store.save(settings)
    return exit_code
