from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos.git_sentinel_modular.security.scanner import SecurityScanner


class SecurityScannerTestCase(unittest.TestCase):
    def _make_repo(self) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / ".git").mkdir()
        (root / "src").mkdir()
        (root / "src" / "safe.py").write_text("print('hello')\n", encoding="utf-8")
        (root / "src" / "config.env").write_text("SECRET=my-secret\nTOKEN=abc\n", encoding="utf-8")
        return root

    def test_finds_secret_like_markers(self):
        repo = self._make_repo()
        scanner = SecurityScanner()
        findings = scanner.scan_security(str(repo))
        self.assertGreaterEqual(len(findings), 1)
        rule_ids = {f.rule_id for f in findings}
        self.assertTrue("SEC_SECRET" in rule_ids or "SEC_TOKEN" in rule_ids)

    def test_ignores_binary_blob(self):
        repo = self._make_repo()
        (repo / "blob.bin").write_bytes(b"\x00\x01\x02")
        scanner = SecurityScanner()
        findings = scanner.scan_security(str(repo))
        self.assertIsInstance(findings, list)


if __name__ == "__main__":
    unittest.main()
