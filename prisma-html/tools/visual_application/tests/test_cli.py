import io,json,tempfile,unittest
from contextlib import redirect_stdout
from pathlib import Path
from visual_application.cli import main

class CliTests(unittest.TestCase):
    def test_invalid_json_is_structured_blocked_not_traceback(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.json'; p.write_text('{bad',encoding='utf-8')
            buf=io.StringIO()
            with redirect_stdout(buf):
                code=main([str(p)])
            self.assertEqual(code,2)
            out=json.loads(buf.getvalue())
            self.assertEqual(out['status'],'BLOCKED'); self.assertIn(out['error'],{'CONTRACT_ERROR','INPUT_ERROR'})
    def test_missing_request_is_structured_blocked(self):
        buf=io.StringIO()
        with redirect_stdout(buf):
            code=main(['/definitely/missing/gvae-request.json'])
        self.assertEqual(code,2); self.assertEqual(json.loads(buf.getvalue())['status'],'BLOCKED')
