import unittest
from visual_application.contracts import load_request
from visual_application.errors import ContractError
from .helpers import make_repo

class ContractTests(unittest.TestCase):
    def setUp(self): self.td,self.root,*rest=make_repo(); self.req=rest[-1]('PREVIEW')
    def tearDown(self): self.td.cleanup()
    def test_valid(self): self.assertEqual(load_request(self.req)['mode'],'PREVIEW')
    def test_extra_root_field_blocks(self):
        r=dict(self.req); r['surprise']=1
        with self.assertRaises(ContractError): load_request(r)
    def test_missing_authority_blocks(self):
        r=dict(self.req); del r['adapterId']
        with self.assertRaises(ContractError): load_request(r)
    def test_surface_must_be_included(self):
        r=dict(self.req); r['includeSurfaces']=['pc']
        with self.assertRaises(ContractError): load_request(r)
    def test_include_exclude_overlap_blocks(self):
        r=dict(self.req); r['excludeSurfaces']=['tablet']
        with self.assertRaises(ContractError): load_request(r)
    def test_unknown_operation_type_blocks(self):
        r=dict(self.req); r['operations']=[{"type":"domMutation","path":"x","values":{"x":1}}]
        with self.assertRaises(ContractError): load_request(r)
    def test_operation_extra_field_blocks(self):
        r=dict(self.req); r['operations']=[{"type":"cssDeclarations","path":".button","values":{"color":"blue"},"extra":1}]
        with self.assertRaises(ContractError): load_request(r)
