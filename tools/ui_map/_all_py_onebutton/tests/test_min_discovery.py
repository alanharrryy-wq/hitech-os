from __future__ import annotations

import unittest
from pathlib import Path

from tools.ui_map.analyze_repo import analyze_repository


class DiscoveryMinimumTests(unittest.TestCase):
    def test_minimum_route_and_component_discovery(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        analysis = analyze_repository(repo_root)
        dictionary = analysis["ui_dictionary"]

        self.assertGreaterEqual(len(dictionary.get("routes", [])), 1)
        self.assertGreaterEqual(len(dictionary.get("components", [])), 50)


if __name__ == "__main__":
    unittest.main()
