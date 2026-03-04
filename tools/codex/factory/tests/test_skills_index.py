from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.codex.factory.skills_index import EXPECTED_FACTORY_ROLES, build_skills_index, generate_and_write_skills_index


class SkillsIndexTests(unittest.TestCase):
    def test_current_repo_role_counts_match_fixture(self) -> None:
        index = build_skills_index(repo_root=ROOT)
        counts = {
            role: len(index.get("roles", {}).get(role, []))
            for role in EXPECTED_FACTORY_ROLES
        }
        if sum(counts.values()) == 0:
            self.skipTest("No repo-local skills discovered; skipping role-count fixture assertion.")
        expected_counts = {
            "A_core": 10,
            "B_tooling": 10,
            "C_features": 10,
            "D_validation": 10,
            "Z_aggregator": 10,
        }
        self.assertEqual(expected_counts, counts)

    def test_index_generation_is_idempotent(self) -> None:
        first = generate_and_write_skills_index(repo_root=ROOT)
        second = generate_and_write_skills_index(repo_root=ROOT)
        first_json_path = Path(str(first.get("index_json", "")))
        second_json_path = Path(str(second.get("index_json", "")))
        self.assertTrue(first_json_path.exists())
        self.assertTrue(second_json_path.exists())
        first_text = first_json_path.read_text(encoding="utf-8")
        second_text = second_json_path.read_text(encoding="utf-8")
        self.assertEqual(first_text, second_text)
        self.assertEqual(json.loads(first_text), json.loads(second_text))


if __name__ == "__main__":
    unittest.main()
