from __future__ import annotations

import unittest

from capatch_contracts.plugin_runtime import (
    CAPATCH_PLUGIN_RUNTIME_VERSION,
    ESSENTIAL_PLUGIN_CAPABILITIES,
    infer_plugin_capabilities,
    summarize_essential_runtime_health,
)
from capatch_contracts.versions import CAPATCH_PLUGIN_RUNTIME_VERSION as CONTRACT_RUNTIME_VERSION
from capatch_diagnostics.loader import summarize_runtime_status


class PluginRuntimeContractTests(unittest.TestCase):
    def test_runtime_version_uses_single_source_of_truth(self) -> None:
        self.assertEqual(CAPATCH_PLUGIN_RUNTIME_VERSION, CONTRACT_RUNTIME_VERSION)
        self.assertEqual('6.0.0', CAPATCH_PLUGIN_RUNTIME_VERSION)

    def test_essential_health_detects_rejected_plugins(self) -> None:
        registry = {
            'fixer.safe-runtime-actions': {'status': 'rejected'},
            'recommender.safe-fix-plan': {'status': 'active'},
            'verifier.post-fix-verifier': {'status': 'missing'},
        }
        summary = summarize_essential_runtime_health(CAPATCH_PLUGIN_RUNTIME_VERSION, registry)
        self.assertEqual('failed', summary['status'])
        self.assertIn('fixer.safe-runtime-actions', summary['rejected'])
        self.assertIn('verifier.post-fix-verifier', summary['missing'])

    def test_inferred_capabilities_cover_essential_plugins(self) -> None:
        capabilities = infer_plugin_capabilities('recommender.safe-fix-plan', {'status': 'active'})
        self.assertIn('recommend.safe-fix-plan', capabilities)
        self.assertIn('recommend.outputs.fix-proposal-v2', capabilities)

    def test_essential_health_detects_missing_capabilities(self) -> None:
        registry = {
            'fixer.safe-runtime-actions': {'status': 'active', 'declared_capabilities': ['fix.apply.safe-runtime-actions']},
            'recommender.safe-fix-plan': {'status': 'active', 'declared_capabilities': ['recommend.safe-fix-plan']},
            'verifier.post-fix-verifier': {'status': 'active', 'declared_capabilities': ['verify.post-fix']},
        }
        capability_map = {
            'declared_capabilities_by_plugin': {
                'fixer.safe-runtime-actions': ['fix.apply.safe-runtime-actions'],
                'recommender.safe-fix-plan': ['recommend.safe-fix-plan'],
                'verifier.post-fix-verifier': ['verify.post-fix'],
            }
        }
        summary = summarize_essential_runtime_health(CAPATCH_PLUGIN_RUNTIME_VERSION, registry, capability_map=capability_map)
        self.assertEqual('degraded', summary['status'])
        self.assertTrue(summary['missing_capabilities'])

    def test_runtime_status_surfaces_essential_plugin_health(self) -> None:
        state = {
            'runtime_version': CAPATCH_PLUGIN_RUNTIME_VERSION,
            'registry': {
                'fixer.safe-runtime-actions': {'status': 'active'},
                'recommender.safe-fix-plan': {'status': 'rejected'},
                'verifier.post-fix-verifier': {'status': 'active'},
            },
            'load_summary': {'discovered': 3, 'active': 2, 'rejected': 1, 'disabled': 0, 'duplicate_ids': 0},
            'active_plugins': [{'plugin_id': 'fixer.safe-runtime-actions'}, {'plugin_id': 'verifier.post-fix-verifier'}],
            'disabled_ids': set(),
            'manifests': {},
            'guards': [],
            'before_apply': [],
            'after_apply': [],
            'support_resolvers': [],
            'target_detectors': [],
            'collectors': [],
            'context_enrichers': [],
            'analyzers': [],
            'recommenders': [],
            'fixers': [],
            'verifiers': [],
            'exporters': [],
        }
        status = summarize_runtime_status(state)
        self.assertEqual('failed', status['status'])
        self.assertEqual('failed', status['essential_plugins']['status'])
        self.assertIn('recommender.safe-fix-plan', status['essential_plugins']['rejected'])

    def test_contract_capability_registry_constant_not_empty(self) -> None:
        self.assertIn('fixer.safe-runtime-actions', ESSENTIAL_PLUGIN_CAPABILITIES)
        self.assertTrue(ESSENTIAL_PLUGIN_CAPABILITIES['verifier.post-fix-verifier'])


if __name__ == '__main__':
    unittest.main()
