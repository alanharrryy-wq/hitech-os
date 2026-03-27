from __future__ import annotations

import sys
from pathlib import Path
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools/execution_framework"))

from lib.validators import validate_required_fields, validate_payload_items


class ManifestValidationTests(unittest.TestCase):
    def test_missing_required_field_is_reported(self):
        issues = validate_required_fields({}, {"run_id": "string"}, "bundle_manifest")
        self.assertEqual(issues[0].code, "missing_field")

    def test_payload_item_requires_repo_path(self):
        issues = validate_payload_items([{}])
        self.assertTrue(any(item.code == "missing_field" for item in issues))


if __name__ == "__main__":
    unittest.main()
