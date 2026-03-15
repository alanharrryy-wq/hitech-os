from __future__ import annotations

import unittest

from tools.hos.git_sentinel_modular.scanning.artifacts import ArtifactClassifier


class ArtifactClassifierTestCase(unittest.TestCase):
    def test_classifies_report_file(self):
        classifier = ArtifactClassifier()
        finding = classifier.classify_path("tools/_reports/audit_report.json")
        self.assertIsNotNone(finding)
        self.assertEqual(finding.category, "report")

    def test_classifies_generated_directory(self):
        classifier = ArtifactClassifier()
        finding = classifier.classify_path("dist/assets/app.js")
        self.assertIsNotNone(finding)
        self.assertIn(finding.category, {"generated_code", "runtime_state"})

    def test_returns_none_for_source_file(self):
        classifier = ArtifactClassifier()
        finding = classifier.classify_path("src/domain/service.py")
        self.assertIsNone(finding)


if __name__ == "__main__":
    unittest.main()
