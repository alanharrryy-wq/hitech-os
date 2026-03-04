from __future__ import annotations

import unittest
from pathlib import Path

from tools.ui_map.analyze_repo import analyze_repository
from tools.ui_map.emit_docs import _schema
from tools.ui_map.validators import validate_deterministic_ids, validate_schema_conformance, validate_sorting


class SchemaValidationTests(unittest.TestCase):
    def test_dictionary_conforms_to_internal_schema(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        analysis = analyze_repository(repo_root)
        dictionary = analysis["ui_dictionary"]
        schema = _schema()

        schema_errors = validate_schema_conformance(dictionary, schema)
        id_errors = validate_deterministic_ids(dictionary)
        sort_errors = validate_sorting(dictionary)

        self.assertEqual(schema_errors, [])
        self.assertEqual(id_errors, [])
        self.assertEqual(sort_errors, [])


if __name__ == "__main__":
    unittest.main()
