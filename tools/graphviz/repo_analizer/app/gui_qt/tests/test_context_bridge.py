import os
import sys
from pathlib import Path
from unittest import TestCase

APP_HOST_ROOT = Path(__file__).resolve().parents[3]
if str(APP_HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_HOST_ROOT))

from app.gui_qt.event_bus import EventBus, Events
from app.gui_qt.shell.context_bridge import WorkstationContextBridge
from app.gui_qt.shell.workstation_context import WorkstationContextRuntime


class _FakeToolWorkspace:
    def __init__(self) -> None:
        self.active_tool_id = "cloudflare_guardian"
        self.updates: list[tuple[str, str, dict[str, object]]] = []

    def update_tool_local_context(self, tool_id: str, *, reason: str, **changes: object) -> None:
        self.updates.append((tool_id, reason, dict(changes)))


class ContextBridgeTests(TestCase):
    def test_context_bridge_updates_runtime_and_tool_local_context(self):
        bus = EventBus()
        runtime = WorkstationContextRuntime(bus)
        tool_workspace = _FakeToolWorkspace()
        bridge = WorkstationContextBridge(bus, runtime, tool_workspace=tool_workspace)
        self.addCleanup(bridge.dispose)

        bus.publish(Events.SEARCH_COMPLETED, {"query": "foo", "results_count": 3})
        bus.publish(Events.PREVIEW_OPENED, {"relpath": "src/main.py", "line": 12})
        bus.publish(Events.COMMAND_EXECUTED, {"name": "execute_search"})

        self.assertEqual(runtime.current.active_query, "foo")
        self.assertEqual(runtime.current.results_count, 3)
        self.assertEqual(runtime.current.active_file_relpath, "src/main.py")
        self.assertEqual(runtime.current.last_command, "execute_search")

        update_keys = {key for _, _, payload in tool_workspace.updates for key in payload.keys()}
        self.assertIn("active_query", update_keys)
        self.assertIn("active_file_relpath", update_keys)
        self.assertIn("last_command", update_keys)

    def test_context_bridge_clears_active_tool_when_deactivated(self):
        bus = EventBus()
        runtime = WorkstationContextRuntime(bus)
        tool_workspace = _FakeToolWorkspace()
        bridge = WorkstationContextBridge(bus, runtime, tool_workspace=tool_workspace)
        self.addCleanup(bridge.dispose)

        bus.publish(Events.TOOL_ACTIVATED, {"tool_id": "cloudflare_guardian"})
        self.assertEqual(runtime.current.active_tool_id, "cloudflare_guardian")
        bus.publish(Events.TOOL_DEACTIVATED, {"tool_id": "cloudflare_guardian"})
        self.assertEqual(runtime.current.active_tool_id, "")
