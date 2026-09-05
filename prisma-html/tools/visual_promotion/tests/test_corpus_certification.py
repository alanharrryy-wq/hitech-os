from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from visual_promotion.corpus_certification import (
    CorpusCertificationError,
    build_semantic_review_groups,
    build_surface_readiness_from_corpus,
    expected_certification_status,
    load_registry,
    normalize_registered_raw_record,
    semantic_review_key,
    verify_registered_file,
)

HEAD = "57b01ad8bda043ec25763203354b686341bace09"


def candidate(surface="mobile", target="TGT.CENSUS.MOBILE.AAAAAAAAAAAAAAAAAAAA.V1"):
    return {
        "schema": "prisma.visual-promotion.candidate.v1", "candidateOnly": True, "baseHead": HEAD,
        "surfaceKey": surface, "targetId": target, "recordKind": "VISUAL_CONTROL_CENSUS_TARGET",
        "enforcement": "DISCOVERY_ONLY", "physicalStatus": "CURRENT",
        "canonicalSourcePath": "prisma-html/authority/rifat/surfaces/mobile/runtime-sources/app/globals.css",
        "generatedOutputPath": "apps/terminal-de-venta-system/products/mobile/app/app/globals.css",
        "sourceSha256": "a" * 64, "outputSha256": "a" * 64, "projectionMode": "exact-byte-copy",
        "physical": {"routeId": None, "regionId": None, "slotId": None, "componentId": None,
            "componentUiId": None, "ownerId": "products.mobile.app.app.globals.css",
            "ownerFile": "products/mobile/app/app/globals.css", "renderSourceFile": None,
            "styleSourceFile": "products/mobile/app/app/globals.css", "selector": "a",
            "implementationLayerId": "products.mobile.app.app.globals.css.a"},
        "ndc": {"ndcPrimaryId": None, "ndcRefs": ["SURF.mb.owner_home"], "ndcResolutionStatus": "UNRESOLVED"},
        "visual": {"visualMeaningId": None, "visualMeaningCandidate": None, "visualMeaningStatus": "UNRESOLVED"},
        "atlasfin": {"atlasfinFamilyId": None, "atlasfinPresetId": None, "atlasfinRecipeId": None,
            "atlasfinAdapterId": "ADP.MB.TOUCH.V2", "atlasfinMatchStatus": "AMBIGUOUS"},
        "identity": {"identityProfileId": None, "identityRecipeId": None,
            "identityAdapterId": "identity::prisma.adapter.mobile.v1", "existingBindingId": None,
            "bindingCandidateKey": None, "bindingStatus": "BLOCKED"},
        "application": {"applicationLayerId": None, "projectionStatus": "CURRENT",
            "promotionStatus": "REGISTER_TARGET_FIRST", "workEntryDecision": "REGISTER_TARGET_FIRST"},
        "confidence": "high",
        "evidenceRefs": ["target-index::TGT.X", "ndc::SURF.mb.owner_home", "atlasfin::ADP.MB.TOUCH.V2"],
        "blockers": ["semantic"], "notes": [],
    }


def registry():
    def row(worker, cert, transforms):
        return {"workerHead": worker, "certificationHead": cert, "recordCount": 1,
            "workerFiles": {"CANDIDATES.jsonl": {"gitBlobSha": "b", "sha256": "x"}},
            "certificationFiles": {"NORMALIZED.jsonl": {"gitBlobSha": "c", "sha256": "y", "recordCount": 1}},
            "allowedRawTransforms": transforms}
    return {"schema": "prisma.visual-promotion.intake-registry.v1", "sourceBaseHead": HEAD,
        "materialityCatalogPolicy": "STANDBY_USER_INVOKED_ONLY", "broadRediscoveryAllowed": False,
        "surfaceOrder": ["tablet", "pc", "mobile", "shared-ui"],
        "surfaces": {
            "tablet": row("1"*40, "2"*40, []), "pc": row("3"*40, "4"*40, []),
            "mobile": row("5"*40, "6"*40, [
                "FLATTEN_PROJECTION_OBJECT_TO_STRICT_TOP_LEVEL_FIELDS",
                "NORMALIZE_NDC_REFS_TO_DOMAIN_SCOPED_RAW_IDS",
                "NORMALIZE_UNQUALIFIED_EVIDENCE_REFS_TO_STRICT_AUTHORITY_REFS",
                "NORMALIZE_ATLASFIN_ADAPTER_TO_DOMAIN_SCOPED_RAW_ID"]),
            "shared-ui": row("7"*40, "8"*40, [
                "EXPLICIT_STRICT_SCHEMA_TAG", "QUALIFIED_ATLASFIN_ADAPTER_TO_STRICT_RAW_REGISTRY_ID"])},
        "atlasfin": {}}


class CorpusCertificationTests(unittest.TestCase):
    def test_registry_fails_closed_on_materiality_policy(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"r.json"; r=registry(); r["materialityCatalogPolicy"]="AUTO"
            p.write_text(json.dumps(r), encoding="utf-8")
            with self.assertRaisesRegex(CorpusCertificationError, "MATERIALITY_POLICY"):
                load_registry(p)

    def test_file_intake_is_head_and_hash_pinned(self):
        r=registry(); raw=b"x\n"
        meta=r["surfaces"]["mobile"]["workerFiles"]["CANDIDATES.jsonl"]
        meta["sha256"]=hashlib.sha256(raw).hexdigest(); meta["recordCount"]=1
        verify_registered_file(r, "mobile", kind="worker", head="5"*40,
            file_name="CANDIDATES.jsonl", content=raw, git_blob_sha="b")
        with self.assertRaisesRegex(CorpusCertificationError, "UNREGISTERED_WORKER_HEAD"):
            verify_registered_file(r, "mobile", kind="worker", head="9"*40,
                file_name="CANDIDATES.jsonl", content=raw)

    def test_mobile_known_shape_normalizes_without_semantic_mutation(self):
        r=registry(); raw=candidate()
        raw["projection"]={k:raw.pop(k) for k in (
            "canonicalSourcePath","generatedOutputPath","sourceSha256","outputSha256","projectionMode")}
        raw["ndc"]["ndcRefs"]=["ndc::SURF.mb.owner_home"]
        raw["atlasfin"]["atlasfinAdapterId"]="atlasfin::ADP.MB.TOUCH.V2"
        raw["evidenceRefs"]=[
            "prisma-html/authority/rifat/prisma-ui/visual-control/target-index/mobile.json",
            "apps/terminal-de-venta-system/products/mobile/app/app/globals.css",
            "ndc::SURF.mb.owner_home"]
        normalized, transforms=normalize_registered_raw_record(r, "mobile", raw, source_head="5"*40)
        self.assertEqual(normalized["ndc"]["ndcRefs"], ["SURF.mb.owner_home"])
        self.assertEqual(normalized["atlasfin"]["atlasfinAdapterId"], "ADP.MB.TOUCH.V2")
        self.assertNotIn("projection", normalized)
        self.assertIn("FLATTEN_PROJECTION_OBJECT_TO_STRICT_TOP_LEVEL_FIELDS", transforms)

    def test_unknown_shape_fails_closed(self):
        r=registry(); raw=candidate("tablet","TGT.CENSUS.TABLET.AAAAAAAAAAAAAAAAAAAA.V1")
        raw["atlasfin"]["atlasfinAdapterId"]="atlasfin::ADP.TB.TOUCH.V2"
        with self.assertRaisesRegex(CorpusCertificationError, "UNREGISTERED_ATLASFIN_ADAPTER_SHAPE"):
            normalize_registered_raw_record(r, "tablet", raw, source_head="1"*40)

    def test_semantic_review_key_is_separate_from_surface_target_identity(self):
        a=candidate(); a["visual"]["visualMeaningCandidate"]="primary action"
        b=candidate("tablet","TGT.CENSUS.TABLET.BBBBBBBBBBBBBBBBBBBB.V1")
        b["visual"]["visualMeaningCandidate"]="primary action"
        self.assertEqual(semantic_review_key(a), semantic_review_key(b))
        groups=build_semantic_review_groups([a,b])
        self.assertEqual(groups["crossSurfaceGroupCount"],1)
        self.assertFalse(groups["reviewKeyIncludesSurfaceKey"])
        self.assertFalse(groups["reviewKeyIncludesTargetId"])
        self.assertFalse(groups["collisionFingerprintChanged"])

    def test_certification_state_never_implies_exact_apply(self):
        row=candidate()
        self.assertEqual(expected_certification_status(row), "VALID_REGISTER_TARGET_FIRST")
        row["application"]["promotionStatus"]="ELIGIBLE_CANDIDATE"
        self.assertEqual(expected_certification_status(row), "VALID_ELIGIBLE_CANDIDATE")
        self.assertNotEqual(row["application"]["workEntryDecision"], "GVAE_EXACT_APPLY")

    def test_surface_readiness_never_claims_whole_surface_apply(self):
        rows=[]
        for i,s in enumerate(("tablet","pc","mobile","shared-ui")):
            rows.append(candidate(s,f"TGT.CENSUS.{s.upper().replace('-', '_')}.{i:020X}.V1"))
        out=build_surface_readiness_from_corpus(rows)
        self.assertEqual(out["wholeSurfaceApplyReadyCount"],0)
        self.assertFalse(out["runtimeVisualGreen"])
        self.assertTrue(all(not x["wholeSurfaceApplyReady"] for x in out["surfaces"]))


if __name__ == "__main__":
    unittest.main()
