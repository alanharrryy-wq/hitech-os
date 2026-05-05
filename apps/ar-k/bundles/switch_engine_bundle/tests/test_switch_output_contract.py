from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from compat.canonical_index_shim import CanonicalIndexShim
from contracts.artifact_contracts import registry_shape_note, validate_artifact_names
from contracts.shared_canon import PORTABLE_CANONICAL_INDEX, REQUIRED_SWITCH_ARTIFACTS
from switch_engine.models import SwitchEntry
from switch_engine.registry_io import load_canonical_inputs
from switch_engine.resolver import resolve_switch_entries
from tools.generate_example_outputs import generate


class SwitchOutputContractTests(unittest.TestCase):
    def test_generate_only_allowed_switch_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            output_dir = Path(tempdir)
            manifest = generate(output_dir)
            self.assertEqual(sorted(manifest), sorted(REQUIRED_SWITCH_ARTIFACTS))
            self.assertTrue(validate_artifact_names(list(manifest)))
            self.assertEqual(sorted(p.name for p in output_dir.iterdir()), sorted(REQUIRED_SWITCH_ARTIFACTS))

    def test_registry_shape_note_tracks_canonical_names(self) -> None:
        note = registry_shape_note()
        self.assertEqual(sorted(note.keys() - {'invariants'}), sorted(REQUIRED_SWITCH_ARTIFACTS))
        self.assertIn('canonical input files are read-only', note['invariants'])

    def test_canonical_inputs_remain_read_only_across_resolution(self) -> None:
        entries = [
            SwitchEntry('switch.alpha', 'module', 'module.alpha', False),
            SwitchEntry('switch.beta', 'module', 'module.beta', True),
        ]
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            module_path = root / 'module_registry.json'
            boundary_path = root / 'boundary_registry.json'
            index_path = root / PORTABLE_CANONICAL_INDEX
            module_path.write_text(json.dumps([{'module_id': 'module.alpha'}], indent=2), encoding='utf-8')
            boundary_path.write_text(json.dumps([{'boundary_id': 'boundary.alpha'}], indent=2), encoding='utf-8')
            index_path.write_text(json.dumps({'entries': ['module_registry.json']}, indent=2), encoding='utf-8')
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [module_path, boundary_path, index_path]}
            load_canonical_inputs(root)
            resolve_switch_entries(entries, {'module.beta': False}, '2026-04-11T23:59:59Z')
            after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [module_path, boundary_path, index_path]}
            self.assertEqual(before, after)

    def test_legacy_index_support_is_shim_only(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            (root / 'query_index.json').write_text('{}', encoding='utf-8')
            shim = CanonicalIndexShim(root)
            resolved, mode = shim.resolve()
            self.assertEqual(resolved.name, 'query_index.json')
            self.assertEqual(mode, 'legacy_shim')


if __name__ == '__main__':
    unittest.main()
