from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from visual_promotion.certification_handoffs import (
    CertificationHandoffError,
    assert_final_aggregation_invariants,
    load_certification_registry,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
REGISTRY = (
    REPO
    / "prisma-html"
    / "governance"
    / "visual-promotion"
    / "contracts"
    / "certification-intake.registry.json"
)


class CertificationHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = load_certification_registry(REGISTRY)

    def test_exact_certification_heads_are_frozen(self):
        expected = {
            "tablet": "fd111022438bab909151c2220b52e95aa5aa7eb3",
            "pc": "8cc979c141000fcedabf832f16468a6ee3e328e2",
            "mobile": "664035e83943ae48c923585765d3c505b1bd8c53",
            "shared-ui": "553577aa74045c73ab9c92d1f81538e7e0a8c65a",
        }
        self.assertEqual(
            {
                key: value["certificationHead"]
                for key, value in self.registry["surfaces"].items()
            },
            expected,
        )
        self.assertEqual(
            self.registry["atlasfin"]["certificationHead"],
            "6c7743f55434eb8d3429f286e2f9eae275d93d87",
        )

    def test_exact_certification_counts_sum_to_2097(self):
        self.assertEqual(
            sum(
                row["expectedCount"]
                for row in self.registry["surfaces"].values()
            ),
            2097,
        )
        self.assertEqual(
            self.registry["atlasfin"]["expectedReferenceCount"],
            2421,
        )

    def test_every_pinned_file_has_git_blob_and_sha256(self):
        lanes = list(self.registry["surfaces"].values()) + [
            self.registry["atlasfin"]
        ]
        for lane in lanes:
            for pin in lane["files"].values():
                self.assertRegex(pin["gitBlobSha"], r"^[0-9a-f]{40}$")
                self.assertRegex(pin["sha256"], r"^[0-9a-f]{64}$")

    def test_materiality_and_broad_rediscovery_stay_forbidden(self):
        self.assertEqual(
            self.registry["materialityCatalogPolicy"],
            "STANDBY_USER_INVOKED_ONLY",
        )
        self.assertFalse(self.registry["broadRediscoveryAllowed"])

    def test_final_invariants_require_owner_certification_metadata(self):
        result = {
            "summary": {
                "normalizedRecordCount": 1,
                "certificationRecordCount": 1,
                "invalidRecordCount": 0,
                "semanticMutationCount": 0,
                "duplicateTargetIdCount": 0,
                "currentlyAuthorizedCanonicalPromotions": 0,
                "runtimeVisualGreen": False,
                "wholeSurfaceApplyReady": False,
                "certificationHandoffsVerified": True,
                "surfaceCertificationHandoffCount": 4,
                "atlasfinCertificationHandoffCount": 1,
            },
            "manifest": {
                "allCertificationRecordHashesPinned": True,
                "materialityCatalogInspected": False,
            },
            "certifications": [{"targetId": "TGT.X"}],
        }
        with self.assertRaisesRegex(
            CertificationHandoffError,
            "OWNER_CERTIFICATION_PROVENANCE",
        ):
            assert_final_aggregation_invariants(result, expected_count=1)

    def test_registry_wrong_schema_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "registry.json"
            doc = copy.deepcopy(self.registry)
            doc["schema"] = "wrong"
            path.write_text(json.dumps(doc), encoding="utf-8")
            with self.assertRaisesRegex(
                CertificationHandoffError,
                "CERTIFICATION_INTAKE_REGISTRY_SCHEMA_INVALID",
            ):
                load_certification_registry(path)


if __name__ == "__main__":
    unittest.main()
