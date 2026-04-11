from __future__ import annotations

import unittest

from tooling.run_windows_smoke import DEFAULT_REQUIRED_PLUGINS, determine_smoke_status, parse_required_plugins


class WindowsSmokeRequiredPluginsDefaultTests(unittest.TestCase):
    def test_default_required_plugins_used_when_env_missing(self) -> None:
        self.assertEqual(list(DEFAULT_REQUIRED_PLUGINS), parse_required_plugins(None))

    def test_override_empty_falls_back_to_default(self) -> None:
        self.assertEqual(list(DEFAULT_REQUIRED_PLUGINS), parse_required_plugins(' , ; '))

    def test_failed_when_required_plugins_missing(self) -> None:
        steps = [
            {'name': 'smoke-test', 'returncode': 0, 'stdout': '', 'stderr': ''},
            {'name': 'plugin-health', 'returncode': 0, 'stdout': 'fixer.safe-runtime-actions', 'stderr': ''},
            {'name': 'apply', 'returncode': 0, 'stdout': '', 'stderr': ''},
            {'name': 'rollback-last', 'returncode': 0, 'stdout': '', 'stderr': ''},
        ]
        status, reason, detail = determine_smoke_status(
            steps,
            required_plugins=list(DEFAULT_REQUIRED_PLUGINS),
        )
        self.assertEqual('failed', status)
        self.assertIn('missing required plugins', reason)
        self.assertIn('verifier.post-fix-verifier', detail['missing'])


if __name__ == '__main__':
    unittest.main()
