from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.smoke import run_smoke


class FactorySmokeTests(unittest.TestCase):
    def test_smoke_passes(self) -> None:
        payload = run_smoke("factory_smoke_test_20260218_000000_001")
        self.assertEqual("PASS", payload["status"])
        self.assertTrue(payload["deterministic"])


if __name__ == "__main__":
    unittest.main()
