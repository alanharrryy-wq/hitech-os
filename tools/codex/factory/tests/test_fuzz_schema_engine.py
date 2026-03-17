from __future__ import annotations

import json
import os
import random
import string
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from factory.schema_engine import validate_instance  # noqa: E402


class SchemaEngineFuzzTests(unittest.TestCase):
    def _random_payload(self, rng: random.Random, depth: int = 0):
        if depth > 3:
            return rng.choice([None, True, False, rng.randint(-100, 100), "".join(rng.choice(string.ascii_letters) for _ in range(6))])
        choice = rng.randint(0, 5)
        if choice == 0:
            return rng.randint(-100, 100)
        if choice == 1:
            return "".join(rng.choice(string.ascii_letters + string.digits + "_-") for _ in range(rng.randint(0, 12)))
        if choice == 2:
            return [self._random_payload(rng, depth + 1) for _ in range(rng.randint(0, 5))]
        if choice == 3:
            obj = {}
            for _ in range(rng.randint(0, 4)):
                key = "".join(rng.choice(string.ascii_lowercase) for _ in range(rng.randint(1, 6)))
                obj[key] = self._random_payload(rng, depth + 1)
            return obj
        if choice == 4:
            return bool(rng.randint(0, 1))
        return None

    def test_fuzz_validate_instance_does_not_crash(self) -> None:
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "items": {"type": "array", "items": {"type": ["string", "object", "integer"]}},
            },
            "additionalProperties": True,
        }
        rng = random.Random(1234)
        for _ in range(500):
            payload = self._random_payload(rng)
            try:
                validate_instance(payload, schema)
            except Exception as exc:  # pragma: no cover
                self.fail(f"validate_instance raised unexpectedly: {exc}")

    def test_fuzz_malformed_json_inputs(self) -> None:
        rng = random.Random(4321)
        for _ in range(200):
            text = "".join(chr(rng.randint(0, 127)) for _ in range(rng.randint(1, 60)))
            if text.strip().startswith("{") and text.strip().endswith("}"):
                # valid/near-valid objects are okay either way.
                pass
            try:
                json.loads(text)
            except Exception:
                continue

    def test_optional_slow_fuzz(self) -> None:
        if os.getenv("FACTORY_SLOW_TESTS", "").strip() not in {"1", "true", "TRUE"}:
            self.skipTest("slow tests disabled")
        schema = {"type": ["object", "array", "string", "integer", "boolean", "null"]}
        rng = random.Random(20260218)
        for _ in range(5000):
            payload = self._random_payload(rng)
            validate_instance(payload, schema)


if __name__ == "__main__":
    unittest.main()

