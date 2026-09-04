import hashlib,json,unittest
from pathlib import Path
from visual_application.target_index import ROOT,OUT,build_index,render_files,SUPPORTED_PROJECTION_MODES,CENSUS_KIND,DISCOVERY_ONLY,SURFACES

REPO_ROOT=ROOT.parent
class FullCheckoutTests(unittest.TestCase):
    def test_code_atlas_application_stays_disabled(self):
        p=REPO_ROOT/'tools/code-atlas/src/code_atlas/ui_bridge/application.py'; self.assertTrue(p.is_file())
        text=p.read_text(encoding='utf-8'); self.assertIn('"applicationEnabled": False',text); self.assertIn('"runtimeMutationAllowed": False',text); self.assertIn('"productApplicationAllowed": False',text)
    def test_historical_cobrar_constants_stay_frozen(self):
        p=REPO_ROOT/'tools/code-atlas/src/code_atlas/ui_bridge/cobrar_application.py'; self.assertTrue(p.is_file())
        text=p.read_text(encoding='utf-8'); self.assertIn('BINDING_ID = "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1"',text); self.assertIn('LAYER_ID = "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE"',text); self.assertIn('ADAPTER_ID = "ADP.TB.TOUCH.V2"',text)
    def test_current_manifest_modes_are_supported(self):
        doc=json.loads((ROOT/'authority/rifat/visual-source-manifest.json').read_text()); modes={e['projectionMode'] for e in doc['entries']}; self.assertTrue(modes); self.assertLessEqual(modes,SUPPORTED_PROJECTION_MODES)
    def test_target_index_is_deterministic_and_fail_closed(self):
        a=build_index(); b=build_index(); self.assertEqual(a,b); self.assertFalse(a['globalBlockers']); self.assertGreaterEqual(a['recordCount'],1); self.assertEqual([r for r in a['records'] if r['targetId']=='TGT.TABLET.POS.COBRAR.PRIMARY.V1'][0]['status'],'BLOCKED')
    def test_target_index_does_not_infer_cobrar_adapter(self):
        row=[r for r in build_index()['records'] if r['targetId']=='TGT.TABLET.POS.COBRAR.PRIMARY.V1'][0]; self.assertIsNone(row['adapterId']); self.assertIn('adapter',row['blockers'])
    def test_target_index_respects_layer_application_policy(self):
        row=[r for r in build_index()['records'] if r['targetId']=='TGT.TABLET.POS.COBRAR.PRIMARY.V1'][0]; self.assertIn('layer-application-policy',row['blockers'])
    def test_target_index_represents_all_surfaces_without_fake_ready(self):
        index=build_index()
        self.assertTrue(index['coverage']['allSurfacesRepresented'])
        self.assertEqual(set(index['coverage']['bySurface']),set(SURFACES))
        self.assertGreater(index['countsByKind'].get(CENSUS_KIND,0),0)
        self.assertEqual(index['coverage']['wholeSurfaceApplyReadyCount'],0)
        census=[row for row in index['records'] if row['recordKind']==CENSUS_KIND]
        self.assertTrue(census)
        self.assertTrue(all(row['enforcement']==DISCOVERY_ONLY and row['status']=='BLOCKED' for row in census))

    def test_committed_manifest_stores_enforced_records_without_census_duplication(self):
        index=build_index()
        files=render_files(index)
        manifest=json.loads(files[OUT/'manifest.json'].decode('utf-8'))
        self.assertFalse(manifest['recordStorage']['censusDuplicatedInManifest'])
        self.assertEqual(manifest['recordStorage']['totalRecordCount'],index['recordCount'])
        self.assertTrue(all(row.get('enforcement')!=DISCOVERY_ONLY for row in manifest['records']))
        surface_views=[
            json.loads(files[OUT/f'{surface}.json'].decode('utf-8'))
            for surface in SURFACES
        ]
        self.assertTrue(any(
            row.get('recordKind')==CENSUS_KIND
            for view in surface_views for row in view['records']
        ))

    def test_factory_ledger_mutation_gate_is_bound_into_engine(self):
        p=ROOT/'tools/visual_application/authority.py'; text=p.read_text(encoding='utf-8')
        self.assertIn('PASS_ANTI_REWORK_GATE',text); self.assertIn('verify_prisma_anti_rework_gate.py',text); self.assertIn('PASS_COMPOSED_AUTHORITY_MESH',text)
    def test_master_map_is_exact_original(self):
        p=ROOT/'docs/ops/PRISMA_VISUAL_CHANGE_MASTER_MAP.md'; self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),'87d1a7cd375ed8b4c0a264a74f1e1d75921d704b4d9da62e53d427a3ac05662d')
