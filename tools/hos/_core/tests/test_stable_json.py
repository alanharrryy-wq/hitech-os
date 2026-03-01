from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.hos._core.stable_json import dump_json, load_json_text, write_json


class StableJsonTests(unittest.TestCase):
    def test_dump_sorted_and_trailing_newline(self) -> None:
        payload = {"z": 1, "a": 2}
        rendered = dump_json(payload)
        self.assertTrue(rendered.endswith("\n"))
        self.assertLess(rendered.find('"a"'), rendered.find('"z"'))

    def test_relaxed_loader_comments_and_trailing_comma(self) -> None:
        raw = """
        {
          // line comment
          "name": "demo", /* block comment */
          "values": [1, 2, 3,],
        }
        """
        parsed = load_json_text(raw, allow_relaxed=True)
        self.assertEqual(parsed["name"], "demo")
        self.assertEqual(parsed["values"], [1, 2, 3])

    def test_write_json_uses_unix_newlines(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "payload.json"
            write_json(target, {"b": 1, "a": 2})
            data = target.read_bytes()
            self.assertNotIn(b"\r\n", data)
            self.assertTrue(data.endswith(b"\n"))


if __name__ == "__main__":
    unittest.main()

