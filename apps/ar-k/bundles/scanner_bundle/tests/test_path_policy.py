from __future__ import annotations

import unittest

from contracts_py.path_policy import classify_path_policy

class PathPolicyTests(unittest.TestCase):
    def test_reports_real_is_excluded(self) -> None:
        policy = classify_path_policy('reports_real/live/run.md')
        self.assertEqual(policy.action, 'exclude')

    def test_docs_are_observed_only(self) -> None:
        policy = classify_path_policy('docs/architecture.md')
        self.assertEqual(policy.action, 'observe_only')
        self.assertFalse(policy.canonical_source)

    def test_runtime_source_is_canonical(self) -> None:
        policy = classify_path_policy('src/screens/PaymentsScreen.tsx')
        self.assertEqual(policy.action, 'canonical')
        self.assertTrue(policy.canonical_source)

if __name__ == '__main__':
    unittest.main()
