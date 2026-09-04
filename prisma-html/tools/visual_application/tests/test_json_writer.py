import unittest,json
from visual_application.json_writer import patch_json_bytes
from visual_application.errors import ContractError,TargetNotFound

class JsonWriterTests(unittest.TestCase):
    def data(self): return b'{"a":{"b":1,"s":"x","flag":true},"arr":[1,2]}\n'
    def test_scalar_replace(self): self.assertEqual(json.loads(patch_json_bytes(self.data(),{'/a/b':2}))['a']['b'],2)
    def test_string_replace(self): self.assertEqual(json.loads(patch_json_bytes(self.data(),{'/a/s':'y'}))['a']['s'],'y')
    def test_array_replace(self): self.assertEqual(json.loads(patch_json_bytes(self.data(),{'/arr/1':3}))['arr'][1],3)
    def test_missing_pointer_blocks(self):
        with self.assertRaises(TargetNotFound): patch_json_bytes(self.data(),{'/a/nope':2})
    def test_root_pointer_blocks(self):
        with self.assertRaises(ContractError): patch_json_bytes(self.data(),{'/':2})
    def test_type_change_blocks(self):
        with self.assertRaises(ContractError): patch_json_bytes(self.data(),{'/a/b':'2'})
    def test_structural_change_blocks(self):
        with self.assertRaises(ContractError): patch_json_bytes(self.data(),{'/a/b':{'x':1}})
    def test_expected_current_blocks_drift(self):
        with self.assertRaises(ContractError): patch_json_bytes(self.data(),{'/a/b':2},{'/a/b':9})
    def test_output_is_deterministic(self): self.assertEqual(patch_json_bytes(self.data(),{'/a/b':2}),patch_json_bytes(self.data(),{'/a/b':2}))
    def test_negative_array_index_blocks(self):
        with self.assertRaises(TargetNotFound): patch_json_bytes(self.data(),{'/arr/-1':3})
    def test_leading_zero_array_index_blocks(self):
        with self.assertRaises(TargetNotFound): patch_json_bytes(self.data(),{'/arr/01':3})
    def test_pointer_must_stay_under_governed_root(self):
        with self.assertRaises(ContractError): patch_json_bytes(self.data(),{'/arr/1':3},root='/a')
    def test_expected_current_must_cover_all_mutations(self):
        with self.assertRaises(ContractError): patch_json_bytes(self.data(),{'/a/b':2},{})
    def test_nonfinite_input_json_blocks(self):
        with self.assertRaises(ContractError): patch_json_bytes(b'{"a":NaN}\n',{'/a':1})
    def test_nonfinite_desired_blocks(self):
        with self.assertRaises(ContractError): patch_json_bytes(self.data(),{'/a/b':float('nan')})
