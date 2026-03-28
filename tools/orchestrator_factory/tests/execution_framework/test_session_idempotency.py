from __future__ import annotations

from pathlib import Path

from _test_support import OneButtonFrameworkTestCase


class TestSessionIdempotency(OneButtonFrameworkTestCase):
    def setUp(self) -> None:
        framework_root = self.make_temp_framework()
        self.framework_root = framework_root
        lib_root = framework_root / 'tools' / 'execution_framework' / 'lib'
        import sys

        if str(lib_root) not in sys.path:
            sys.path.insert(0, str(lib_root))
        from session_idempotency import SessionIdempotencyManager  # type: ignore
        from session_ledger import LedgerEntry, SessionLedger  # type: ignore

        self.SessionIdempotencyManager = SessionIdempotencyManager
        self.SessionLedger = SessionLedger
        self.LedgerEntry = LedgerEntry
        self.ledger_path = framework_root / 'ops' / 'projects' / 'idp_demo' / 'state' / 'sessions' / 'session_ledger.jsonl'

    def test_missing_manifests_use_none_sentinels(self) -> None:
        ledger = self.SessionLedger(self.ledger_path)
        manager = self.SessionIdempotencyManager(ledger)
        project_manifest = self.framework_root / 'ops' / 'projects' / 'idp_demo' / 'project_manifest.json'
        run_manifest = self.framework_root / 'ops' / 'projects' / 'idp_demo' / 'runs' / 'run_001' / 'run_manifest.json'
        round_manifest = self.framework_root / 'ops' / 'projects' / 'idp_demo' / 'runs' / 'run_001' / 'rounds' / 'round_001' / 'round_manifest.json'
        context = manager.compute(
            session_mode='new_project',
            policy='open_new_round',
            project_id='idp_demo',
            normalized_intent='Boot the project cleanly',
            target_run_id='run_001',
            target_round_id='round_001',
            project_manifest_path=project_manifest,
            run_manifest_path=run_manifest,
            round_manifest_path=round_manifest,
        )
        self.assertEqual(context.context_hashes['project_manifest_sha256'], 'none')
        self.assertEqual(context.context_hashes['run_manifest_sha256'], 'none')
        self.assertEqual(context.context_hashes['round_manifest_sha256'], 'none')
        self.assertEqual(context.decision, 'new_session')
        self.assertIsNone(context.reusable_entry)

    def test_ledger_entry_can_be_reused_when_zip_exists(self) -> None:
        zip_path = self.framework_root / 'ops' / 'projects' / 'idp_demo' / 'bundles' / 'sessions' / 'session_a.zip'
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        zip_path.write_bytes(b'zip-placeholder')
        ledger = self.SessionLedger(self.ledger_path)
        ledger.append(
            self.LedgerEntry(
                session_id='session_a',
                created_at_utc='2026-03-27T18:22:10Z',
                session_mode='existing_project',
                policy='open_new_round',
                project_id='idp_demo',
                run_id='run_001',
                round_id='round_002',
                idempotency_key='abc123',
                status='ready_for_dispatch',
                session_zip_path=str(zip_path),
                handoff_copy_path=None,
                lock_id='lock_a',
            )
        )
        manager = self.SessionIdempotencyManager(ledger)
        context = manager.compute(
            session_mode='existing_project',
            policy='open_new_round',
            project_id='idp_demo',
            normalized_intent='Continue execution',
            target_run_id='run_001',
            target_round_id='round_002',
            project_manifest_path=self.framework_root / 'missing_project_manifest.json',
            run_manifest_path=self.framework_root / 'missing_run_manifest.json',
            round_manifest_path=self.framework_root / 'missing_round_manifest.json',
        )
        # Force the same digest to match the seeded ledger entry and verify the reusable scan independently.
        self.assertIsNone(context.reusable_entry)
        self.assertIsNotNone(ledger.find_reusable('abc123'))
        self.assertEqual(ledger.find_reusable('abc123').session_id, 'session_a')


if __name__ == '__main__':
    import unittest

    unittest.main()
