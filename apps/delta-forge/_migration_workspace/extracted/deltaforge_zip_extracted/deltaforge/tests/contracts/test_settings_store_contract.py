from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from infrastructure.persistence.settings_store import (
    SettingsStore as LegacySettingsStore,
)
from infrastructure.settings_store import SettingsStore


class SettingsStoreContractTests(unittest.TestCase):
    def test_roundtrip_persists_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "settings.json"
            store = SettingsStore(path)

            store.set("theme", "dark")
            store.write("show_hidden", True)

            reloaded = SettingsStore(path)
            self.assertEqual(reloaded.get("theme"), "dark")
            self.assertIs(reloaded.read("show_hidden"), True)

    def test_update_delete_and_clear_are_stable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "settings.json"
            store = SettingsStore(path)

            store.update({"a": 1, "b": 2})
            self.assertEqual(store.load(), {"a": 1, "b": 2})

            self.assertTrue(store.delete("a"))
            self.assertEqual(store.read_all(), {"b": 2})

            self.assertFalse(store.delete("missing"))
            self.assertEqual(store.clear(), {})

    def test_legacy_shim_resolves_to_canonical_store(self) -> None:
        self.assertIs(LegacySettingsStore, SettingsStore)


if __name__ == "__main__":
    unittest.main()
