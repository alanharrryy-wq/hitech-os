from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools/execution_framework"))

from lib.reports import compute_apply_order


class DependencyOrderTests(unittest.TestCase):
    def test_topological_order_respects_dependencies(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            (repo / "configs/execution_framework").mkdir(parents=True, exist_ok=True)
            (repo / "parallel_manifest.json").write_text(json.dumps({
                "01-a": {"depends_on": []},
                "02-b": {"depends_on": ["01-a"]},
                "03-c": {"depends_on": ["02-b"]},
            }), encoding="utf-8")
            order = compute_apply_order(repo, ["03-c", "02-b", "01-a"])
            self.assertEqual(order, ["01-a", "02-b", "03-c"])


if __name__ == "__main__":
    unittest.main()
