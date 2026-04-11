from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pya.engines.scanner.engine import ScannerEngine

from tests.helpers import build_context, load_manifest, read_json


class ScannerEngineTests(unittest.TestCase):
    def test_engine_runs_and_emits_signals(self) -> None:
        temp_dir, context = build_context()
        try:
            engine = ScannerEngine(manifest=load_manifest("scanner"))
            result = engine.run(context)
            signals = read_json(context.paths.registries / "signals.json")
            inventory = read_json(context.paths.artifacts / "inventory" / "scanner_inventory.json")
            self.assertGreater(len(signals), 0)
            self.assertGreater(len(inventory), 0)
            self.assertIn("signals", result.execution_summary["registries_written"])
        finally:
            temp_dir.cleanup()

    def test_tolerates_parse_defect(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            (target / "pkg").mkdir()
            (target / "pkg" / "ok.py").write_text("import json\n", encoding="utf-8")
            (target / "pkg" / "bad.py").write_text("def broken(:\n    pass\n", encoding="utf-8")
            temp_dir, context = build_context(target=target)
            try:
                engine = ScannerEngine(manifest=load_manifest("scanner"))
                engine.run(context)
                signals = read_json(context.paths.registries / "signals.json")
                bad_signals = [
                    item
                    for item in signals
                    if item["source_path"].endswith("bad.py") and item["state"] == "ambiguous"
                ]
                self.assertTrue(bad_signals)
            finally:
                temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
