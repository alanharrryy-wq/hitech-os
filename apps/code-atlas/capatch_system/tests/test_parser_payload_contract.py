from __future__ import annotations

import unittest

from capatch_engine import parse_operations
from capatch_ops.base import CapatchError


def _replace_exact_op() -> dict[str, object]:
    return {
        "type": "EnsureReplaceExactOnce",
        "label": "meaning-42",
        "file": "pkg/service.py",
        "old_text": "    return 41\n",
        "new_text": "    return 42\n",
    }


class ParserPayloadContractTests(unittest.TestCase):
    def test_accepts_root_list(self) -> None:
        ops = parse_operations([_replace_exact_op()])
        self.assertEqual(1, len(ops))
        self.assertEqual("EnsureReplaceExactOnce", ops[0].type)
        self.assertEqual("pkg/service.py", ops[0].file)

    def test_accepts_object_with_operations(self) -> None:
        ops = parse_operations({"operations": [_replace_exact_op()]})
        self.assertEqual(1, len(ops))
        self.assertEqual("EnsureReplaceExactOnce", ops[0].type)

    def test_accepts_object_with_payload_list(self) -> None:
        ops = parse_operations({"payload": [_replace_exact_op()]})
        self.assertEqual(1, len(ops))
        self.assertEqual("EnsureReplaceExactOnce", ops[0].type)

    def test_accepts_object_with_payload_operations(self) -> None:
        ops = parse_operations({"payload": {"operations": [_replace_exact_op()]}})
        self.assertEqual(1, len(ops))
        self.assertEqual("EnsureReplaceExactOnce", ops[0].type)

    def test_accepts_single_operation_object(self) -> None:
        ops = parse_operations(_replace_exact_op())
        self.assertEqual(1, len(ops))
        self.assertEqual("EnsureReplaceExactOnce", ops[0].type)

    def test_rejects_legacy_ops_key_with_clear_error(self) -> None:
        with self.assertRaises(CapatchError) as raised:
            parse_operations({"ops": [_replace_exact_op()]})
        self.assertIn("El campo 'ops' no esta soportado", str(raised.exception))

    def test_rejects_path_field_without_file(self) -> None:
        payload = dict(_replace_exact_op())
        payload.pop("file")
        payload["path"] = "pkg/service.py"
        with self.assertRaises(CapatchError) as raised:
            parse_operations(payload)
        self.assertIn("no trae file", str(raised.exception))

    def test_requires_fields_for_ensure_replace_exact_once(self) -> None:
        payload = dict(_replace_exact_op())
        payload.pop("new_text")
        with self.assertRaises(CapatchError) as raised:
            parse_operations(payload)
        self.assertIn("requiere new_text", str(raised.exception))

    def test_requires_fields_for_set_toml_value(self) -> None:
        payload = {
            "type": "SetTomlValue",
            "label": "set-version",
            "file": "pyproject.toml",
            "value": "1.2.3",
        }
        with self.assertRaises(CapatchError) as raised:
            parse_operations(payload)
        self.assertIn("requiere toml_path", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
