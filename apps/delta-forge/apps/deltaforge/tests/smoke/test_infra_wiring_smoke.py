from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from infrastructure.event_bus_in_memory import InMemoryEventBus
from infrastructure.file_watcher_polling import FileWatcherPolling
from infrastructure.settings_store import SettingsStore


class InfraWiringSmokeTests(unittest.TestCase):
    def test_store_bus_and_watcher_wire_without_ui_imports(self) -> None:
        bus = InMemoryEventBus()
        received: list[object] = []
        bus.subscribe("filesystem_changed", received.append)

        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            settings = SettingsStore(tmp_path / "settings.json")
            watcher = FileWatcherPolling(event_bus=bus)

            workspace = tmp_path / "workspace"
            workspace.mkdir()
            watcher.watch(workspace)

            settings.set("theme", "dark")
            (workspace / "a.txt").write_text("hello", encoding="utf-8")

            changes = watcher.poll()

            self.assertEqual(settings.get("theme"), "dark")
            self.assertTrue(changes)
            self.assertEqual(received, [changes])


if __name__ == "__main__":
    unittest.main()
