#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from capatch_project.detectors import detect_project
from capatch_packs.dependency_map.planner import install_analyzer
from capatch_packs.dependency_map.verifier import verify_project


class ProjectCapabilityDependencyMapTests(unittest.TestCase):
    def test_detects_python_project(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "main.py").write_text("import json\n", encoding="utf-8")
            profile = detect_project(root)
            self.assertTrue(profile.exists)
            self.assertIn("python", profile.languages)

    def test_installs_and_verifies_dependency_map_analyzer(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "package.json").write_text(
                json.dumps({"name": "demo", "dependencies": {"react": "latest"}}),
                encoding="utf-8",
            )
            (root / "src").mkdir()
            (root / "src" / "index.ts").write_text(
                "import React from 'react'\nimport x from './x'\n",
                encoding="utf-8",
            )
            (root / "src" / "x.ts").write_text("export const x = 1\n", encoding="utf-8")
            result = install_analyzer(root, dry_run=False)
            self.assertTrue(Path(str(result["target"])).exists())
            self.assertTrue(verify_project(root)["ok"])


if __name__ == "__main__":
    unittest.main()
