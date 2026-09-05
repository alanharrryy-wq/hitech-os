from __future__ import annotations

import unittest

from visual_application.visual_work_entry_gate import classify_path, decide_request, evaluate_changed

HEAD = "a" * 40
EXACT = "TGT.TABLET.EXACT.ONE.V1"
CENSUS = "TGT.CENSUS.TABLET.ONE.V1"
SOURCE = "prisma-html/authority/rifat/surfaces/tablet/runtime-sources/exact.css"
OUTPUT = "apps/terminal-de-venta-system/products/tablet/app/exact.css"
CENSUS_FILE = "apps/terminal-de-venta-system/products/tablet/app/census.css"
OWNER_TSX = "apps/terminal-de-venta-system/products/tablet/app/app/page.tsx"
UNREGISTERED_CSS = "apps/terminal-de-venta-system/products/mobile/app/unregistered.css"
GENERATED = "apps/terminal-de-venta-system/products/web/app/app/globals.css"
GENERATED_SOURCE = "prisma-html/authority/rifat/surfaces/web/runtime-sources/app/globals.css"


def exact(status="APPLY_READY", blockers=None):
    return {
        "targetId": EXACT,
        "recordKind": "EXACT_APPLICATION_TARGET",
        "enforcement": "GVAE_ENFORCED",
        "surface": "tablet",
        "selector": ".exact",
        "status": status,
        "blockers": blockers or [],
        "canonicalSourcePath": SOURCE,
        "generatedOutputPath": OUTPUT,
    }


def census():
    return {
        "targetId": CENSUS,
        "recordKind": "VISUAL_CONTROL_CENSUS_TARGET",
        "enforcement": "DISCOVERY_ONLY",
        "surface": "tablet",
        "selector": ".census",
        "status": "BLOCKED",
        "blockers": ["semantic", "recipe", "exact-binding", "layer-application-policy"],
        "ownerCss": CENSUS_FILE,
    }


def authority(records=None):
    rows = records if records is not None else [exact(), census()]
    by_id = {r["targetId"]: r for r in rows}
    by_path = {}
    for r in rows:
        for field in ("canonicalSourcePath", "generatedOutputPath", "ownerCss"):
            if r.get(field):
                by_path.setdefault(r[field], []).append(r)
    visual_rows = {
        CENSUS_FILE: [{"surface": "tablet", "authority": "VisualControl:layers.jsonl"}],
        OWNER_TSX: [{"surface": "tablet", "authority": "VisualControl:visual-regions.jsonl"}],
        UNREGISTERED_CSS: [{"surface": "mobile", "authority": "VisualControl:layers.jsonl"}],
    }
    manifest_rows = {
        SOURCE: [{"surface": "tablet", "authority": "visual-source-manifest:source"}],
        OUTPUT: [{"surface": "tablet", "authority": "visual-source-manifest:output"}],
        GENERATED_SOURCE: [{"surface": "web", "authority": "visual-source-manifest:source"}],
        GENERATED: [{"surface": "web", "authority": "visual-source-manifest:output"}],
    }
    return {
        "index": {"schema": "prisma.visual.application.target-index.v1", "globalBlockers": [], "records": rows},
        "surfaceScopes": {
            "tablet": ["apps/terminal-de-venta-system/products/tablet"],
            "pc": ["apps/terminal-de-venta-system/products/pc"],
            "mobile": ["apps/terminal-de-venta-system/products/mobile"],
            "web": ["apps/terminal-de-venta-system/products/web"],
            "chart-lab": ["apps/terminal-de-venta-system/products/chart-lab"],
            "control-center": ["apps/terminal-de-venta-system/prisma-control-center"],
            "shared-ui": ["apps/terminal-de-venta-system/products/shared-ui", "apps/terminal-de-venta-system/tools/quality"],
        },
        "visualRowsByPath": visual_rows,
        "manifestRowsByPath": manifest_rows,
        "generatedOutputs": {GENERATED: {"source": GENERATED_SOURCE}, OUTPUT: {"source": SOURCE}},
        "targetsById": by_id,
        "targetsByPath": by_path,
        "routes": {s: set() for s in ("tablet", "pc", "mobile", "web", "chart-lab", "control-center", "shared-ui")},
        "selectors": {"tablet": {".exact", ".census"}},
        "ledger": {"capability": {"id": "visual.generic_application_engine_v1"}, "errors": []},
    }


def mandatory(status="PASS_GVAE_MANDATORY_GATE", protected=None, errors=None):
    return {"status": status, "protectedChanged": protected or [], "errors": errors or []}


class VisualWorkEntryGateTests(unittest.TestCase):
    def test_01_exact_with_receipt_passes_diff(self):
        a = authority([exact()])
        result = evaluate_changed(authority=a, changed=[SOURCE, OUTPUT], mandatory_result=mandatory())
        self.assertEqual(result["status"], "PASS_VISUAL_WORK_ENTRY_DIFF_GATE")

    def test_02_exact_without_receipt_fails(self):
        a = authority([exact()])
        result = evaluate_changed(authority=a, changed=[SOURCE], mandatory_result=mandatory("BLOCKED_GVAE_MANDATORY_GATE", [SOURCE], ["GVAE_RECEIPT_REQUIRED"]))
        self.assertEqual(result["status"], "BLOCKED_VISUAL_WORK_ENTRY_DIFF_GATE")

    def test_03_census_direct_edit_fails(self):
        result = evaluate_changed(authority=authority(), changed=[CENSUS_FILE], mandatory_result=mandatory())
        self.assertTrue(any("REGISTER_TARGET_FIRST_REQUIRED" in e for e in result["errors"]))

    def test_04_unregistered_visual_owned_file_fails(self):
        result = evaluate_changed(authority=authority(), changed=[UNREGISTERED_CSS], mandatory_result=mandatory())
        self.assertTrue(any("UNREGISTERED_GOVERNED_VISUAL_MUTATION" in e for e in result["errors"]))

    def test_05_nonvisual_file_no_false_positive(self):
        result = evaluate_changed(authority=authority(), changed=["docs/README.md"], mandatory_result=mandatory())
        self.assertEqual(result["status"], "PASS_VISUAL_WORK_ENTRY_DIFF_GATE")
        self.assertEqual(result["visualChangedCount"], 0)

    def test_06_wildcard_request_blocked(self):
        r = decide_request({"task":"visual work","surface":"tablet","files":["apps/**"]}, authority=authority(), current_head=HEAD)
        self.assertEqual(r["decision"], "BLOCKED")

    def test_07_census_target_register_first(self):
        r = decide_request({"task":"visual work","surface":"tablet","targetIds":[CENSUS]}, authority=authority(), current_head=HEAD)
        self.assertEqual(r["decision"], "REGISTER_TARGET_FIRST")

    def test_08_exact_apply_ready_routes_to_gvae(self):
        r = decide_request({"task":"visual work","surface":"tablet","targetIds":[EXACT]}, authority=authority(), current_head=HEAD)
        self.assertEqual(r["decision"], "GVAE_EXACT_APPLY")

    def test_09_blocked_exact_target_blocked(self):
        a = authority([exact("BLOCKED", ["adapter"])])
        r = decide_request({"task":"visual work","surface":"tablet","targetIds":[EXACT]}, authority=a, current_head=HEAD)
        self.assertEqual(r["decision"], "BLOCKED")

    def test_10_whole_surface_with_discovery_gaps_never_apply(self):
        r = decide_request({"task":"whole tablet visual","surface":"tablet"}, authority=authority(), current_head=HEAD)
        self.assertEqual(r["decision"], "SURFACE_BATCH_PLAN")
        self.assertFalse(r["details"]["plans"][0]["ready"])

    def test_11_ambiguous_ownership_blocked(self):
        a = authority()
        a["visualRowsByPath"][CENSUS_FILE].append({"surface":"pc","authority":"VisualControl:layers.jsonl"})
        r = decide_request({"task":"visual work","files":[CENSUS_FILE]}, authority=a, current_head=HEAD)
        self.assertEqual(r["decision"], "BLOCKED")
        self.assertIn("AMBIGUOUS_VISUAL_OWNERSHIP", r["reasons"])

    def test_12_execution_missing_layer_map_authority_blocked(self):
        r = decide_request({"task":"visual work","surface":"tablet","targetIds":[EXACT],"mode":"APPLY"}, authority=authority(), current_head=HEAD)
        self.assertEqual(r["decision"], "BLOCKED")
        self.assertIn("CURRENT_TASK_AUTHORITY_MESH_REQUIRED", r["reasons"])

    def test_13_generated_projection_manual_edit_fails(self):
        r = evaluate_changed(authority=authority(), changed=[GENERATED], mandatory_result=mandatory())
        self.assertTrue(any("GENERATED_PROJECTION_MANUAL_EDIT" in e for e in r["errors"]))

    def test_14_fake_receipt_failure_propagates(self):
        a=authority([exact()])
        r=evaluate_changed(authority=a,changed=[SOURCE],mandatory_result=mandatory("BLOCKED_GVAE_MANDATORY_GATE",[SOURCE],["RECEIPT_DIGEST_INVALID"]))
        self.assertIn("RECEIPT_DIGEST_INVALID",r["errors"])

    def test_15_important_mutation_fails(self):
        r=evaluate_changed(authority=authority(),changed=[CENSUS_FILE],mandatory_result=mandatory(),important_paths=[CENSUS_FILE])
        self.assertTrue(any("PRIORITY_OVERRIDE_FORBIDDEN" in e for e in r["errors"]))

    def test_16_stale_source_hash_blocks_request(self):
        a=authority([exact("APPLY_READY",["source-hash-drift"])])
        r=decide_request({"task":"visual work","targetIds":[EXACT]},authority=a,current_head=HEAD)
        self.assertEqual(r["decision"],"BLOCKED")

    def test_17_cross_surface_target_mismatch_blocked(self):
        r=decide_request({"task":"visual work","surface":"pc","targetIds":[EXACT]},authority=authority(),current_head=HEAD)
        self.assertEqual(r["decision"],"BLOCKED")

    def test_18_shared_ui_is_governed_surface(self):
        a=authority()
        path="apps/terminal-de-venta-system/products/shared-ui/prisma/tokens/theme.css"
        a["visualRowsByPath"][path]=[{"surface":"shared-ui","authority":"VisualControl:layers.jsonl"}]
        info=classify_path(path,a)
        self.assertTrue(info["visual"])
        self.assertEqual(info["surfaces"],["shared-ui"])

    def test_19_scoped_run_authority_path_is_nonvisual_mutation(self):
        r=evaluate_changed(authority=authority(),changed=["apps/terminal-de-venta-system/.prisma-ui/surface-runs/tablet/registry.json"],mandatory_result=mandatory())
        self.assertEqual(r["status"],"PASS_VISUAL_WORK_ENTRY_DIFF_GATE")

    def test_20_census_presence_never_becomes_apply_ready(self):
        r=decide_request({"task":"visual work","targetIds":[CENSUS]},authority=authority(),current_head=HEAD)
        self.assertNotEqual(r["decision"],"GVAE_EXACT_APPLY")

    def test_21_unknown_surface_blocked(self):
        r=decide_request({"task":"visual work","surface":"microwave"},authority=authority(),current_head=HEAD)
        self.assertEqual(r["decision"],"BLOCKED")

    def test_22_expected_head_mismatch_blocked(self):
        r=decide_request({"task":"visual work","surface":"tablet","expectedHead":"b"*40},authority=authority(),current_head=HEAD)
        self.assertEqual(r["decision"],"BLOCKED")

    def test_23_factory_ledger_failure_blocks(self):
        a=authority(); a["ledger"]["errors"]=["FACTORY_LEDGER_DNR_REQUIRED"]
        r=decide_request({"task":"visual work","targetIds":[EXACT]},authority=a,current_head=HEAD)
        self.assertEqual(r["decision"],"BLOCKED")

    def test_24_current_task_mesh_execution_passes(self):
        mesh={"status":"PASS_COMPOSED_AUTHORITY_MESH","repoHead":HEAD,"requiredAuthorityCoveragePct":100,"blockers":0,"layerMapPresent":True,"requestDigest":"1"*64,"artifactDigest":"2"*64}
        r=decide_request({"task":"visual work","surface":"tablet","targetIds":[EXACT],"mode":"APPLY","authorityMesh":mesh},authority=authority(),current_head=HEAD)
        self.assertEqual(r["decision"],"GVAE_EXACT_APPLY")

    def test_25_stale_mesh_execution_blocked(self):
        mesh={"status":"PASS_COMPOSED_AUTHORITY_MESH","repoHead":"b"*40,"requiredAuthorityCoveragePct":100,"blockers":0,"layerMapPresent":True,"requestDigest":"1"*64,"artifactDigest":"2"*64}
        r=decide_request({"task":"visual work","surface":"tablet","targetIds":[EXACT],"mode":"APPLY","authorityMesh":mesh},authority=authority(),current_head=HEAD)
        self.assertEqual(r["decision"],"BLOCKED")

    def test_26_direct_edit_intent_blocked(self):
        r=decide_request({"task":"visual work","surface":"tablet","mode":"DIRECT_EDIT"},authority=authority(),current_head=HEAD)
        self.assertEqual(r["decision"],"BLOCKED")

    def test_27_target_index_global_blocker_blocks(self):
        a=authority(); a["index"]["globalBlockers"]=["authority-drift"]
        r=decide_request({"task":"visual work","targetIds":[EXACT]},authority=a,current_head=HEAD)
        self.assertEqual(r["decision"],"BLOCKED")


if __name__ == "__main__":
    unittest.main()
