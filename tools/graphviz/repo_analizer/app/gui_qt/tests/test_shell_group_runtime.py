import sys
from dataclasses import dataclass
from pathlib import Path
from unittest import TestCase

from PySide6.QtCore import QObject

APP_HOST_ROOT = Path(__file__).resolve().parents[3]
if str(APP_HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_HOST_ROOT))

from app.gui_qt.event_bus import EventBus, Events
from app.gui_qt.shell.group_shell import ShellGroupRuntime


class _FakeSettings:
    def __init__(self, initial: dict[str, object] | None = None) -> None:
        self._data = dict(initial or {})

    def value(self, key: str, default_value: object = ""):
        return self._data.get(key, default_value)

    def setValue(self, key: str, value: object) -> None:
        self._data[key] = value


class _FakeStatusBar:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def showMessage(self, text: str, _timeout: int = 0) -> None:
        self.messages.append(str(text))


class _FakeDock:
    def __init__(self, name: str) -> None:
        self.name = name
        self.visible = False

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def raise_(self) -> None:
        return None


@dataclass(slots=True)
class _ToolEntry:
    tool_id: str
    visible: bool


class _FakeToolWorkspace:
    def __init__(self) -> None:
        self.active_tool_id: str | None = None
        self._last_active_tool_id: str | None = None
        self.visible_tools: set[str] = set()
        self.lifecycle_calls: list[tuple[str, str]] = []

    def list_tools(self):
        return tuple(
            _ToolEntry(tool_id=tool_id, visible=(tool_id in self.visible_tools))
            for tool_id in ("cloudflare_guardian", "orchestrator_bridge")
        )

    def activate_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        normalized = str(tool_id or "").strip().lower()
        if normalized not in {"cloudflare_guardian", "orchestrator_bridge"}:
            return False
        self.active_tool_id = normalized
        self._last_active_tool_id = normalized
        self.visible_tools = {normalized}
        self.lifecycle_calls.append(("activate", reason))
        return True

    def hide_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        normalized = str(tool_id or "").strip().lower()
        self.visible_tools.discard(normalized)
        if self.active_tool_id == normalized:
            self.active_tool_id = None
        self.lifecycle_calls.append(("hide", reason))
        return True

    def reopen_last_active_tool(self) -> bool:
        if not self._last_active_tool_id:
            return False
        target = self._last_active_tool_id
        self.active_tool_id = target
        self.visible_tools = {target}
        self.lifecycle_calls.append(("reopen", "manual"))
        return True


class _FakeServices:
    def __init__(self) -> None:
        self._services: dict[str, object] = {}

    def register(self, key: str, value: object) -> None:
        self._services[key] = value

    def get(self, key: str):
        return self._services.get(key)


class _FakeContextRuntime:
    def __init__(self) -> None:
        self.updates: list[dict[str, object]] = []

    def update(self, **changes: object) -> None:
        self.updates.append(dict(changes))


class _FakeMain(QObject):
    def __init__(self, *, settings_data: dict[str, object] | None = None) -> None:
        super().__init__(None)
        self.settings = _FakeSettings(settings_data)
        self.event_bus = EventBus()
        self.service_container = _FakeServices()
        self.tool_workspace = _FakeToolWorkspace()
        self._status = _FakeStatusBar()

        for dock_name in (
            "workspace_summary_dock",
            "preview_workspace_dock",
            "central_inspector_dock",
            "tools_launcher_dock",
            "explorer_dock",
            "results_dock",
            "inspector_dock",
            "bookmarks_dock",
        ):
            setattr(self, dock_name, _FakeDock(dock_name))

    def statusBar(self) -> _FakeStatusBar:
        return self._status


class ShellGroupRuntimeTests(TestCase):
    def _build_runtime(self, *, settings_data: dict[str, object] | None = None):
        main = _FakeMain(settings_data=settings_data)
        context_runtime = _FakeContextRuntime()
        main.service_container.register("workstation_context", context_runtime)
        runtime = ShellGroupRuntime(main)
        main.service_container.register("shell_group_runtime", runtime)
        return main, runtime, context_runtime

    def test_graph_group_activates_cloudflare_guardian_and_collapses_core_docks(self):
        main, runtime, context_runtime = self._build_runtime()
        applied = runtime.apply_group("graph", reason="test")

        self.assertTrue(applied)
        self.assertEqual(main.tool_workspace.active_tool_id, "cloudflare_guardian")
        self.assertFalse(main.workspace_summary_dock.visible)
        self.assertFalse(main.explorer_dock.visible)
        self.assertFalse(main.results_dock.visible)
        self.assertEqual(runtime.active_group_id, "graph")
        self.assertTrue(any(update.get("active_group") == "graph" for update in context_runtime.updates))

    def test_run_group_activates_orchestrator_and_shows_console(self):
        main, runtime, _ = self._build_runtime()
        runtime.apply_group("run", reason="test")

        self.assertEqual(main.tool_workspace.active_tool_id, "orchestrator_bridge")
        self.assertTrue(main.results_dock.visible)
        self.assertFalse(main.explorer_dock.visible)

    def test_explore_group_suspends_visible_plugin_tools(self):
        main, runtime, _ = self._build_runtime()
        runtime.apply_group("graph", reason="test")
        runtime.apply_group("explore", reason="test")

        self.assertIsNone(main.tool_workspace.active_tool_id)
        self.assertFalse(main.results_dock.visible)
        self.assertTrue(main.workspace_summary_dock.visible)
        self.assertTrue(main.explorer_dock.visible)

    def test_restore_startup_group_uses_active_tool_mapping(self):
        main, runtime, _ = self._build_runtime(settings_data={"shell_active_group_v1": ""})
        main.tool_workspace.active_tool_id = "orchestrator_bridge"
        selected = runtime.restore_startup_group()

        self.assertEqual(selected, "run")
        self.assertEqual(runtime.active_group_id, "run")

    def test_shell_group_change_event_is_published(self):
        main, runtime, _ = self._build_runtime()
        runtime.apply_group("search", reason="test")
        history = main.event_bus.get_history(Events.SHELL_GROUP_CHANGED)

        self.assertTrue(history)
        payload = history[-1][1]
        self.assertEqual(payload.get("group_id"), "search")


