import sys
from pathlib import Path
from unittest import TestCase

from PySide6.QtCore import QObject

APP_HOST_ROOT = Path(__file__).resolve().parents[3]
if str(APP_HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_HOST_ROOT))

from app.gui_qt.event_bus import EventBus, Events
from app.gui_qt.shell.tool_workspace import ToolWorkspaceCoordinator
from app.gui_qt.shell.workstation_context import WorkstationContextRuntime
from app.gui_qt.tools.catalog import ToolCatalogService


class _FakeSignal:
    def __init__(self) -> None:
        self._handlers = []

    def connect(self, callback) -> None:
        self._handlers.append(callback)

    def emit(self, payload) -> None:
        for callback in list(self._handlers):
            callback(payload)


class _FakeWidget:
    def __init__(self) -> None:
        self.lifecycle_calls: list[str] = []
        self.context_payloads: list[dict[str, object]] = []

    def on_tool_activate(self) -> None:
        self.lifecycle_calls.append("activate")

    def on_tool_deactivate(self) -> None:
        self.lifecycle_calls.append("deactivate")

    def on_tool_suspend(self) -> None:
        self.lifecycle_calls.append("suspend")

    def on_tool_restore(self) -> None:
        self.lifecycle_calls.append("restore")

    def on_tool_hide(self) -> None:
        self.lifecycle_calls.append("hide")

    def set_tool_context(self, payload: dict[str, object]) -> None:
        self.context_payloads.append(dict(payload))


class _FakeDock:
    def __init__(self, widget: _FakeWidget) -> None:
        self._widget = widget
        self._visible = False
        self._properties = {}
        self.visibilityChanged = _FakeSignal()

    def setAttribute(self, *_args, **_kwargs) -> None:
        return None

    def setProperty(self, key: str, value) -> None:
        self._properties[key] = value

    def widget(self):
        return self._widget

    def show(self) -> None:
        self._visible = True
        self.visibilityChanged.emit(True)

    def hide(self) -> None:
        self._visible = False
        self.visibilityChanged.emit(False)

    def raise_(self) -> None:
        return None

    def isVisible(self) -> bool:
        return self._visible

    def setParent(self, *_args, **_kwargs) -> None:
        return None

    def deleteLater(self) -> None:
        return None


class _FakeSettings:
    def __init__(self) -> None:
        self._data = {}

    def value(self, key, default_value=""):
        return self._data.get(key, default_value)

    def setValue(self, key, value) -> None:
        self._data[key] = value

    def remove(self, key) -> None:
        self._data.pop(key, None)


class _FakeServices:
    def __init__(self) -> None:
        self._services = {}

    def register(self, name: str, value) -> None:
        self._services[name] = value

    def get(self, name: str):
        return self._services.get(name)


class _FakeMainWindow(QObject):
    def __init__(self) -> None:
        super().__init__(None)
        self.settings = _FakeSettings()
        self.event_bus = EventBus()
        self.service_container = _FakeServices()
        self.shell_menu_builder = None


class _RecursiveStr:
    def __str__(self) -> str:
        return str(self)


class ToolWorkspaceLifecycleTests(TestCase):
    def _build_workspace(self) -> ToolWorkspaceCoordinator:
        main = _FakeMainWindow()
        catalog = ToolCatalogService(main.settings)
        context_runtime = WorkstationContextRuntime(main.event_bus)
        main.service_container.register("tool_catalog", catalog)
        main.service_container.register("workstation_context", context_runtime)
        return ToolWorkspaceCoordinator(main)

    def test_single_active_invariant_and_reopen_last(self):
        workspace = self._build_workspace()
        widget_a = _FakeWidget()
        widget_b = _FakeWidget()
        dock_a = _FakeDock(widget_a)
        dock_b = _FakeDock(widget_b)

        workspace.register_tool_surface(
            contribution_id="cloudflare_guardian.dock",
            title="Cloudflare Guardian Diagnostics",
            dock=dock_a,
        )
        workspace.register_tool_surface(
            contribution_id="orchestrator_bridge.dock",
            title="Orchestrator Bridge",
            dock=dock_b,
        )

        self.assertTrue(workspace.activate_tool("cloudflare_guardian", reason="test"))
        self.assertTrue(dock_a.isVisible())
        self.assertFalse(dock_b.isVisible())

        self.assertTrue(workspace.activate_tool("orchestrator_bridge", reason="test"))
        self.assertFalse(dock_a.isVisible())
        self.assertTrue(dock_b.isVisible())
        self.assertEqual(workspace.active_tool_id, "orchestrator_bridge")

        workspace.hide_tool("orchestrator_bridge", reason="test-hide")
        self.assertFalse(dock_b.isVisible())
        self.assertIsNone(workspace.active_tool_id)

        reopened = workspace.reopen_last_active_tool()
        self.assertTrue(reopened)
        self.assertEqual(workspace.active_tool_id, "orchestrator_bridge")
        self.assertTrue(dock_b.isVisible())

    def test_disable_tool_is_non_destructive_and_emits_lifecycle_event(self):
        workspace = self._build_workspace()
        widget = _FakeWidget()
        dock = _FakeDock(widget)
        workspace.register_tool_surface(
            contribution_id="cloudflare_guardian.dock",
            title="Cloudflare Guardian Diagnostics",
            dock=dock,
        )
        workspace.activate_tool("cloudflare_guardian", reason="test")

        result = workspace.set_tool_enabled("cloudflare_guardian", False, reason="test-disable")
        self.assertTrue(result)
        self.assertFalse(dock.isVisible())
        history = workspace.main.event_bus.get_history(Events.TOOL_LIFECYCLE_TRANSITION)
        self.assertTrue(
            any(
                payload.get("action") == "set_enabled"
                and payload.get("tool_id") == "cloudflare_guardian"
                for _, payload in history
                if isinstance(payload, dict)
            )
        )

    def test_workstation_and_local_context_are_pushed_to_active_tool(self):
        workspace = self._build_workspace()
        widget = _FakeWidget()
        dock = _FakeDock(widget)
        workspace.register_tool_surface(
            contribution_id="cloudflare_guardian.dock",
            title="Cloudflare Guardian Diagnostics",
            dock=dock,
        )
        workspace.activate_tool("cloudflare_guardian", reason="test")
        workspace.main.event_bus.publish(
            Events.WORKSTATION_CONTEXT_CHANGED,
            {"repo_root": "F:/repos/hitech-os", "active_tool_id": "cloudflare_guardian"},
        )
        workspace.update_tool_local_context("cloudflare_guardian", reason="test", mode="analysis")

        self.assertTrue(widget.context_payloads)
        last_payload = widget.context_payloads[-1]
        self.assertEqual(last_payload["tool_id"], "cloudflare_guardian")
        self.assertEqual(last_payload["global"]["repo_root"], "F:/repos/hitech-os")
        self.assertEqual(last_payload["local"]["mode"], "analysis")

    def test_restore_startup_state_skips_disabled_target_and_activates_enabled_tool(self):
        workspace = self._build_workspace()
        dock_a = _FakeDock(_FakeWidget())
        dock_b = _FakeDock(_FakeWidget())
        workspace.register_tool_surface(
            contribution_id="cloudflare_guardian.dock",
            title="Cloudflare Guardian Diagnostics",
            dock=dock_a,
        )
        workspace.register_tool_surface(
            contribution_id="orchestrator_bridge.dock",
            title="Orchestrator Bridge",
            dock=dock_b,
        )
        workspace.set_tool_enabled("cloudflare_guardian", False, reason="test")
        workspace._active_tool_id = "cloudflare_guardian"
        workspace._last_active_tool_id = "cloudflare_guardian"

        workspace.restore_startup_state()

        self.assertEqual(workspace.active_tool_id, "orchestrator_bridge")
        self.assertTrue(dock_b.isVisible())
        self.assertFalse(dock_a.isVisible())

    def test_restore_snapshot_contract_persists_state_shape(self):
        workspace = self._build_workspace()
        dock = _FakeDock(_FakeWidget())
        workspace.register_tool_surface(
            contribution_id="cloudflare_guardian.dock",
            title="Cloudflare Guardian Diagnostics",
            dock=dock,
        )
        workspace.activate_tool("cloudflare_guardian", reason="test")
        snapshot = workspace.build_restore_snapshot()

        self.assertIn("active_tool_id", snapshot)
        self.assertIn("last_active_tool_id", snapshot)
        self.assertIn("single_active_mode", snapshot)
        self.assertIn("tool_states", snapshot)
        workspace.persist_restore_snapshot()
        reloaded = workspace.load_restore_snapshot()
        self.assertEqual(reloaded.get("active_tool_id"), "cloudflare_guardian")

    def test_normalize_tool_id_handles_recursive_string_value(self):
        workspace = self._build_workspace()
        normalized = workspace._normalize_tool_id(_RecursiveStr())
        self.assertEqual(normalized, "tool")

