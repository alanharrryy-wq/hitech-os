from __future__ import annotations
import json
import tempfile
from pathlib import Path

from code_atlas.app_map.uimap.contracts import SCHEMA_VERSION, add_integrity

from .application import apply_plan
from .canonical import canonical_sha256
from .errors import ApplicationDisabledError
from .recipes import RecipeRepository
from .repository import BridgeRepository
from .planner import build_plan


def _component() -> dict:
    return {
        "schema": "prisma.ui.component-record.v1", "schemaVersion": SCHEMA_VERSION,
        "runtimeAlias": "tb", "surfaceId": "SURF.tb.pos", "interfaceId": "IFC.tb.retail.pos_sale", "routeId": "ROUTE.tb.pos", "routePath": "/pos",
        "regionId": "ZONE.tb.pos.payment", "slotId": "SLOT.tb.pos.payment.cobrar", "componentId": "WGT.tb.pos.cobrar", "componentUiId": "TB-POS-PAY-COBRAR-BTN-01",
        "widgetTypeId": "WID.button.primary", "neutralMeaningId": "ACT.sale.checkout", "relatedNeutralIds": ["ENT.sale"],
        "ownerId": "OWN.tb.pos_ticket_panel", "ownerFile": "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-ticket-panel.tsx", "ownerSymbol": "PosTicketPanel",
        "renderSourceFile": "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-ticket-panel.tsx", "renderSymbol": "PosTicketPanel",
        "visualTargets": [{"visualTargetId":"VTR.TB-POS-PAY-COBRAR-BTN-01.ROOT","targetRole":"ROOT","styleSourceFile":"apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css","anchorKind":"CSS_MODULE_CLASS","anchorValue":"cobrarReferenceButton","selector":".cobrarReferenceButton","pseudoElement":None,"stateSelector":"default","atRule":None,"implementationLayerId":"products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton","sourceHash":"0"*64}],
        "bindingId": "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1", "layerId": "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE", "implementationLayerId": "products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton",
        "adapterId": "ADP.TB.TOUCH.V2", "recipeCompatibility": {"coverageStatus":"CURRENT_SOURCE_COVERAGE_COMPLETE","compatibleRecipeIds":["REC.button.primary"],"hoverPolicy":"substitute-pressed"},
        "stateSupport": {"default":"SOURCE_DEFINED","hover":"SOURCE_DEFINED","focus":"SOURCE_DEFINED","focus-visible":"SOURCE_DEFINED","pressed":"SOURCE_DEFINED","disabled":"SOURCE_DEFINED","loading":"SOURCE_DEFINED","reduced-motion":"SOURCE_DEFINED","success":"NOT_APPLICABLE","warning":"NOT_APPLICABLE","error":"NOT_APPLICABLE"},
        "evidenceRefs":[{"evidenceType":"SELFTEST_FIXTURE","sourceFile":"selftest.py"}], "sourceHashes":{"apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css":"0"*64},
        "ndcStatus":"CONFIRMED", "confidence":"VERY_HIGH", "targetResolutionStatus":"SOURCE_RESOLVED", "applicationReadiness":"ELIGIBLE_FOR_AUTHORITY_PREFLIGHT", "blockingReasons":[],
        "instancePolicy":"SINGLE_OR_STATIC", "projectionOfComponentId":None, "legacyIdPreserved":False,
    }


def main() -> int:
    component = _component()
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        css = root / "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css"
        css.parent.mkdir(parents=True)
        css.write_text(".cobrarReferenceButton{}", encoding="utf-8")
        from .canonical import file_sha256
        digest = file_sha256(css).upper()
        component["sourceHashes"] = {"apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css": digest}
        component["visualTargets"][0]["sourceHash"] = digest
        contract_hash = canonical_sha256({"version":"1"}).upper()
        batch = add_integrity({"schema":"prisma.ui.component-batch.v1","schemaVersion":SCHEMA_VERSION,"batchId":"BATCH.tb.selftest00000001","supersedesBatchId":None,"contractHash":contract_hash,"runtimeAlias":"tb","sourceSnapshotHash":"F"*64,"components":[component],"aliases":[],"conflicts":[],"coverage":{},"integrity":{}})
        bridge = BridgeRepository([batch], [])
        assert bridge.validation["ok"], bridge.validation
        recipe_path = root / "recipe.json"
        recipe_path.write_text(json.dumps({"recipeId":"REC.button.primary","target":{"componentUiId":"TB-POS-PAY-COBRAR-BTN-01"},"values":{"visualStack":{"units":[{"unitId":"base","kind":"BASE_SELECTOR","selector":".cobrarReferenceButton","applicationPolicy":"EXPLICIT_REPLACE_VISUAL_PRESERVE_STRUCTURE","properties":{"color":{"mode":"TOKEN","value":"color.accentText"}}}]}}}), encoding="utf-8")
        recipes = RecipeRepository.load([recipe_path])
        plan1, diff1 = build_plan(bridge, recipes, component["componentUiId"], str(root))
        plan2, diff2 = build_plan(bridge, recipes, component["componentUiId"], str(root))
        stable1 = dict(plan1); stable2 = dict(plan2); stable1.pop("createdAt", None); stable2.pop("createdAt", None)
        assert canonical_sha256(stable1) == canonical_sha256(stable2)
        assert diff1["checksum"] == diff2["checksum"]
    try:
        apply_plan({})
    except ApplicationDisabledError:
        pass
    else:
        raise AssertionError("Application must remain disabled")
    assert component["bindingId"] == "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1"
    assert component["layerId"] == "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE"
    assert component["implementationLayerId"] == "products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton"
    print("PASS_PRISMA_UI_BRIDGE_V1_SELFTEST")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
