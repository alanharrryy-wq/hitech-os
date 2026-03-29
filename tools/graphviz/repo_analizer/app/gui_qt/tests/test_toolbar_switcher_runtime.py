import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase

APP_HOST_ROOT = Path(__file__).resolve().parents[3]
if str(APP_HOST_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_HOST_ROOT))

from app.gui_qt.toolbar_controller import ToolbarController


class _FakeSignal:
    def __init__(self) -> None:
        self._handlers = []

    def connect(self, callback) -> None:
        self._handlers.append(callback)

    def emit(self, payload) -> None:
        for callback in list(self._handlers):
            callback(payload)


class _FakeComboItem:
    def __init__(self) -> None:
        self.enabled = True

    def setEnabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)


class _FakeComboModel:
    def __init__(self) -> None:
        self._items: dict[int, _FakeComboItem] = {}

    def item(self, index: int) -> _FakeComboItem:
        if index not in self._items:
            self._items[index] = _FakeComboItem()
        return self._items[index]


class _FakeComboBox:
    def __init__(self) -> None:
        self.currentIndexChanged = _FakeSignal()
        self._signals_blocked = False
        self._items: list[tuple[str, str]] = []
        self._index = -1
        self._model = _FakeComboModel()

    def blockSignals(self, blocked: bool) -> None:
        self._signals_blocked = bool(blocked)

    def clear(self) -> None:
        self._items.clear()
        self._index = -1

    def addItem(self, label: str, data: str) -> None:
        self._items.append((label, data))

    def model(self) -> _FakeComboModel:
        return self._model

    def setCurrentIndex(self, index: int) -> None:
        self._index = index
        if not self._signals_blocked:
            self.currentIndexChanged.emit(index)

    def itemData(self, index: int):
        if index < 0 or index >= len(self._items):
            return None
        return self._items[index][1]

    def currentData(self):
        return self.itemData(self._index)


class _FakeWorkspace:
    def __init__(self) -> None:
        self.active_tool_id = "cloudflare_guardian"
        self._entries = (
            SimpleNamespace(tool_id="cloudflare_guardian", display_name="Cloudflare Guardian Diagnostics", active=True),
            SimpleNamespace(
                tool_id="orchestrator_bridge",
                display_name="Orchestrator Bridge",
                active=False,
            ),
        )
        self.activation_calls: list[str] = []

    def list_tools(self):
        return self._entries

    def activate_tool(self, tool_id: str, *, reason: str = "manual") -> bool:
        self.activation_calls.append(f"{tool_id}:{reason}")
        self.active_tool_id = tool_id
        return True

    def reopen_last_active_tool(self) -> bool:
        self.activation_calls.append("reopen")
        return True


class _FakeServices:
    def get(self, _name: str):
        return None


class _FakeMain:
    def __init__(self) -> None:
        self.tool_switch_combo = _FakeComboBox()
        self.tool_workspace = _FakeWorkspace()
        self.service_container = _FakeServices()


class ToolbarSwitcherRuntimeTests(TestCase):
    def test_refresh_does_not_trigger_reentrant_activation(self):
        main = _FakeMain()
        controller = ToolbarController(main)
        main.tool_switch_combo.currentIndexChanged.connect(controller._on_tool_switch_selected)

        controller.refresh_tool_switcher()
        self.assertEqual(main.tool_workspace.activation_calls, [])

    def test_user_switch_still_activates_tool(self):
        main = _FakeMain()
        controller = ToolbarController(main)
        main.tool_switch_combo.currentIndexChanged.connect(controller._on_tool_switch_selected)
        controller.refresh_tool_switcher()

        main.tool_switch_combo.setCurrentIndex(1)
        self.assertEqual(
            main.tool_workspace.activation_calls,
            ["orchestrator_bridge:toolbar-switch"],
        )


