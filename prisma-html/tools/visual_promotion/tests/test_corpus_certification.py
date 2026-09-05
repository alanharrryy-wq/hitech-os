from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from visual_promotion.corpus_certification import (
    CorpusCertificationError,
    build_semantic_review_groups,
    load_registry,
    normalize_manifest,
    normalize_record,
    semantic_signature,
    sha256_bytes,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRY_PATH = (
    REPO
    / "prisma-html"
    / "governance"
    / "visual-promotion"
    / "contracts"
    / "legacy-worker-intake.registry.json"
)
FIXTURE_PATH = HERE / "fixtures" / "exact-worker-samples.json"


def sample_manifest(surface: str, registry: dict) -> dict:
    base = {
        "candidateOnly": True,
        "baseHead": registry["commonWorkerBaseHead"],
        "surfaceKey": surface,
    }
    if surface == "tablet":
        base["policy"] = {
            "materialityCatalogPolicy": "STANDBY_USER_INVOKED_ONLY",
            "broadRediscoveryPerformed": False,
        }
    elif surface == "pc":
        base["materialityCatalog"] = {
            "policy": "STANDBY_USER_INVOKED_ONLY",
        }
        base["broadRediscovery"] = {"performed": False}
    elif surface == "mobile":
        base["materialityCatalogPolicy"] = (
            "STANDBY_USER_INVOKED_ONLY"
        )
        base["broadRediscoveryPerformed"] = False
    else:
        base["policies"] = {
            "materialityCatalog":
                "STANDBY_USER_INVOKED_ONLY",
            "broadRediscovery": False,
        }
    return base


class CorpusCertificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_registry(REGISTRY_PATH)
        cls.fixtures = json.loads(
            FIXTURE_PATH.read_text(encoding="utf-8")
        )["samples"]

    def normalize_fixture(self, surface: str):
        fixture = next(
            row
            for row in self.fixtures
            if row["surfaceKey"] == surface
        )
        raw_line = fixture["rawLine"]
        raw = json.loads(raw_line)
        normalized, certification = normalize_record(
            raw,
            surface=surface,
            source_head=fixture["sourceHead"],
            source_file=fixture["sourceFile"],
            source_line=fixture["sourceLine"],
            source_record_sha256=sha256_bytes(
                raw_line.encode("utf-8")
            ),
            registry=self.registry,
        )
        return fixture, raw, normalized, certification

    def test_exact_worker_samples_cover_all_surfaces(self):
        self.assertEqual(
            {row["surfaceKey"] for row in self.fixtures},
            {"tablet", "pc", "mobile", "shared-ui"},
        )
        for fixture in self.fixtures:
            profile = self.registry["surfaces"][
                fixture["surfaceKey"]
            ]
            self.assertEqual(
                fixture["sourceHead"],
                profile["sourceHead"],
            )

    def test_exact_samples_normalize_without_semantic_mutation(self):
        for surface in (
            "tablet",
            "pc",
            "mobile",
            "shared-ui",
        ):
            _, raw, normalized, certification = (
                self.normalize_fixture(surface)
            )
            self.assertEqual(
                semantic_signature(raw),
                semantic_signature(normalized),
            )
            self.assertFalse(
                certification["normalization"][
                    "semanticMutation"
                ]
            )
            self.assertTrue(
                certification[
                    "certificationStatus"
                ].startswith("VALID_")
            )

    def test_mobile_known_legacy_shape_normalizes_only_representation(self):
        _, raw, normalized, certification = (
            self.normalize_fixture("mobile")
        )
        self.assertIn("projection", raw)
        self.assertNotIn("projection", normalized)
        self.assertEqual(
            normalized["ndc"]["ndcRefs"],
            ["SURF.mb.owner_home"],
        )
        self.assertEqual(
            normalized["atlasfin"]["atlasfinAdapterId"],
            "ADP.MB.TOUCH.V2",
        )
        self.assertEqual(
            normalized["application"]["projectionStatus"],
            "DRIFT",
        )
        domains = {
            ref.get("authorityDomain")
            for ref in normalized["evidenceRefs"]
            if isinstance(ref, dict)
        }
        self.assertIn("projection-manifest", domains)
        self.assertIn("code-atlas", domains)
        self.assertEqual(
            certification["normalization"]["liftedProvenanceRefs"],
            [],
        )

    def test_shared_ui_qualified_adapter_becomes_raw_field(self):
        _, _, normalized, certification = (
            self.normalize_fixture("shared-ui")
        )
        self.assertEqual(
            normalized["atlasfin"]["atlasfinAdapterId"],
            "ADP.SHARED.NEUTRAL.V2",
        )
        self.assertFalse(
            certification["normalization"][
                "semanticMutation"
            ]
        )

    def test_unknown_head_fails_closed(self):
        fixture = self.fixtures[0]
        raw_line = fixture["rawLine"]
        with self.assertRaisesRegex(
            CorpusCertificationError,
            "UNKNOWN_SOURCE_HEAD",
        ):
            normalize_record(
                json.loads(raw_line),
                surface=fixture["surfaceKey"],
                source_head="0" * 40,
                source_file=fixture["sourceFile"],
                source_line=1,
                source_record_sha256=sha256_bytes(
                    raw_line.encode("utf-8")
                ),
                registry=self.registry,
            )

    def test_all_legacy_manifest_shapes_get_strict_derivative(self):
        for surface in (
            "tablet",
            "pc",
            "mobile",
            "shared-ui",
        ):
            manifest = normalize_manifest(
                sample_manifest(surface, self.registry),
                surface=surface,
                registry=self.registry,
            )
            self.assertEqual(
                manifest["schema"],
                "prisma.visual-promotion.candidate-shard.v1",
            )
            self.assertEqual(
                manifest["inputCensusCount"],
                self.registry["surfaces"][surface][
                    "inputCount"
                ],
            )
            self.assertFalse(
                manifest["broadRediscoveryPerformed"]
            )
            self.assertEqual(
                manifest["materialityCatalogPolicy"],
                "STANDBY_USER_INVOKED_ONLY",
            )

    def test_recipe_review_key_is_separate_and_review_only(self):
        _, _, tablet, _ = self.normalize_fixture("tablet")
        _, _, pc, _ = self.normalize_fixture("pc")
        groups = build_semantic_review_groups(
            [tablet, pc]
        )["groups"]
        recipe = next(
            row
            for row in groups
            if row["reviewKey"]
            == "recipe:REC.table.governed.v2"
        )
        self.assertEqual(
            recipe["surfaceKeys"],
            ["pc", "tablet"],
        )
        self.assertTrue(recipe["crossSurface"])
        self.assertFalse(recipe["canAutoCoalesce"])
        self.assertFalse(
            recipe["canonicalMeaningResolvedByGroup"]
        )

    def test_registry_expected_counts_are_frozen(self):
        self.assertEqual(
            self.registry["expectedCorpusCount"],
            2097,
        )
        self.assertEqual(
            self.registry["expectedAggregate"][
                "sourceOutcomeCounts"
            ],
            {
                "CANDIDATES": 365,
                "UNRESOLVED": 1580,
                "CONFLICTS": 152,
            },
        )


if __name__ == "__main__":
    unittest.main()
