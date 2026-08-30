from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sync_sentinel.fixtures import load_fixture_registry, mandatory_fixture_readiness
from sync_sentinel.sandbox.database import owned_sqlite_path, validate_database_url
from sync_sentinel.sandbox.prisma_runtime import _pc_sentinel_schema


class CapsuleAssetTests(unittest.TestCase):
    def test_m_owned_sqlite_blocks_escape_and_network_urls(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            safe = owned_sqlite_path(root / "data/pc.db", root, "pc")
            self.assertTrue(str(safe).endswith("pc.db"))
            with self.assertRaises(RuntimeError):
                owned_sqlite_path(root.parent / "live.db", root, "escape")
            with self.assertRaises(RuntimeError):
                validate_database_url("postgresql://example.invalid/live", root, "network")

    def test_n_pc_sentinel_schema_stays_inside_capsule_and_preserves_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "apps/terminal-de-venta-system/prisma/schema.prisma"
            source.parent.mkdir(parents=True)
            original = '''generator client {\n  provider = "prisma-client-js"\n}\n\ndatasource db {\n  provider = "sqlite"\n  url = env("DATABASE_URL")\n}\n'''
            source.write_text(original, encoding="utf-8")
            target = _pc_sentinel_schema(root)
            self.assertEqual(source.read_text(encoding="utf-8"), original)
            self.assertIn("/.sync-sentinel/prisma/schema.prisma", target.as_posix())
            rendered = target.read_text(encoding="utf-8")
            self.assertIn('output   = "../../.generated/prisma-client"', rendered)
            self.assertNotEqual(target, source)

    def test_o_fixture_registry_contains_executable_positive_and_a_through_l_cases(self):
        registry = load_fixture_registry()
        ids = {item["fixtureId"] for item in registry["fixtures"]}
        self.assertIn("SYNC.JOURNEY.A.SALE_ACK.V1", ids)
        self.assertIn("SYNC.JOURNEY.B.CATALOG_DELTA.V1", ids)
        for letter in "ABCDEFGHIJKL":
            self.assertTrue(any(f"SYNC.NEG.{letter}." in fixture_id for fixture_id in ids), letter)
        readiness = mandatory_fixture_readiness(registry)
        self.assertEqual(readiness["total"], 14)
        self.assertEqual(readiness["implemented"], 14)
        self.assertEqual(readiness["missingImplementations"], [])
        self.assertEqual(readiness["invalidDefinitions"], [])
        self.assertTrue(readiness["ready"], "registry may be ready only because A-L now have real runtime execution in negative_runner.mts")

    def test_p_runtime_registry_is_extensible_but_future_targets_are_not_certified(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root / "contracts/runtime-registry.v1.json").read_text(encoding="utf-8"))
        roles = {item["role"]: item["status"] for item in data["runtimes"]}
        self.assertEqual(roles["tablet"], "ACTIVE_CERTIFICATION_TARGET")
        self.assertEqual(roles["pc"], "ACTIVE_CERTIFICATION_TARGET")
        self.assertEqual(roles["mobile"], "FUTURE_ADAPTER_NOT_CERTIFIED")
        self.assertFalse(data["productionCertified"])


if __name__ == "__main__":
    unittest.main()
