import unittest
from visual_application.preflight import preflight,resolve_target
from visual_application.errors import *
from .helpers import make_repo

class PreflightTests(unittest.TestCase):
    def setUp(self): self.td,self.root,self.source,self.output,self.manifest,self.tx,self.provider,self.request=make_repo()
    def tearDown(self): self.td.cleanup()
    def test_valid_exact_target(self): self.assertEqual(preflight(self.request('PREVIEW'),self.provider(),self.root)['targetId'],'TGT.TEST')
    def test_target_missing(self):
        with self.assertRaises(TargetNotFound): resolve_target({'records':[]},'x')
    def test_target_ambiguous(self):
        with self.assertRaises(AmbiguousTarget): resolve_target({'records':[{'targetId':'x'},{'targetId':'x'}]},'x')
    def _field(self,field,exc):
        index=self.provider(); index['records'][0][field]=None
        with self.assertRaises(exc): preflight(self.request('PREVIEW'),index,self.root)
    def test_missing_binding(self): self._field('bindingId',MissingBinding)
    def test_missing_layer(self): self._field('layerId',MissingLayer)
    def test_missing_adapter(self): self._field('adapterId',MissingAdapter)
    def test_missing_recipe(self): self._field('recipeId',MissingRecipe)
    def test_missing_semantic(self): self._field('semanticMeaningId',MissingSemantic)
    def test_stale_hash(self):
        r=self.request('PREVIEW'); r['expectedSourceSha256']='0'*64
        with self.assertRaises(StaleSourceHash): preflight(r,self.provider(),self.root)
    def test_surface_expansion(self):
        r=self.request('PREVIEW'); r['surface']='pc'; r['includeSurfaces']=['pc']
        with self.assertRaises(SurfaceExpansion): preflight(r,self.provider(),self.root)
    def test_unsupported_projection_mode(self):
        i=self.provider(); i['records'][0]['projectionMode']='magic'
        with self.assertRaises(UnsupportedProjectionMode): preflight(self.request('PREVIEW'),i,self.root)
    def test_direct_product_source_blocks(self):
        i=self.provider(); i['records'][0]['canonicalSourcePath']='apps/terminal-de-venta-system/products/tablet/test.css'
        with self.assertRaises(DirectGeneratedProductWrite): preflight(self.request('PREVIEW'),i,self.root)
