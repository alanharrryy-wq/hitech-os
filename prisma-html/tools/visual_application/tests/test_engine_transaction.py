import unittest
from unittest.mock import patch
from visual_application.engine import preview,apply,verify,rollback_transaction
from visual_application.hashing import sha256_file
from visual_application.errors import ProjectionFailure,RollbackWouldOverwriteNewerWork,TamperedBackup
from .helpers import make_repo

class EngineTransactionTests(unittest.TestCase):
    def setUp(self): self.td,self.root,self.source,self.output,self.manifest,self.tx,self.provider,self.request=make_repo(); self.before=self.source.read_bytes(); self.out_before=self.output.read_bytes(); self.man_before=self.manifest.read_bytes()
    def tearDown(self): self.td.cleanup()
    def test_preview_is_read_only(self):
        r=preview(self.request('PREVIEW'),self.provider,self.root); self.assertEqual(r['status'],'CHANGE_PLANNED'); self.assertEqual(self.source.read_bytes(),self.before)
    def test_apply_projects_and_never_claims_runtime(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx); self.assertEqual(r['status'],'APPLIED_SOURCE_STATIC'); self.assertFalse(r['runtimeVisualGreen']); self.assertEqual(self.output.read_bytes(),self.source.read_bytes())
    def test_apply_idempotent_with_fresh_hash(self):
        apply(self.request('APPLY'),self.provider,self.root,self.tx); r=apply(self.request('APPLY'),self.provider,self.root,self.tx); self.assertEqual(r['status'],'IDEMPOTENT_NO_CHANGE')
    def test_verify_static_green_only(self):
        apply(self.request('APPLY'),self.provider,self.root,self.tx); r=verify(self.request('VERIFY'),self.provider,self.root); self.assertEqual(r['status'],'STATIC_GREEN'); self.assertFalse(r['ready'])
    def test_exact_rollback(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx); rr=rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx); self.assertEqual(rr['status'],'ROLLED_BACK'); self.assertEqual(self.source.read_bytes(),self.before); self.assertEqual(self.output.read_bytes(),self.out_before); self.assertEqual(self.manifest.read_bytes(),self.man_before)
    def test_second_rollback_is_idempotent(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx); rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx); rr=rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx); self.assertEqual(rr['status'],'ALREADY_ROLLED_BACK')
    def test_rollback_refuses_newer_work(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx); self.source.write_text('.button { color: purple; }',encoding='utf-8')
        with self.assertRaises(RollbackWouldOverwriteNewerWork): rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx)
    def test_tampered_backup_blocks(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx); import json
        tx=json.loads((self.tx/r['transactionId']/'transaction.json').read_text()); row=next(x for x in tx['files'] if x['path'].endswith('test.css') and x['backupPath']); (self.tx/r['transactionId']/row['backupPath']).write_bytes(b'tampered')
        with self.assertRaises(TamperedBackup): rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx)
    def test_projection_failure_auto_rolls_back(self):
        with patch('visual_application.engine.project',side_effect=ProjectionFailure('boom')):
            with self.assertRaises(ProjectionFailure): apply(self.request('APPLY'),self.provider,self.root,self.tx)
        self.assertEqual(self.source.read_bytes(),self.before); self.assertEqual(self.output.read_bytes(),self.out_before); self.assertEqual(self.manifest.read_bytes(),self.man_before)
