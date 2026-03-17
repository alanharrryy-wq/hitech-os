from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.codex.guards.no_js_src_imports import load_allowlist, scan_repo


class NoJsSrcImportsTests(unittest.TestCase):
    def _write(self, path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_detects_relative_js_import_in_src(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write(root / "services/core-api/src/main.ts", 'import { x } from "./dep.js";\n')
            self._write(root / "services/core-api/src/dep.ts", "export const x = 1;\n")
            allowlist_path = root / "allowlist.json"
            allowlist_path.write_text(json.dumps({"allow": []}), encoding="utf-8")

            violations, scanned = scan_repo(root, load_allowlist(allowlist_path))

            self.assertEqual(scanned, 2)
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0].file, "services/core-api/src/main.ts")
            self.assertEqual(violations[0].specifier, "./dep.js")

    def test_respects_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write(root / "packages/contracts/src/index.ts", 'export * from "./featureFlags.js";\n')
            allowlist_path = root / "allowlist.json"
            allowlist_path.write_text(
                json.dumps(
                    {
                        "allow": [
                            {
                                "file_glob": "packages/contracts/src/*.ts",
                                "specifier_glob": "*.js",
                            },
                            {
                                "file_glob": "packages/contracts/src/**/*.ts",
                                "specifier_glob": "*.js",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            violations, scanned = scan_repo(root, load_allowlist(allowlist_path))

            self.assertEqual(scanned, 1)
            self.assertEqual(violations, [])

    def test_ignores_non_import_js_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write(
                root / "apps/web/src/lib/api.ts",
                "const payload = await response.json();\nconst ext = '.js';\n",
            )
            allowlist_path = root / "allowlist.json"
            allowlist_path.write_text(json.dumps({"allow": []}), encoding="utf-8")

            violations, scanned = scan_repo(root, load_allowlist(allowlist_path))

            self.assertEqual(scanned, 1)
            self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
