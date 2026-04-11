from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.qa_testkit import apply_ops, build_ops, fixture_workspace, make_ctx, read_json, read_text

from capatch_engine.preflight import preflight
from capatch_engine.strategy_selector import select_patch_strategy
from capatch_policy import classify_change
from capatch_verify.registry import run_required_verifiers
from capatch_ops.semantic_typescript import render_ts_ensure_import, render_ts_wrap_jsx_text


class EngineGoldenTests(unittest.TestCase):
    def test_textual_replace_exact_matches_golden(self) -> None:
        with fixture_workspace('golden_replace_exact') as root:
            target = root / 'app.py'
            before = read_text(root / 'expected_before.py')
            after = read_text(root / 'expected_after.py')
            self.assertEqual(before, read_text(target))

            rows = [
                {
                    'type': 'EnsureReplaceExactOnce',
                    'label': 'meaning-42',
                    'file': 'app.py',
                    'old_text': '    return 41\n',
                    'new_text': '    return 42\n',
                }
            ]
            _ctx, _ops, pf, pv, results = apply_ops(root, rows)
            self.assertTrue(pf.ok)
            self.assertIn('app.py', pf.target_files)
            self.assertTrue(pv['messages'])
            self.assertEqual('applied', results[0].patch_status)
            self.assertEqual(after, read_text(target))

            _ctx2, _ops2, _pf2, _pv2, results2 = apply_ops(root, rows)
            self.assertEqual('noop', results2[0].patch_status)
            self.assertEqual(after, read_text(target))

    def test_normalize_file_crlf_unicode_matches_golden(self) -> None:
        with fixture_workspace('golden_normalize') as root:
            target = root / 'notes.txt'
            expected = read_text(root / 'expected_after.txt')
            rows = [
                {
                    'type': 'NormalizeFile',
                    'label': 'normalize-crlf',
                    'file': 'notes.txt',
                    'line_ending': 'CRLF',
                    'ensure_final_newline': True,
                    'strip_trailing_spaces': True,
                }
            ]
            _ctx, _ops, _pf, _pv, results = apply_ops(root, rows)
            self.assertEqual('applied', results[0].patch_status)
            self.assertEqual(expected, read_text(target))

    def test_semantic_family_updates_json_yaml_toml_and_python(self) -> None:
        with fixture_workspace('semantic_fixture') as root:
            rows = [
                {
                    'type': 'SetJsonValue',
                    'label': 'set-json-port',
                    'file': 'settings.json',
                    'json_pointer': '/service/port',
                    'value': 9000,
                },
                {
                    'type': 'MergeJsonObject',
                    'label': 'merge-json-flags',
                    'file': 'settings.json',
                    'json_pointer': '/service',
                    'object_value': {'enabled': True},
                },
                {
                    'type': 'SetYamlValue',
                    'label': 'set-yaml-host',
                    'file': 'docker-compose.yml',
                    'yaml_path': 'services.web.environment.HOST',
                    'value': '0.0.0.0',
                },
                {
                    'type': 'SetTomlValue',
                    'label': 'set-toml-version',
                    'file': 'pyproject.toml',
                    'toml_path': 'tool.capatch.version',
                    'value': '6.0.0',
                },
                {
                    'type': 'EnsurePythonImport',
                    'label': 'ensure-import',
                    'file': 'module.py',
                    'module': 'pathlib',
                    'symbol': 'Path',
                },
                {
                    'type': 'SetPythonConstant',
                    'label': 'set-constant',
                    'file': 'module.py',
                    'name': 'MEANING',
                    'value': 42,
                },
                {
                    'type': 'InsertPythonFunctionArg',
                    'label': 'insert-arg',
                    'file': 'module.py',
                    'function_name': 'build_message',
                    'arg_name': 'suffix',
                    'default_value': 'ok',
                },
            ]
            _ctx, _ops, _pf, _pv, results = apply_ops(root, rows)
            self.assertTrue(all(item.patch_status in {'applied', 'noop'} for item in results))

            settings = read_json(root / 'settings.json')
            self.assertEqual(9000, settings['service']['port'])
            self.assertTrue(settings['service']['enabled'])

            compose = read_text(root / 'docker-compose.yml')
            self.assertIn('HOST: 0.0.0.0', compose)

            pyproject = read_text(root / 'pyproject.toml')
            self.assertIn('version = "6.0.0"', pyproject)

            module_text = read_text(root / 'module.py')
            self.assertIn('from pathlib import Path', module_text)
            self.assertIn('MEANING = 42', module_text)
            self.assertIn("def build_message(name, suffix='ok'):", module_text)

            verifier_rows = run_required_verifiers(
                [
                    str(root / 'settings.json'),
                    str(root / 'module.py'),
                    str(root / 'pyproject.toml'),
                    str(root / 'docker-compose.yml'),
                ],
                ['json-parse', 'python-parse', 'python-compile-smoke', 'python-import-smoke', 'toml-parse', 'yaml-parse'],
                {'root_dir': str(root)},
            )
            self.assertTrue(verifier_rows)
            self.assertTrue(all(row['ok'] for row in verifier_rows), verifier_rows)

    def test_strategy_selector_prefers_exact_for_single_file_anchor_patch(self) -> None:
        with fixture_workspace('golden_replace_exact') as root:
            ctx = make_ctx(root)
            ops = build_ops([
                {
                    'type': 'EnsureReplaceExactOnce',
                    'label': 'meaning-42',
                    'file': 'app.py',
                    'old_text': '    return 41\n',
                    'new_text': '    return 42\n',
                }
            ])
            pf = preflight(ctx, ops)
            risk = classify_change(pf, ops)
            decision = select_patch_strategy(ctx, pf, ops, risk)
            self.assertEqual('exact', decision['selected_strategy'])
            self.assertFalse(decision['advisory_only'])
            self.assertEqual('exact', decision['candidate_ranking'][0]['strategy'])

    def test_strategy_selector_prefers_guarded_for_multi_file_fragile_batch(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_golden_guarded_') as tmp_dir:
            root = Path(tmp_dir)
            pkg = root / 'pkg'
            pkg.mkdir(parents=True, exist_ok=True)
            (pkg / 'a.py').write_text('A=1\n', encoding='utf-8')
            (pkg / 'b.py').write_text('B=1\n', encoding='utf-8')
            ctx = make_ctx(root)
            ops = build_ops([
                {
                    'type': 'EnsureReplaceExactOnce',
                    'label': 'a',
                    'file': 'pkg/a.py',
                    'old_text': 'A=1\n',
                    'new_text': 'A=2\n',
                },
                {
                    'type': 'EnsureReplaceExactOnce',
                    'label': 'b',
                    'file': 'pkg/b.py',
                    'old_text': 'B=1\n',
                    'new_text': 'B=2\n',
                },
            ])
            pf = preflight(ctx, ops)
            risk = classify_change(pf, ops)
            decision = select_patch_strategy(ctx, pf, ops, risk)
            self.assertEqual('guarded', decision['selected_strategy'])
            self.assertIn('transaction-review', decision['recommended_guardrails'])

    def test_typescript_structural_helpers_and_verifier_smoke(self) -> None:
        with tempfile.TemporaryDirectory(prefix='capatch_golden_ts_') as tmp_dir:
            root = Path(tmp_dir)
            target = root / 'Widget.tsx'
            original = "import React from 'react';\n\nexport function Widget() {\n    return <div>Hello barrio</div>;\n}\n"
            target.write_text(original, encoding='utf-8')
            with_import = render_ts_ensure_import(target, original, 'react', 'useMemo', 'ensure-usememo')
            with_import_twice = render_ts_ensure_import(target, with_import, 'react', 'useMemo', 'ensure-usememo')
            wrapped = render_ts_wrap_jsx_text(target, with_import_twice, 'Hello barrio', 't(\"hello.barrio\")', 'wrap-jsx')
            self.assertEqual(1, with_import_twice.count("import { useMemo } from 'react';"))
            self.assertIn('{t("hello.barrio")}', wrapped)
            target.write_text("import { useState } from 'react';\n\nexport function Widget() {\n    const [count] = useState(0);\n    return <div>{count}</div>;\n}\n", encoding='utf-8')
            with patch('capatch_verify.builtin_typescript.shutil.which', return_value=None):
                verifier_rows = run_required_verifiers([str(target)], ['typescript-parse'], {'root_dir': str(root)})
            self.assertEqual(1, len(verifier_rows))
            self.assertFalse(verifier_rows[0]['ok'])
            self.assertIn('use client', verifier_rows[0]['detail'])


if __name__ == '__main__':
    unittest.main()
