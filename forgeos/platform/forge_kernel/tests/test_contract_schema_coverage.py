import json
import unittest
from pathlib import Path

from forge_kernel import WAVE1_CONTRACTS


class ContractSchemaCoverageTests(unittest.TestCase):
    def test_schema_index_covers_wave1_contracts(self) -> None:
        forgeos_root = Path(__file__).resolve().parents[3]
        schemas_root = forgeos_root / "governance" / "schemas"
        index_path = schemas_root / "contract_schema_index.json"
        self.assertTrue(index_path.exists(), "contract schema index must exist")

        data = json.loads(index_path.read_text(encoding="utf-8"))
        self.assertEqual(data["total_contracts"], len(WAVE1_CONTRACTS))

        contract_map = {entry["contract_id"]: entry for entry in data["contracts"]}
        self.assertEqual(len(contract_map), len(WAVE1_CONTRACTS))

        for definition in WAVE1_CONTRACTS:
            self.assertIn(definition.contract_id, contract_map)
            entry = contract_map[definition.contract_id]
            schema_file = schemas_root / entry["schema_file"]
            self.assertTrue(schema_file.exists(), f"schema missing for {definition.contract_id}")

            schema = json.loads(schema_file.read_text(encoding="utf-8"))
            request_all_of = schema["properties"]["request"]["allOf"]
            response_all_of = schema["properties"]["response"]["allOf"]
            request_const = request_all_of[1]["properties"]["contract_id"]["const"]
            response_const = response_all_of[1]["properties"]["contract_id"]["const"]
            self.assertEqual(request_const, definition.contract_id)
            self.assertEqual(response_const, definition.contract_id)


if __name__ == "__main__":
    unittest.main()
