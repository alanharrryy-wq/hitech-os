import json, unittest
from visual_application.authority import verify_mesh_artifact,verify_ui_bridge_plan
from visual_application.errors import AuthorizationError,PlanBindingError
from visual_application.hashing import sha256_file
from .helpers import make_repo,make_mesh_artifact,make_plan

class AuthorityHardeningTests(unittest.TestCase):
    def setUp(self):
        self.td,self.root,self.source,self.output,self.manifest,self.tx,self.provider,self.request,self.authfn=make_repo()
        self.target=self.provider()['records'][0]
        mesh,mesh_sha,digest=make_mesh_artifact(self.root)
        pp,ps,dp,ds=make_plan(self.root,self.target)
        self.auth={"task":"Synthetic governed visual application test.","authorityTaskId":"gvae-test",
                   "authorityMeshArtifact":mesh,"authorityMeshArtifactSha256":mesh_sha,
                   "authorityMeshRequestDigest":digest,"uiBridgePlanPath":pp,"uiBridgePlanSha256":ps,
                   "uiBridgeSemanticDiffPath":dp,"uiBridgeSemanticDiffSha256":ds}
    def tearDown(self): self.td.cleanup()
    def test_mesh_artifact_is_verified_structurally(self):
        out=verify_mesh_artifact(self.auth,self.root,'a'*40)
        self.assertEqual(out['status'],'PASS_COMPOSED_AUTHORITY_MESH'); self.assertTrue(out['layerMapPresent'])
    def test_mesh_hash_mismatch_blocks(self):
        a=dict(self.auth); a['authorityMeshArtifactSha256']='0'*64
        with self.assertRaises(AuthorizationError): verify_mesh_artifact(a,self.root,'a'*40)
    def test_mesh_stale_head_blocks(self):
        with self.assertRaises(AuthorizationError): verify_mesh_artifact(self.auth,self.root,'f'*40)
    def test_mesh_missing_exact_task_layer_map_blocks(self):
        a=dict(self.auth); a['authorityTaskId']='other-task'
        with self.assertRaises(AuthorizationError): verify_mesh_artifact(a,self.root,'a'*40)
    def test_ui_bridge_plan_binds_exact_selector_and_property(self):
        req=self.request('APPLY'); out=verify_ui_bridge_plan(self.auth,self.root,self.target,req)
        self.assertTrue(out['planId'].startswith('BRPLAN.'))
    def test_ui_bridge_plan_rejects_unreviewed_property(self):
        req=self.request('APPLY'); req['operations'][0]['values']['padding']='2px'
        with self.assertRaises(PlanBindingError): verify_ui_bridge_plan(self.auth,self.root,self.target,req)
    def test_ui_bridge_plan_rejects_selector_drift(self):
        req=self.request('APPLY'); req['operations'][0]['path']='.other'
        with self.assertRaises(PlanBindingError): verify_ui_bridge_plan(self.auth,self.root,self.target,req)
    def test_ui_bridge_plan_hash_mismatch_blocks(self):
        a=dict(self.auth); a['uiBridgePlanSha256']='0'*64
        with self.assertRaises(PlanBindingError): verify_ui_bridge_plan(a,self.root,self.target,self.request('APPLY'))
    def test_semantic_diff_checksum_tamper_blocks(self):
        p=self.root/self.auth['uiBridgeSemanticDiffPath']; d=json.loads(p.read_text()); d['checksum']='0'*64; p.write_text(json.dumps(d),encoding='utf-8')
        a=dict(self.auth); a['uiBridgeSemanticDiffSha256']=sha256_file(p)
        with self.assertRaises(PlanBindingError): verify_ui_bridge_plan(a,self.root,self.target,self.request('APPLY'))
