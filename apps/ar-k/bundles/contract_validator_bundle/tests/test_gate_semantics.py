
from __future__ import annotations

import unittest

from ark_contract_validator_bundle.runtime.severities import bundle_status_from_findings


class GateSemanticsTests(unittest.TestCase):
    def test_ready_warning_blocked_semantics(self) -> None:
        self.assertEqual(bundle_status_from_findings(['info']), 'READY')
        self.assertEqual(bundle_status_from_findings(['info', 'warning']), 'WARNING')
        self.assertEqual(bundle_status_from_findings(['warning', 'error']), 'BLOCKED')
        self.assertEqual(bundle_status_from_findings(['critical']), 'BLOCKED')
