import json, unittest
from unittest.mock import patch
from visual_application.engine import preview,apply,verify,rollback_transaction
from visual_application.hashing import sha256_file
from visual_application.transaction import create_transaction,mark_after,rollback,load_transaction
from visual_application.errors import ProjectionFailure,RollbackWouldOverwriteNewerWork,TamperedBackup,TamperedTransaction
from .helpers import make_repo

class EngineTransactionTests(unittest.TestCase):
    def setUp(self):
        self.td,self.root,self.source,self.output,self.manifest,self.tx,self.provider,self.request,self.auth=make_repo()
        self.before=self.source.read_bytes(); self.out_before=self.output.read_bytes(); self.man_before=self.manifest.read_bytes()
    def tearDown(self): self.td.cleanup()
    def test_preview_is_read_only(self):
        r=preview(self.request('PREVIEW'),self.provider,self.root)
        self.assertEqual(r['status'],'CHANGE_PLANNED'); self.assertEqual(self.source.read_bytes(),self.before)
    def test_apply_projects_and_never_claims_runtime(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        self.assertEqual(r['status'],'APPLIED_SOURCE_STATIC'); self.assertFalse(r['runtimeVisualGreen']); self.assertEqual(self.output.read_bytes(),self.source.read_bytes())
    def test_apply_idempotent_with_fresh_hash(self):
        apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        self.assertEqual(r['status'],'IDEMPOTENT_NO_CHANGE')
    def test_verify_static_green_only(self):
        apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        r=verify(self.request('VERIFY'),self.provider,self.root)
        self.assertEqual(r['status'],'STATIC_GREEN'); self.assertFalse(r['ready'])
    def test_exact_rollback(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        rr=rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx)
        self.assertEqual(rr['status'],'ROLLED_BACK'); self.assertEqual(self.source.read_bytes(),self.before)
        self.assertEqual(self.output.read_bytes(),self.out_before); self.assertEqual(self.manifest.read_bytes(),self.man_before)
    def test_second_rollback_is_idempotent(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx)
        rr=rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx)
        self.assertEqual(rr['status'],'ALREADY_ROLLED_BACK')
    def test_rollback_refuses_newer_work(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth); self.source.write_text('.button { color: purple; }',encoding='utf-8')
        with self.assertRaises(RollbackWouldOverwriteNewerWork): rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx)
    def test_tampered_backup_blocks(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        tx=load_transaction(self.tx,r['transactionId']); row=next(x for x in tx['files'] if x['backupPath'])
        (self.tx/r['transactionId']/row['backupPath']).write_bytes(b'tampered')
        with self.assertRaises(TamperedBackup): rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx)
    def test_projection_failure_auto_rolls_back(self):
        with patch('visual_application.engine.project',side_effect=ProjectionFailure('boom')):
            with self.assertRaises(ProjectionFailure): apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        self.assertEqual(self.source.read_bytes(),self.before); self.assertEqual(self.output.read_bytes(),self.out_before); self.assertEqual(self.manifest.read_bytes(),self.man_before)
    def test_two_phase_validation_prevents_partial_rollback(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        tx=load_transaction(self.tx,r['transactionId'])
        rows=[x for x in tx['files'] if x['backupPath']]
        last=rows[-1]; (self.tx/r['transactionId']/last['backupPath']).write_bytes(b'tampered')
        post={x['path']:(self.root/x['path']).read_bytes() if (self.root/x['path']).exists() else None for x in tx['files']}
        with self.assertRaises(TamperedBackup): rollback_transaction(r['transactionId'],'TGT.TEST',self.root,self.tx)
        for path,data in post.items():
            p=self.root/path
            self.assertEqual(p.read_bytes() if p.exists() else None,data)
    def test_after_none_protects_newer_file(self):
        new=self.root/'prisma-html/authority/rifat/new.css'
        tx=create_transaction(self.root,self.tx,'gvae-newfile','TGT.TEST',[new],'a'*40)
        mark_after(self.root,self.tx,tx)
        new.parent.mkdir(parents=True,exist_ok=True); new.write_text('new work',encoding='utf-8')
        with self.assertRaises(RollbackWouldOverwriteNewerWork): rollback(self.root,self.tx,load_transaction(self.tx,'gvae-newfile'))
    def test_transaction_metadata_digest_detects_tamper(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        p=self.tx/r['transactionId']/'transaction.json'; doc=json.loads(p.read_text()); doc['targetId']='TGT.OTHER'; p.write_text(json.dumps(doc),encoding='utf-8')
        with self.assertRaises(TamperedTransaction): load_transaction(self.tx,r['transactionId'])
    def test_rollback_target_is_transaction_bound(self):
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        with self.assertRaises(TamperedTransaction): rollback_transaction(r['transactionId'],'TGT.OTHER',self.root,self.tx)
    def test_transaction_id_traversal_blocks(self):
        r=self.request('APPLY'); r['transactionId']='../../evil'
        from visual_application.contracts import load_request
        from visual_application.errors import ContractError
        with self.assertRaises(ContractError): load_request(r)
    def test_idempotent_apply_repairs_projection_drift(self):
        apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        source_now=self.source.read_bytes(); self.output.write_text('drift',encoding='utf-8')
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        self.assertEqual(r['status'],'REPAIRED_PROJECTION_DRIFT'); self.assertEqual(self.source.read_bytes(),source_now); self.assertEqual(self.output.read_bytes(),source_now)
    def test_idempotent_apply_repairs_manifest_drift(self):
        apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        doc=json.loads(self.manifest.read_text()); doc['entries'][0]['outputSha256']='0'*64; self.manifest.write_text(json.dumps(doc),encoding='utf-8')
        r=apply(self.request('APPLY'),self.provider,self.root,self.tx,self.auth)
        self.assertEqual(r['status'],'REPAIRED_PROJECTION_DRIFT')
        fixed=json.loads(self.manifest.read_text()); self.assertEqual(fixed['entries'][0]['outputSha256'],sha256_file(self.output))
