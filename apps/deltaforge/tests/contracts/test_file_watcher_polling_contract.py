from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path

from infrastructure.file_watcher_polling import FileWatcherPolling


class FileWatcherPollingContractTests(unittest.TestCase):
    def test_poll_detects_create_modify_delete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            watcher = FileWatcherPolling()
            watcher.watch(root)

            path = root / "demo.txt"
            path.write_text("one", encoding="utf-8")

            created = watcher.poll()
            self.assertTrue(any(item["change_type"] == "created" for item in created))

            time.sleep(0.02)
            path.write_text("two", encoding="utf-8")

            modified = watcher.poll()
            self.assertTrue(any(item["change_type"] == "modified" for item in modified))

            path.unlink()
            deleted = watcher.poll()
            self.assertTrue(any(item["change_type"] == "deleted" for item in deleted))


if __name__ == "__main__":
    unittest.main()
