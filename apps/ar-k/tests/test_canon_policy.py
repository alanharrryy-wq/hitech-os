from __future__ import annotations

import unittest

from pya.system.canon_policy import classify_source_path


class CanonPolicyTests(unittest.TestCase):
    def test_product_runtime_paths_remain_canonical(self) -> None:
        self.assertTrue(classify_source_path("app/page.tsx").canonical_source)
        self.assertTrue(classify_source_path("src/lib/i18n/use-t.ts").canonical_source)
        self.assertTrue(classify_source_path("components/ui/status-panel.tsx").canonical_source)

    def test_non_product_classes_are_marked_noncanonical(self) -> None:
        self.assertEqual(classify_source_path("docs/architecture/README.md").non_product_class, "docs")
        self.assertEqual(classify_source_path("reports/patch_runs/run.json").non_product_class, "reports")
        self.assertEqual(classify_source_path("tests/payments.i18n.contract.test.ts").non_product_class, "tests")
        self.assertEqual(classify_source_path("tools/enforce_i18n_guardrails.py").non_product_class, "tooling")
        self.assertFalse(classify_source_path("scripts/rebuild-index.ts").canonical_source)

    def test_history_artifacts_are_noncanonical(self) -> None:
        self.assertEqual(classify_source_path("src/lib/_tracking/backups/readme.md").non_product_class, "history")
        self.assertEqual(classify_source_path("src/lib/i18n/messages/en.ts.bak").non_product_class, "history")
        self.assertFalse(classify_source_path(".capatch/runtime.patch").canonical_source)


if __name__ == "__main__":
    unittest.main()
