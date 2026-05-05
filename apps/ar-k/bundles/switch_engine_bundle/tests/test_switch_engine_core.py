from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from compat.canonical_index_shim import CanonicalIndexShim
from contracts.exclusion_policy import should_exclude
from switch_engine.invariants import assert_deterministic, assert_read_only_hashes, assert_traceability
from switch_engine.models import SwitchEntry
from switch_engine.registry_io import load_canonical_inputs
from switch_engine.resolver import resolve_switch_entries


class SwitchEngineCoreTests(unittest.TestCase):
    def test_resolve_switch_entries_prefers_switch_id_then_target_id(self) -> None:
        entries = [
            SwitchEntry('switch.alpha', 'module', 'module.alpha', False),
            SwitchEntry('switch.beta', 'module', 'module.beta', True),
        ]
        resolutions, trace, warnings, _hash = resolve_switch_entries(
            entries,
            {'switch.alpha': True, 'module.beta': False},
            '2026-04-11T21:00:00Z',
        )
        self.assertEqual(resolutions[0]['resolved_value'], True)
        self.assertEqual(resolutions[0]['decision_source'], 'switch_id')
        self.assertEqual(resolutions[1]['resolved_value'], False)
        self.assertEqual(resolutions[1]['decision_source'], 'target_id')
        self.assertEqual(warnings, [])
        assert_traceability(trace)

    def test_invalid_override_is_ignored_with_warning(self) -> None:
        entries = [SwitchEntry('switch.gamma', 'route', 'route.gamma', True)]
        resolutions, trace, warnings, _hash = resolve_switch_entries(
            entries,
            {'switch.gamma': 'not-bool'},
            '2026-04-11T21:01:00Z',
        )
        self.assertEqual(resolutions[0]['resolved_value'], True)
        self.assertEqual(trace[0]['precedence_path'], ['default', 'invalid_override_ignored'])
        self.assertEqual(len(warnings), 1)

    def test_determinism_and_read_only_inputs(self) -> None:
        entries = [SwitchEntry('switch.delta', 'boundary', 'boundary.delta', False)]
        deterministic_hash = assert_deterministic(entries, {'boundary.delta': True}, '2026-04-11T21:02:00Z')
        self.assertEqual(len(deterministic_hash), 64)
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / 'module_registry.json').write_text(json.dumps([{'module_id': 'module.alpha'}]), encoding='utf-8')
            (root / 'boundary_registry.json').write_text(json.dumps([{'boundary_id': 'boundary.alpha'}]), encoding='utf-8')
            (root / 'registry_index.json').write_text(json.dumps({'entries': []}), encoding='utf-8')
            before = load_canonical_inputs(root)['input_hashes']
            after = load_canonical_inputs(root)['input_hashes']
            assert_read_only_hashes(before, after)

    def test_legacy_index_shim(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / 'query_index.json').write_text('{}', encoding='utf-8')
            shim = CanonicalIndexShim(root)
            path, mode = shim.resolve()
            self.assertEqual(path.name, 'query_index.json')
            self.assertEqual(mode, 'legacy_shim')

    def test_reports_real_is_excluded(self) -> None:
        self.assertTrue(should_exclude('apps/ar-k/reports_real/switch_resolution_summary.json'))
        self.assertFalse(should_exclude('apps/ar-k/pya/engines/switch_engine/engine.py'))


if __name__ == '__main__':
    unittest.main()
