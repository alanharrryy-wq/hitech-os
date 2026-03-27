from __future__ import annotations

import sys
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools/execution_framework"))

from lib.validators import validate_against_patterns


class OwnershipEnforcementTests(unittest.TestCase):
    def test_path_outside_allowed_is_rejected(self):
        issues = validate_against_patterns(["services/api/app.py"], ["apps/site/**"], [])
        self.assertTrue(any(item.code == "ownership_violation" for item in issues))

    def test_forbidden_path_is_rejected(self):
        issues = validate_against_patterns(["apps/web/page.tsx"], ["apps/**"], ["apps/web/**"])
        self.assertTrue(any(item.code == "forbidden_path" for item in issues))


if __name__ == "__main__":
    unittest.main()
