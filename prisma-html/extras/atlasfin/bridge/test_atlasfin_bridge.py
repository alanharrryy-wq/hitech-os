#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "atlasfin_bridge.py"
SPEC = importlib.util.spec_from_file_location("atlasfin_bridge", MODULE_PATH)
assert SPEC and SPEC.loader
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)


class AtlasfinBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = bridge._find_repo_root(None)
        cls.snapshot = bridge.build_bridge(cls.repo)

    def test_reuses_exact_418_element_catalog(self) -> None:
        self.assertEqual(self.snapshot["atlasfin"]["catalogElementCount"], 418)
        self.assertEqual(len(self.snapshot["atlasfin"]["catalogElements"]), 418)

    def test_current_structured_registry_counts_are_reused(self) -> None:
        expected = {
            "properties": 79,
            "families": 32,
            "presets": 32,
            "recipes": 8,
            "states": 19,
            "variants": 16,
            "adapters": 8,
            "assets": 1,
        }
        actual = {
            key: len(value)
            for key, value in self.snapshot["atlasfin"]["registries"].items()
        }
        self.assertEqual(actual, expected)

    def test_registry_record_kinds_are_explicit(self) -> None:
        expected = {
            "properties": "atlasfinProperty",
            "families": "atlasfinFamily",
            "presets": "atlasfinPreset",
            "recipes": "atlasfinRecipe",
            "states": "atlasfinState",
            "variants": "atlasfinVariant",
            "adapters": "atlasfinAdapter",
            "assets": "atlasfinAsset",
        }
        for registry_name, record_kind in expected.items():
            records = self.snapshot["atlasfin"]["registries"][registry_name]
            self.assertTrue(records)
            self.assertTrue(all(row["recordKind"] == record_kind for row in records))

    def test_materiality_catalog_is_fail_closed_and_uninspected(self) -> None:
        policy = self.snapshot["materialityCatalog"]
        self.assertEqual(policy["policy"], "STANDBY_USER_INVOKED_ONLY")
        self.assertFalse(policy["inspected"])
        self.assertFalse(policy["automaticFallbackAllowed"])
        with self.assertRaisesRegex(bridge.BridgeError, "MATERIALITY_CATALOG_STANDBY_FORBIDS_READ"):
            bridge._contained(self.repo, bridge.MATERIALITY_CATALOG)

    def test_missing_worker_lane_is_pending_not_fake(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            lane = bridge._load_worker_lane(Path(td), "tablet")
        self.assertEqual(lane["workerDataState"], "PENDING_NOT_PRESENT")
        self.assertEqual(lane["records"], [])
        self.assertEqual(lane["blockers"], [])

    def test_invalid_worker_data_is_explicitly_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            lane_dir = root / bridge.CANDIDATE_ROOT / "tablet"
            lane_dir.mkdir(parents=True)
            bad = {
                "candidateOnly": False,
                "baseHead": "not-a-head",
                "surfaceKey": "pc",
                "targetId": "",
            }
            (lane_dir / "CANDIDATES.jsonl").write_text(
                json.dumps(bad) + "\n", encoding="utf-8"
            )
            lane = bridge._load_worker_lane(root, "tablet")
        self.assertEqual(lane["workerDataState"], "INVALID")
        self.assertGreaterEqual(len(lane["blockers"]), 4)

    def test_fixture_preserves_candidate_only_contract(self) -> None:
        fixture = json.loads((HERE / "fixtures" / "tablet-candidate.json").read_text(encoding="utf-8"))
        self.assertEqual(bridge._candidate_conformance(fixture, "tablet", "fixture", 1), [])
        normalized = bridge._worker_bridge_record(
            fixture,
            source_lane="tablet",
            source_file="fixture",
            source_line=1,
        )
        self.assertTrue(normalized["candidateOnly"])
        self.assertEqual(normalized["targetId"], "FIXTURE.NOT_CANONICAL.001")
        self.assertEqual(normalized["workEntryDecision"], "BLOCKED")
        self.assertEqual(normalized["ndcResolutionStatus"], "UNRESOLVED")

    def test_visual_core_absence_does_not_create_fake_status(self) -> None:
        feed = self.snapshot["visualCore"]
        self.assertIn(feed["feedState"], {"PRESENT", "PENDING_NOT_PRESENT"})
        if feed["feedState"] == "PENDING_NOT_PRESENT":
            self.assertIsNone(feed["visualCoreStatus"])
            self.assertIsNone(feed["applicationEngine"])
            self.assertEqual(feed["surfaces"], [])

    def test_cobrar_keeps_identity_and_atlasfin_recipe_domains_separate(self) -> None:
        cobrar = self.snapshot["currentReferences"]["cobrar"]
        self.assertEqual(cobrar["identityRecipeId"], "REC.button.primary")
        self.assertIsNone(cobrar["atlasfinRecipeId"])
        self.assertEqual(
            cobrar["existingBindingId"],
            "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1",
        )
        self.assertEqual(cobrar["bindingStatus"], "EXISTING_RESOLVED")
        self.assertEqual(cobrar["physicalStatus"], "CURRENT")
        self.assertIn(cobrar["projectionStatus"], {"CURRENT", "DRIFT", "UNRESOLVED"})

    def test_authority_refs_are_domain_qualified(self) -> None:
        refs = list(bridge._walk_authority_refs(self.snapshot))
        self.assertTrue(refs)
        for ref in refs:
            self.assertIn(ref["authorityDomain"], bridge.ALLOWED_AUTHORITY_DOMAINS)
            self.assertTrue(ref["id"])

    def test_bridge_is_deterministic_for_same_checkout(self) -> None:
        second = bridge.build_bridge(self.repo, base_head=self.snapshot["baseHead"])
        self.assertEqual(bridge.canonical_json(self.snapshot), bridge.canonical_json(second))

    def test_bridge_validation_passes_current_read_only_model(self) -> None:
        self.assertEqual(bridge.validate_bridge(self.snapshot), [])

    def test_snapshot_write_cannot_escape_bridge_owned_directory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / bridge.BRIDGE_ROOT).mkdir(parents=True)
            with self.assertRaisesRegex(bridge.BridgeError, "OUTPUT_MUST_STAY_INSIDE_ATLASFIN_BRIDGE"):
                bridge._write_snapshot(
                    root,
                    root / "outside.json",
                    {"schema": bridge.BRIDGE_SCHEMA},
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
