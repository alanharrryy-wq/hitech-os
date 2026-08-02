from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path

from code_atlas.app_map.uimap.contracts import SCHEMA_VERSION, add_integrity
from code_atlas.app_map.uimap.runner import run_uimap
from code_atlas.app_map.uimap.tests import FIXED_TIME, fixture_tree
from code_atlas.cli.main import main as code_atlas_main
from code_atlas.ui_bridge.application import apply_plan
from code_atlas.ui_bridge.canonical import canonical_sha256, file_sha256
from code_atlas.ui_bridge.errors import ApplicationDisabledError
from code_atlas.ui_bridge.planner import build_plan
from code_atlas.ui_bridge.recipes import RecipeRepository
from code_atlas.ui_bridge.repository import BridgeRepository
from code_atlas.ui_bridge.validation import validate_batches, validate_component


def component() -> dict:
    return {
        "schema":"prisma.ui.component-record.v1","schemaVersion":SCHEMA_VERSION,
        "runtimeAlias":"tb","surfaceId":"SURF.tb.pos","interfaceId":"IFC.tb.retail.pos_sale","routeId":"ROUTE.tb.pos","routePath":"/pos","regionId":"ZONE.tb.pos.payment","slotId":"SLOT.tb.pos.payment.cobrar","componentId":"WGT.tb.pos.cobrar","componentUiId":"TB-POS-PAY-COBRAR-BTN-01","widgetTypeId":"WID.button","neutralMeaningId":"ACT.sale.checkout","relatedNeutralIds":["ENT.sale"],"ownerId":"OWN.tb.pos_ticket_panel","ownerFile":"app/pos-ticket-panel.tsx","ownerSymbol":"PosTicketPanel","renderSourceFile":"app/pos-ticket-panel.tsx","renderSymbol":"PosTicketPanel","visualTargets":[{"visualTargetId":"VTR.TB-POS-PAY-COBRAR-BTN-01.ROOT","targetRole":"ROOT","styleSourceFile":"app/pos.module.css","anchorKind":"CSS_MODULE_CLASS","anchorValue":"cobrarReferenceButton","selector":".cobrarReferenceButton","pseudoElement":None,"stateSelector":"default","atRule":None,"implementationLayerId":"products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton","sourceHash":"0"*64}],"bindingId":"BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1","layerId":"LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE","implementationLayerId":"products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton","adapterId":"ADP.TB.TOUCH.V2","recipeCompatibility":{"coverageStatus":"CURRENT_SOURCE_COVERAGE_COMPLETE","compatibleRecipeIds":["REC.button.primary"],"hoverPolicy":"substitute-pressed"},"stateSupport":{"default":"SOURCE_DEFINED","hover":"SOURCE_DEFINED","focus":"SOURCE_DEFINED","focus-visible":"SOURCE_DEFINED","pressed":"SOURCE_DEFINED","disabled":"SOURCE_DEFINED","loading":"SOURCE_DEFINED","reduced-motion":"SOURCE_DEFINED","success":"NOT_APPLICABLE","warning":"NOT_APPLICABLE","error":"NOT_APPLICABLE"},"evidenceRefs":[{"evidenceType":"TEST_FIXTURE","sourceFile":"test_ui_bridge_v1.py"}],"sourceHashes":{"app/pos.module.css":"0"*64},"ndcStatus":"CONFIRMED","confidence":"VERY_HIGH","targetResolutionStatus":"SOURCE_RESOLVED","applicationReadiness":"ELIGIBLE_FOR_AUTHORITY_PREFLIGHT","blockingReasons":[],"instancePolicy":"SINGLE_OR_STATIC","projectionOfComponentId":None,"legacyIdPreserved":False
    }

def batch(c=None, aliases=None):
    components = c if isinstance(c, list) else [c or component()]
    return add_integrity({"schema":"prisma.ui.component-batch.v1","schemaVersion":SCHEMA_VERSION,"batchId":"BATCH.tb.test000000000001","supersedesBatchId":None,"contractHash":"A"*64,"runtimeAlias":"tb","sourceSnapshotHash":"B"*64,"components":components,"aliases":aliases or [],"conflicts":[],"coverage":{},"integrity":{}})

class BridgeTests(unittest.TestCase):
    def test_canonical_determinism(self):
        self.assertEqual(canonical_sha256({"b":2,"a":1}), canonical_sha256({"a":1,"b":2}))
    def test_duplicate_id_conflict(self):
        one=component(); two=component(); two["ownerSymbol"]="Other"
        report=validate_batches([{**batch(one),"components":[one,two]}])
        self.assertTrue(any(i["code"]=="DUPLICATE_CANONICAL_ID" for i in report["issues"]))
    def test_alias_cycle_blocked(self):
        report=validate_batches([batch(aliases=[{"aliasId":"A","canonicalId":"B"},{"aliasId":"B","canonicalId":"A"}])])
        self.assertTrue(any(i["code"]=="ALIAS_CYCLE" for i in report["issues"]))
    def test_generated_projection_protected(self):
        c=component(); c["visualTargets"][0]["anchorKind"]="GENERATED_PROJECTION"
        self.assertTrue(any(i["code"]=="GENERATED_PATCH_POLICY_REQUIRED" for i in validate_component(c)))
    def test_repeated_data_no_instance_ids(self):
        c=component(); c["instancePolicy"]="REPEATED_BY_DATA"; c["instanceIdPattern"]="row-*"
        self.assertTrue(any(i["code"]=="DATA_INSTANCE_IDS_FORBIDDEN" for i in validate_component(c)))
    def test_touch_hover_policy(self):
        c=component(); c["stateSupport"]["hover"]="NOT_APPLICABLE"; c["recipeCompatibility"]["hoverPolicy"]="substitute-pressed"
        self.assertFalse(any(i["code"]=="TOUCH_HOVER_SUBSTITUTION_INVALID" for i in validate_component(c)))
    def test_coverage_terms_are_distinct(self):
        c=component(); c["recipeCompatibility"]["coverageStatus"]="COMPLETE"
        self.assertTrue(any(i["code"]=="INVALID_RECIPE_COVERAGE" for i in validate_component(c)))
    def test_application_disabled(self):
        with self.assertRaises(ApplicationDisabledError): apply_plan({})
    def test_cobrar_ids_preserved(self):
        c=component(); self.assertEqual(c["bindingId"],"BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1"); self.assertEqual(c["layerId"],"LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE")
    def test_deterministic_plan(self):
        c=component()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); f=root/'app/pos.module.css'; f.parent.mkdir(parents=True); f.write_text('.cobrarReferenceButton{}',encoding='utf-8')
            d=file_sha256(f).upper(); c['sourceHashes']={'app/pos.module.css':d}; c['visualTargets'][0]['sourceHash']=d
            r=root/'recipe.json'; r.write_text(json.dumps({"recipeId":"REC.button.primary","target":{"componentUiId":c['componentUiId']},"values":{"visualStack":{"units":[{"unitId":"base","kind":"BASE_SELECTOR","selector":".cobrarReferenceButton","applicationPolicy":"EXPLICIT_REPLACE","properties":{"color":{"mode":"TOKEN","value":"color.accentText"}}}]}}}),encoding='utf-8')
            repo=BridgeRepository([batch(c)],[]); recipes=RecipeRepository.load([r]); p1,d1=build_plan(repo,recipes,c['componentUiId'],str(root)); p2,d2=build_plan(repo,recipes,c['componentUiId'],str(root)); p1.pop('createdAt'); p2.pop('createdAt'); self.assertEqual(canonical_sha256(p1),canonical_sha256(p2)); self.assertEqual(d1['checksum'],d2['checksum'])

    def test_partial_target_allows_nullable_implementation_layer(self):
        c=component()
        c.update({
            "bindingId": None,
            "layerId": None,
            "implementationLayerId": None,
            "targetResolutionStatus": "PARTIAL",
            "applicationReadiness": "BLOCKED",
            "blockingReasons": ["MISSING_LAYER_AUTHORITY"],
            "ndcStatus": "CANDIDATE",
            "confidence": "LOW",
        })
        c["visualTargets"][0]["implementationLayerId"] = None
        issues = validate_component(c)
        self.assertFalse(any(i["code"] == "VISUAL_TARGET_MISSING_FIELDS" for i in issues), issues)
        self.assertFalse(any(i["code"].startswith("UIMAP_COMPONENT_") for i in issues), issues)

    def test_precise_uimap_alias_resolves(self):
        c=component()
        alias={"aliasId":"TB-POS-PAY-COBRAR-BTN-00","canonicalComponentUiId":c["componentUiId"],"canonicalComponentId":c["componentId"],"canonicalOwnerFile":c["ownerFile"],"dedupeKeyHash":"C"*64,"reason":"SAME_OWNER_PROJECTION_DEDUPLICATED","status":"INTERNAL"}
        repo=BridgeRepository([batch(c,[alias])],[])
        self.assertEqual(repo.component(alias["aliasId"])["componentUiId"], c["componentUiId"])
        self.assertTrue(repo.validation["ok"], repo.validation)

    def test_alias_provenance_mismatch_is_blocked(self):
        c=component()
        alias={"aliasId":"TB-POS-PAY-COBRAR-BTN-00","canonicalComponentUiId":c["componentUiId"],"canonicalComponentId":"WGT.tb.pos.wrong","canonicalOwnerFile":"wrong.tsx","dedupeKeyHash":"C"*64,"reason":"SAME_OWNER_PROJECTION_DEDUPLICATED","status":"INTERNAL"}
        report=validate_batches([batch(c,[alias])])
        self.assertTrue(any(i["code"]=="ALIAS_TARGET_INVALID" for i in report["issues"]))

    def test_batches_directory_ignores_immutable_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"batches"; history=root/"history"; history.mkdir(parents=True)
            (root/"01_tb.json").write_text(json.dumps(batch()),encoding="utf-8")
            old=batch(); old["batchId"]="BATCH.tb.old000000000000"; old["contractHash"]="D"*64; old=add_integrity(old)
            (history/"BATCH.tb.old000000000000.json").write_text(json.dumps(old),encoding="utf-8")
            repo=BridgeRepository.load([root])
            self.assertEqual(len(repo.batches),1)

    def test_bridge_consumes_uimap_generated_batches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); product,governor,evidence=fixture_tree(root); out=root/"out"
            result=run_uimap(str(product),str(governor),str(out),str(evidence),run_timestamp=FIXED_TIME)
            self.assertTrue(result["ok"],result["validation"])
            repo=BridgeRepository.load([out/"batches"])
            self.assertTrue(repo.validation["ok"],repo.validation)
            self.assertEqual(repo.component("TB-POS-PAY-COBRAR-BTN-01")["routePath"],"/pos")

    def test_root_code_atlas_cli_routes_ui_bridge(self):
        self.assertEqual(code_atlas_main(["ui-bridge","selftest"]),0)

    def test_recipe_authority_priority_is_input_order_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); coverage=root/"coverage.json"; portable=root/"portable.json"
            coverage.write_text(json.dumps({"schema":"prisma.identity.recipe-coverage-matrix.v1","recipeId":"REC.button.primary","units":[]}),encoding="utf-8")
            portable.write_text(json.dumps({"schema":"prisma.identity.portable-element-export.v2","recipeId":"REC.button.primary","values":{"visualStack":{"units":[]}}}),encoding="utf-8")
            forward=RecipeRepository.load([coverage,portable]); reverse=RecipeRepository.load([portable,coverage])
            self.assertEqual(forward.by_id["REC.button.primary"]["schema"],"prisma.identity.portable-element-export.v2")
            self.assertEqual(forward.by_id["REC.button.primary"]["canonicalPayloadSha256"],reverse.by_id["REC.button.primary"]["canonicalPayloadSha256"])

    def test_plan_resolves_related_targets_from_same_owner(self):
        parent=component(); child=json.loads(json.dumps(parent))
        child.update({"componentId":"WGT.tb.pos.cobrar_icon","componentUiId":"TB-POS-PAY-COBRAR-ICO-01","slotId":"SLOT.tb.pos.payment.cobrar_icon","widgetTypeId":"WID.icon","bindingId":"BND.ACT.PRIMARY.TABLET.POS.COBRAR.ICON.V1","layerId":"LYR.ACT.PRIMARY.TABLET.POS.COBRAR.ICON","implementationLayerId":"products.tablet.app.components.pos.pos.module.css.cobraricon"})
        child["visualTargets"]=[{"visualTargetId":"VTR.TB-POS-PAY-COBRAR-ICO-01.ICON.01","targetRole":"ICON","styleSourceFile":"app/pos.module.css","anchorKind":"CSS_MODULE_CLASS","anchorValue":"cobrarIcon","selector":".cobrarIcon","pseudoElement":None,"stateSelector":"default","atRule":None,"implementationLayerId":child["implementationLayerId"],"sourceHash":"0"*64}]
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); css=root/"app/pos.module.css"; css.parent.mkdir(parents=True); css.write_text('.cobrarReferenceButton{}.cobrarIcon{}',encoding='utf-8')
            digest=file_sha256(css).upper()
            for c in (parent,child):
                c["sourceHashes"]={"app/pos.module.css":digest}
                for target in c["visualTargets"]: target["sourceHash"]=digest
            recipe=root/"recipe.json"; recipe.write_text(json.dumps({"schema":"prisma.identity.portable-element-export.v2","recipeId":"REC.button.primary","values":{"visualStack":{"units":[{"unitId":"base","kind":"BASE_SELECTOR","selector":".cobrarReferenceButton","applicationPolicy":"EXPLICIT_REPLACE","properties":{"color":{"mode":"TOKEN","value":"color.accentText"}}},{"unitId":"icon","kind":"SUBCOMPONENT","selector":".cobrarIcon","applicationPolicy":"EXPLICIT_REPLACE","properties":{"color":{"mode":"TOKEN","value":"color.accentText"}}}]}}}),encoding="utf-8")
            repo=BridgeRepository([batch([parent,child])],[]); recipes=RecipeRepository.load([recipe]); plan,_=build_plan(repo,recipes,parent["componentUiId"],str(root))
            self.assertEqual(plan["status"],"PLAN_READY_FOR_REVIEW",plan["blockingReasons"])
            icon=next(operation for operation in plan["operations"] if operation["unitId"]=="icon")
            self.assertEqual(icon["matchedComponentUiIds"],[child["componentUiId"]])

if __name__=='__main__': unittest.main()
