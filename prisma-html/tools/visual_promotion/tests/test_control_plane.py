from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from visual_promotion.control_plane import (
    BROAD_REDISCOVERY_REASON,
    CANDIDATE_SCHEMA,
    CURRENT_CENSUS_REASON,
    MATERIALITY_POLICY,
    SHARD_SCHEMA,
    ControlPlaneError,
    build_atlasfin_indexes,
    build_current_truth,
    build_surface_readiness,
    composer_plan,
    normalize_atlasfin,
    validate_candidate,
    validate_disjoint_write_ownership,
    validate_edge_type,
    validate_owned_output,
    validate_shard,
)

HEAD = "a" * 40
TARGET = "TGT.CENSUS.TABLET.0123456789ABCDEF.V1"


def candidate(**overrides):
    row = {
        "schema": CANDIDATE_SCHEMA,
        "candidateOnly": True,
        "baseHead": HEAD,
        "surfaceKey": "tablet",
        "targetId": TARGET,
        "recordKind": "VISUAL_CONTROL_CENSUS_TARGET",
        "enforcement": "DISCOVERY_ONLY",
        "physicalStatus": "CURRENT",
        "physical": {
            "routeId": None, "regionId": None, "slotId": None, "componentId": None,
            "componentUiId": None, "ownerId": None, "ownerFile": None,
            "renderSourceFile": None, "styleSourceFile": None,
            "selector": ".fixture", "implementationLayerId": "products.tablet.fixture",
        },
        "ndc": {"ndcPrimaryId": None, "ndcRefs": [], "ndcResolutionStatus": "UNRESOLVED"},
        "visual": {
            "visualMeaningId": None, "visualMeaningCandidate": "primary action",
            "visualMeaningStatus": "CANDIDATE_REVIEW_REQUIRED",
        },
        "atlasfin": {
            "atlasfinCatalogElementId": None, "atlasfinUiId": None,
            "atlasfinFamilyId": "FAM.BUTTON.PRIMARY.SOLID",
            "atlasfinPresetId": None, "atlasfinRecipeId": None,
            "atlasfinLegacyRecipeId": None, "atlasfinAdapterId": None,
            "atlasfinMatchStatus": "MATCHED_FAMILY",
        },
        "identity": {
            "identityProfileId": None, "identityRecipeId": None,
            "identityAdapterId": None, "existingBindingId": None,
            "bindingCandidateKey": "tablet:fixture", "bindingStatus": "CANDIDATE",
        },
        "application": {
            "applicationLayerId": None, "projectionStatus": "UNRESOLVED",
            "promotionStatus": "REGISTER_TARGET_FIRST",
            "workEntryDecision": "REGISTER_TARGET_FIRST",
        },
        "confidence": "medium",
        "evidenceRefs": [{"authorityDomain": "target-index", "id": TARGET}],
        "blockers": ["semantic"],
        "notes": [CURRENT_CENSUS_REASON],
    }
    row.update(overrides)
    return row


def manifest(count=1):
    return {
        "schema": SHARD_SCHEMA,
        "candidateOnly": True,
        "baseHead": HEAD,
        "surfaceKey": "tablet",
        "ownedRoot": "prisma-html/governance/visual-promotion/candidates/tablet/",
        "inputCensusCount": count,
        "materialityCatalogPolicy": MATERIALITY_POLICY,
        "broadRediscoveryPerformed": False,
    }


class ControlPlaneTests(unittest.TestCase):
    def test_candidate_validates_closed_vocabulary(self):
        validate_candidate(candidate(), expected_head=HEAD)

    def test_candidate_schema_is_optional_for_parallel_compatibility(self):
        row = candidate(); row.pop("schema")
        validate_candidate(row, expected_head=HEAD)

    def test_wrong_base_head_fails_closed(self):
        with self.assertRaisesRegex(ControlPlaneError, "BASE_HEAD_MISMATCH"):
            validate_candidate(candidate(), expected_head="b" * 40)

    def test_authority_refs_must_be_qualified(self):
        row = candidate(); row["evidenceRefs"] = ["TGT.X"]
        with self.assertRaisesRegex(ControlPlaneError, "AUTHORITY_QUALIFIED_REF_REQUIRED"):
            validate_candidate(row)

    def test_ndc_edge_vocab_is_closed(self):
        validate_edge_type("reconciles")
        with self.assertRaisesRegex(ControlPlaneError, "NDC_EDGE_TYPE_INVALID"):
            validate_edge_type("mapsTo")

    def test_disjoint_write_ownership(self):
        self.assertEqual(validate_disjoint_write_ownership()["status"], "PASS_DISJOINT_WRITE_OWNERSHIP")
        validate_owned_output("tablet", "prisma-html/governance/visual-promotion/candidates/tablet/CANDIDATES.jsonl")
        with self.assertRaisesRegex(ControlPlaneError, "WRITE_OWNERSHIP_VIOLATION"):
            validate_owned_output("tablet", "prisma-html/governance/visual-promotion/candidates/pc/CANDIDATES.jsonl")

    def test_zero_loss_accounting(self):
        result = validate_shard(manifest(), [candidate()], expected_head=HEAD)
        self.assertEqual(result["inputCensusCount"], 1)
        self.assertEqual(result["outputCount"], 1)
        self.assertEqual(result["accounting"], {"unresolved": 1})

    def test_zero_loss_missing_target_fails(self):
        with self.assertRaisesRegex(ControlPlaneError, "ZERO_LOSS_ACCOUNTING_FAILED"):
            validate_shard(manifest(2), [candidate()])

    def test_duplicate_target_fails(self):
        with self.assertRaisesRegex(ControlPlaneError, "DUPLICATE_TARGET_IDS"):
            validate_shard(manifest(2), [candidate(), candidate()])

    def test_materiality_policy_cannot_be_enabled(self):
        m = manifest(); m["materialityCatalogPolicy"] = "AUTO_FALLBACK"
        with self.assertRaisesRegex(ControlPlaneError, "MATERIALITY_POLICY"):
            validate_shard(m, [candidate()])

    def test_atlasfin_indexes_and_normalization(self):
        docs = [
            {"sections": [{"items": [{"id": "C.PRIMARY_BUTTON"}]}]},
            {"schema": "PRISMA_VISUAL_FAMILY_REGISTRY_V1", "items": [{"familyId": "FAM.BUTTON.PRIMARY.SOLID"}]},
            {"schema": "PRISMA_VISUAL_PRESET_REGISTRY_V1", "items": [{"presetId": "PRESET.BUTTON.PRIMARY.SOLID.V2"}]},
            {"schema": "PRISMA_VISUAL_RECIPE_REGISTRY_V4", "items": [{"recipeId": "REC.button.governed.v2"}]},
            {"schema": "PRISMA_SURFACE_ADAPTER_REGISTRY_V2", "items": [{"id": "ADP.TB.TOUCH.V2"}]},
            {"elements": [{"ui_id": "ATL-ONE", "recipe_id": "RCP.ATLAS.ONE", "target_bindings": [{"adapter_id": "ADP.TB.PENDING"}]}]},
        ]
        indexes = build_atlasfin_indexes(docs)
        normalized = normalize_atlasfin(candidate(), indexes)
        self.assertEqual(normalized["matchStatus"], "MATCHED_FAMILY")
        self.assertFalse(normalized["materialityFallbackUsed"])
        self.assertIn("C.PRIMARY_BUTTON", indexes["catalog"])

    def test_atlasfin_unknown_match_fails(self):
        empty = {key: set() for key in ("catalog", "ui", "family", "preset", "recipe", "legacyRecipe", "adapter")}
        with self.assertRaisesRegex(ControlPlaneError, "ATLASFIN_MATCH_UNPROVEN"):
            normalize_atlasfin(candidate(), empty)

    def test_source_hash_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.css"
            output = root / "output.css"
            source.write_text(".x{}\n", encoding="utf-8")
            output.write_text(".x{}\n", encoding="utf-8")
            row = candidate()
            row["canonicalSourcePath"] = "source.css"
            row["generatedOutputPath"] = "output.css"
            row["sourceSha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
            row["outputSha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
            validate_candidate(row, repo_root=root)
            row["sourceSha256"] = "0" * 64
            with self.assertRaisesRegex(ControlPlaneError, "SOURCESHA256_MISMATCH"):
                validate_candidate(row, repo_root=root)

    def test_census_never_claims_exact_apply(self):
        row = candidate(); row["application"]["workEntryDecision"] = "GVAE_EXACT_APPLY"
        with self.assertRaisesRegex(ControlPlaneError, "CENSUS_CANNOT_SELF_PROMOTE"):
            validate_candidate(row)

    def test_composer_is_plan_only(self):
        plan = composer_plan([candidate()])
        self.assertEqual(plan["status"], "PLAN_READY_FOR_REVIEW")
        self.assertFalse(plan["canonicalMutationPerformed"])
        self.assertFalse(plan["canonicalIdsAssigned"])

    def test_mixed_base_blocks_composer(self):
        other = candidate(
            baseHead="b" * 40,
            surfaceKey="pc",
            targetId="TGT.CENSUS.PC.0123456789ABCDEF.V1",
        )
        self.assertIn("MIXED_BASE_REQUIRES_REVALIDATION", composer_plan([candidate(), other])["blockers"])

    def test_binding_collision_is_explicit(self):
        other = candidate(targetId="TGT.CENSUS.TABLET.FEDCBA9876543210.V1")
        collisions = composer_plan([candidate(), other])["collisions"]
        self.assertTrue(any(row["kind"] == "BINDING_CANDIDATE_KEY_COLLISION" for row in collisions))

    def test_current_census_reused_not_rediscovered(self):
        index = {"schema": "prisma.visual.application.target-index.v1", "records": [{
            "surface": "tablet", "targetId": TARGET,
            "recordKind": "VISUAL_CONTROL_CENSUS_TARGET", "enforcement": "DISCOVERY_ONLY",
            "blockers": ["semantic"],
        }]}
        row = build_current_truth(index)["records"][0]
        self.assertTrue(row["currentCensusReusable"])
        self.assertFalse(row["genuineDiscoveryNeeded"])
        self.assertEqual(row["nextStepReason"], CURRENT_CENSUS_REASON)

    def test_drift_is_targeted_not_broad(self):
        index = {"records": [{
            "surface": "tablet", "targetId": TARGET,
            "recordKind": "VISUAL_CONTROL_CENSUS_TARGET", "enforcement": "DISCOVERY_ONLY",
            "blockers": ["source-hash-drift"],
        }]}
        row = build_current_truth(index)["records"][0]
        self.assertTrue(row["genuineDiscoveryNeeded"])
        self.assertEqual(row["discoveryScope"], "TARGETED_ONLY")

    def test_surface_readiness_never_claims_apply(self):
        index = {"records": [{
            "surface": "tablet", "targetId": TARGET,
            "recordKind": "VISUAL_CONTROL_CENSUS_TARGET", "enforcement": "DISCOVERY_ONLY",
            "blockers": [],
        }]}
        tablet = build_surface_readiness(build_current_truth(index))["surfaces"][0]
        self.assertFalse(tablet["wholeSurfaceApplyReady"])
        self.assertFalse(tablet["broadRediscoveryAllowed"])
        self.assertEqual(tablet["broadRediscoveryReason"], BROAD_REDISCOVERY_REASON)

    def test_contract_json_files_parse(self):
        repo = Path(__file__).resolve().parents[4]
        root = repo / "prisma-html" / "governance" / "visual-promotion" / "contracts"
        for name in ("candidate.schema.json", "candidate-shard-manifest.schema.json", "control-plane.contract.json"):
            self.assertIsInstance(json.loads((root / name).read_text(encoding="utf-8")), dict)


if __name__ == "__main__":
    unittest.main()
