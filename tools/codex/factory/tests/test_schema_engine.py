from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.schema_engine import validate_instance


class SchemaEngineTests(unittest.TestCase):
    def test_valid_payload(self) -> None:
        schema = {
            "type": "object",
            "required": ["name", "items"],
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "items": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["path"],
                        "properties": {"path": {"type": "string", "pattern": r"^a/"}},
                        "additionalProperties": False,
                    },
                },
            },
            "additionalProperties": False,
        }
        payload = {"name": "ok", "items": [{"path": "a/file.txt"}]}
        errors = validate_instance(payload, schema)
        self.assertEqual([], errors)

    def test_invalid_payload(self) -> None:
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string", "minLength": 3}},
            "additionalProperties": False,
        }
        payload = {"name": "x", "extra": True}
        errors = validate_instance(payload, schema)
        self.assertGreaterEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
