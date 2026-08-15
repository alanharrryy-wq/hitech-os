from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_atlas.app_map.uimap.discovery import CssTarget, UiCandidate
from code_atlas.app_map.uimap.governed_markers import (
    certified_pilot_alias_for_candidate,
    load_certified_pilot_contracts,
)
from code_atlas.ui_bridge.binding_promotion import evaluate_component, resolve_pilot_contracts
from code_atlas.ui_bridge.repository import BridgeRepository

SOURCE_OWNER = "apps/terminal-de-venta-system/products/pc/app/components/inventory/inventory-workspace.tsx"
CSS_OWNER = "apps/terminal-de-venta-system/products/pc/app/components/inventory/pc-inventory-master-detail.module.css"
PILOT_UI = "PC-STOCK-FICHA-PANEL-01"
HEURISTIC_UI = "PC-STOCK-MAIN-COMPONENTS-INVENTORY-INVENTORY-WORKSPACE-PRODUCT-FICHA-TAB-01"
CERTIFIED_BINDING = "BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1"
CERTIFIED_LAYER = "LYR.SURFACE.OPERATIONAL.DETAIL"
CERTIFIED_IMPLEMENTATION_LAYER = "products.pc.app.components.inventory.pc.inventory.master.detail.module.css.productficha"
CERTIFIED_ADAPTER = "ADP.PC.DENSE.CLOUDGLASS.V1"


def pilot_payload() -> dict:
    return {
        "schema": "PRISMA_PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1",
        "status": "EXACT_TARGET_AUTHORIZED_FOR_GOVERNED_APPLICATION",
        "taskId": "PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1",
        "pilot": {
            "surfaceId": "SURF.pc.backoffice",
            "routeId": "ROUTE.pc.stock",
            "runtimeRoute": "/stock",
            "ownerId": "OWN.pc.inventory.stock_ficha",
            "ownerSymbol": "StockFicha",
            "regionId": "ZONE.pc.stock.detail",
            "slotId": "SLOT.pc.stock.detail.primary",
            "componentUiId": PILOT_UI,
            "recipeId": "REC.panel.operational.cloudglass",
            "visualStackId": "VSTACK.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1",
            "bindingId": CERTIFIED_BINDING,
            "adapterId": CERTIFIED_ADAPTER,
            "neutralLayerId": CERTIFIED_LAYER,
            "implementationLayerId": CERTIFIED_IMPLEMENTATION_LAYER,
            "runtimeSelector": "[data-pcinv-product-ficha=\"stock\"]",
            "sourceOwner": SOURCE_OWNER,
            "cssOwner": CSS_OWNER,
        },
    }


def candidate(route_path: str = "/stock", ui_id: str = PILOT_UI) -> UiCandidate:
    attrs = {
        "data-prisma-visual-pilot": "pc-stock-ficha-tablet-licenses-v1",
        "data-prisma-surface": "pc",
        "data-prisma-route": "/stock",
        "data-prisma-owner": "StockFicha",
        "data-prisma-region": "ZONE.pc.stock.detail",
        "data-prisma-slot": "SLOT.pc.stock.detail.primary",
        "data-prisma-component-ui-id": ui_id,
        "data-prisma-recipe": "REC.panel.operational.cloudglass",
        "data-prisma-visual-stack": "VSTACK.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1",
        "data-prisma-binding": CERTIFIED_BINDING,
        "data-prisma-adapter": CERTIFIED_ADAPTER,
        "data-prisma-neutral-layer": CERTIFIED_LAYER,
        "data-prisma-source-owner": "inventory-workspace.tsx",
        "data-prisma-css-owner": "pc-inventory-master-detail.module.css",
    }
    return UiCandidate(
        runtime_alias="pc",
        route_path=route_path,
        route_id="ROUTE.pc.stock" if route_path == "/stock" else "ROUTE.pc.counts",
        route_source_file=f"apps/terminal-de-venta-system/products/pc/app/app/{route_path.strip('/')}/page.tsx",
        render_source_file=SOURCE_OWNER,
        render_symbol="InventoryWorkspaceView",
        owner_file=SOURCE_OWNER,
        owner_symbol="InventoryWorkspaceView",
        class_name="productFicha",
        tag_name="section",
        widget_kind="control",
        text_hint="",
        instance_policy="SINGLE_OR_STATIC",
        data_attributes=attrs,
        source_hash="A" * 64,
    )


def css_target() -> CssTarget:
    return CssTarget(
        class_name="productFicha",
        selector='.productFicha[data-prisma-visual-pilot="pc-stock-ficha-tablet-licenses-v1"]',
        source_file=CSS_OWNER,
        source_hash="B" * 64,
        pseudo_element=None,
        state_selector="default",
        at_rule=None,
        anchor_kind="CSS_MODULE_CLASS",
        target_role="ROOT",
        declarations={},
    )


def canonical_component() -> dict:
    return {
        "runtimeAlias": "pc",
        "surfaceId": "SURF.pc.stock",
        "interfaceId": "IFC.pc.stock.interface",
        "routeId": "ROUTE.pc.stock",
        "routePath": "/stock",
        "regionId": "ZONE.pc.stock.main",
        "slotId": "SLOT.pc.stock.main.components_inventory_inventory_workspace.product_ficha",
        "componentId": "WGT.pc.stock.components_inventory_inventory_workspace.product_ficha",
        "componentUiId": HEURISTIC_UI,
        "widgetTypeId": "WID.control",
        "neutralMeaningId": None,
        "relatedNeutralIds": [],
        "ownerId": "OWN.pc.components_inventory_inventory_workspace",
        "ownerFile": SOURCE_OWNER,
        "ownerSymbol": "InventoryWorkspaceView",
        "renderSourceFile": SOURCE_OWNER,
        "renderSymbol": "InventoryWorkspaceView",
        "visualTargets": [{
            "visualTargetId": "VTR.X.ROOT.01",
            "targetRole": "ROOT",
            "styleSourceFile": CSS_OWNER,
            "anchorKind": "CSS_MODULE_CLASS",
            "anchorValue": "productFicha",
            "selector": ".productFicha",
            "pseudoElement": None,
            "stateSelector": "default",
            "atRule": None,
            "implementationLayerId": None,
            "sourceHash": "B" * 64,
        }],
        "bindingId": None,
        "layerId": None,
        "implementationLayerId": None,
        "adapterId": "ADP.PC.ADMIN.V2",
        "recipeCompatibility": {"coverageStatus": "PARTIAL_VISUAL_STATE_COVERAGE", "compatibleRecipeIds": []},
        "stateSupport": {},
        "evidenceRefs": [],
        "sourceHashes": {SOURCE_OWNER: "A" * 64, CSS_OWNER: "B" * 64},
        "ndcStatus": "CANDIDATE",
        "confidence": "MEDIUM",
        "targetResolutionStatus": "BLOCKED_BY_MISSING_LAYER",
        "applicationReadiness": "BLOCKED",
        "blockingReasons": ["MISSING_CERTIFIED_LAYER", "MISSING_IMPLEMENTATION_LAYER", "MISSING_VISUAL_BINDING", "NEUTRAL_MEANING_NOT_PROVEN"],
        "instancePolicy": "SINGLE_OR_STATIC",
        "projectionOfComponentId": None,
        "legacyIdPreserved": False,
    }


class CertifiedPilotCrosswalkTests(unittest.TestCase):
    def make_index(self, root: Path) -> dict:
        path = root / "apps/terminal-de-venta-system/products/pc/app/docs/visual-pilots/PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.contract.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pilot_payload()), encoding="utf-8")
        return load_certified_pilot_contracts(root)

    def test_exact_certified_pilot_promotes_governed_identity_atomically(self):
        with tempfile.TemporaryDirectory() as tmp:
            component = canonical_component()
            alias, conflict = certified_pilot_alias_for_candidate(
                candidate(), [css_target()], component, self.make_index(Path(tmp))
            )

            self.assertIsNone(conflict)
            self.assertEqual(component["componentUiId"], PILOT_UI)
            self.assertEqual(component["surfaceId"], "SURF.pc.backoffice")
            self.assertEqual(component["ownerId"], "OWN.pc.inventory.stock_ficha")
            self.assertEqual(component["ownerSymbol"], "StockFicha")
            self.assertEqual(component["regionId"], "ZONE.pc.stock.detail")
            self.assertEqual(component["slotId"], "SLOT.pc.stock.detail.primary")
            self.assertEqual(component["bindingId"], CERTIFIED_BINDING)
            self.assertEqual(component["layerId"], CERTIFIED_LAYER)
            self.assertEqual(component["implementationLayerId"], CERTIFIED_IMPLEMENTATION_LAYER)
            self.assertEqual(component["adapterId"], CERTIFIED_ADAPTER)
            self.assertEqual(component["visualTargets"][0]["implementationLayerId"], CERTIFIED_IMPLEMENTATION_LAYER)
            self.assertIsNone(component["neutralMeaningId"])
            self.assertEqual(component["targetResolutionStatus"], "PARTIAL")
            self.assertEqual(component["applicationReadiness"], "BLOCKED")
            self.assertEqual(component["blockingReasons"], ["NEUTRAL_MEANING_NOT_PROVEN"])
            self.assertTrue(any(row.get("evidenceType") == "CERTIFIED_VISUAL_PILOT_CONTRACT" for row in component["evidenceRefs"]))

            self.assertEqual(alias["aliasId"], HEURISTIC_UI)
            self.assertEqual(alias["canonicalComponentUiId"], PILOT_UI)
            self.assertEqual(alias["reason"], "CERTIFIED_GOVERNED_IDENTITY_PROMOTED")
            self.assertEqual(alias["pilotTrace"]["adapterId"], CERTIFIED_ADAPTER)
            self.assertEqual(alias["formerCanonicalTrace"]["adapterId"], "ADP.PC.ADMIN.V2")
            self.assertEqual(alias["canonicalTrace"]["componentUiId"], PILOT_UI)
            self.assertNotIn("neutralMeaningId", alias["pilotTrace"])

    def test_shared_source_on_other_route_is_not_false_conflict_or_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            component = canonical_component()
            before = json.loads(json.dumps(component))
            alias, conflict = certified_pilot_alias_for_candidate(
                candidate(route_path="/counts"), [css_target()], component, self.make_index(Path(tmp))
            )
            self.assertIsNone(alias)
            self.assertIsNone(conflict)
            self.assertEqual(component, before)

    def test_unregistered_explicit_pilot_marker_fails_closed_without_mutation(self):
        component = canonical_component()
        before = json.loads(json.dumps(component))
        alias, conflict = certified_pilot_alias_for_candidate(
            candidate(ui_id="PC-UNKNOWN-PILOT-01"), [css_target()], component, {}
        )
        self.assertIsNone(alias)
        self.assertIn("CERTIFIED_PILOT_CONTRACT_NOT_FOUND", conflict["blockingReasons"])
        self.assertEqual(component, before)

    def test_bridge_resolves_heuristic_compatibility_alias_to_governed_component(self):
        with tempfile.TemporaryDirectory() as tmp:
            component = canonical_component()
            alias, conflict = certified_pilot_alias_for_candidate(
                candidate(), [css_target()], component, self.make_index(Path(tmp))
            )
            self.assertIsNone(conflict)
            batch = {
                "schema": "test",
                "batchId": "BATCH.TEST",
                "runtimeAlias": "pc",
                "components": [component],
                "aliases": [alias],
            }
            repository = BridgeRepository([batch], [])
            self.assertEqual(repository.resolve_alias(HEURISTIC_UI), PILOT_UI)
            self.assertEqual(repository.resolve_alias(PILOT_UI), PILOT_UI)
            self.assertEqual(repository.component(HEURISTIC_UI)["adapterId"], CERTIFIED_ADAPTER)
            self.assertEqual(repository.component(PILOT_UI)["componentUiId"], PILOT_UI)

    def test_binding_promotion_sees_governed_id_directly_but_stays_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            component = canonical_component()
            alias, conflict = certified_pilot_alias_for_candidate(
                candidate(), [css_target()], component, self.make_index(Path(tmp))
            )
            self.assertIsNone(conflict)
            batch = {
                "schema": "test",
                "batchId": "BATCH.TEST",
                "runtimeAlias": "pc",
                "components": [component],
                "aliases": [alias],
            }
            repository = BridgeRepository([batch], [])
            raw = {
                PILOT_UI: {
                    "path": "pilot.contract.json",
                    "schema": pilot_payload()["schema"],
                    "status": pilot_payload()["status"],
                    "pilot": pilot_payload()["pilot"],
                }
            }
            resolved = resolve_pilot_contracts(repository, raw)
            row = evaluate_component(component, set(), resolved)
            self.assertTrue(row["pilotAlignment"]["aligned"])
            self.assertEqual(row["pilotAlignment"]["identityResolution"], "DIRECT_CANONICAL_ID")
            self.assertEqual(row["pilotAlignment"]["pilotComponentUiId"], PILOT_UI)
            self.assertEqual(row["pilotAlignment"]["canonicalComponentUiId"], PILOT_UI)
            self.assertIn("MISSING_COORDINATE:neutralMeaningId", row["blockingReasons"])
            self.assertIn("TARGET_NOT_SOURCE_RESOLVED", row["blockingReasons"])
            self.assertEqual(row["uimapState"]["applicationReadiness"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
