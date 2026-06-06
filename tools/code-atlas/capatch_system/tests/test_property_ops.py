
from __future__ import annotations

import json
import random
import string
import tempfile
import unittest
from pathlib import Path

from tests.qa_testkit import apply_ops, make_ctx, write_text


class PropertyStyleTests(unittest.TestCase):
    def _token(self, rng: random.Random, prefix: str) -> str:
        alphabet = string.ascii_letters + string.digits
        return prefix + "_" + "".join(rng.choice(alphabet) for _ in range(12))

    def test_ensure_replace_exact_once_is_idempotent_under_random_inputs(self) -> None:
        rng = random.Random(9001)
        for index in range(20):
            with self.subTest(case=index):
                with tempfile.TemporaryDirectory(prefix="capatch_prop_exact_") as tmp_dir:
                    root = Path(tmp_dir)
                    old = self._token(rng, "old")
                    new = self._token(rng, "new")
                    target = root / "sample.txt"
                    write_text(target, f"header\n{old}\nfooter\n")
                    rows = [
                        {
                            "type": "EnsureReplaceExactOnce",
                            "label": "ensure-random",
                            "file": "sample.txt",
                            "old_text": f"{old}\n",
                            "new_text": f"{new}\n",
                        }
                    ]
                    _ctx1, _ops1, _pf1, _pv1, results1 = apply_ops(root, rows)
                    self.assertEqual("applied", results1[0].patch_status)
                    _ctx2, _ops2, _pf2, _pv2, results2 = apply_ops(root, rows)
                    self.assertEqual("noop", results2[0].patch_status)
                    self.assertIn(new, target.read_text(encoding="utf-8"))

    def test_set_json_value_is_idempotent_under_random_values(self) -> None:
        rng = random.Random(1337)
        for index in range(15):
            with self.subTest(case=index):
                with tempfile.TemporaryDirectory(prefix="capatch_prop_json_") as tmp_dir:
                    root = Path(tmp_dir)
                    target = root / "settings.json"
                    target.write_text('{"service": {"port": 8000}}\n', encoding="utf-8")
                    value = rng.randint(8100, 8999)
                    rows = [
                        {
                            "type": "SetJsonValue",
                            "label": "set-port",
                            "file": "settings.json",
                            "json_pointer": "/service/port",
                            "value": value,
                        }
                    ]
                    _ctx1, _ops1, _pf1, _pv1, results1 = apply_ops(root, rows)
                    self.assertEqual("applied", results1[0].patch_status)
                    _ctx2, _ops2, _pf2, _pv2, results2 = apply_ops(root, rows)
                    self.assertEqual("noop", results2[0].patch_status)
                    payload = json.loads(target.read_text(encoding="utf-8"))
                    self.assertEqual(value, payload["service"]["port"])

    def test_normalize_file_remains_stable_after_second_pass(self) -> None:
        rng = random.Random(77)
        for index in range(10):
            with self.subTest(case=index):
                with tempfile.TemporaryDirectory(prefix="capatch_prop_norm_") as tmp_dir:
                    root = Path(tmp_dir)
                    target = root / "mixed.txt"
                    lines = [self._token(rng, "line") + "   " for _ in range(6)]
                    target.write_text("\n".join(lines), encoding="utf-8", newline="")
                    rows = [
                        {
                            "type": "NormalizeFile",
                            "label": "normalize",
                            "file": "mixed.txt",
                            "line_ending": "LF",
                            "ensure_final_newline": True,
                            "strip_trailing_spaces": True,
                        }
                    ]
                    _ctx1, _ops1, _pf1, _pv1, results1 = apply_ops(root, rows)
                    self.assertEqual("applied", results1[0].patch_status)
                    _ctx2, _ops2, _pf2, _pv2, results2 = apply_ops(root, rows)
                    self.assertEqual("noop", results2[0].patch_status)
                    content = target.read_text(encoding="utf-8")
                    self.assertTrue(content.endswith("\n"))
                    self.assertNotIn("   \n", content)


if __name__ == "__main__":
    unittest.main()
