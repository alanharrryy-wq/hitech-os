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

SOURCE_OWNER = "apps/terminal-de-venta-system/products/pc/app/components/inventory/inventory-workspace.tsx"
CSS_OWNER = "apps/terminal-de-venta-system/products/pc/app/components/inventory/pc-inventory-master-detail.module.css"
PILOT_UI = "PC-STOCK-FICHA-PANEL-01"
HEURISTIC_UI = "PC-STOCK-MAIN-COMPONENTS-INVENTORY-INVENTORY-WORKSPACE-PRODUCT-FICHA-TAB-01"
CERTIFIED_BINDING = "BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1"


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
            "adapterId": "ADP.PC.DENSE.CLOUDGLASS.V1",
            "neutralLayerId": "LYR.SURFACE.OPERATIONAL.DETAIL",
            "implementationLayerId": "products.pc.app.components.inventory.pc.inventory.master.detail.module.css.productficha",
            "runtimeSelector": "[data-pcinv-product-ficha=\"stock\"]",
            "sourceOwner": SOURCE_OWNER,
            "cssOwner": CSS_OWNER,
        },
    }


def candidate_with_binding(binding_id: str) -> UiCandidate:
    return UiCandidate(
        runtime_alias="pc",
        route_path="/stock",
        route_id="ROUTE.pc.stock",
        route_source_file="apps/terminal-de-venta-system/products/pc/app/app/stock/page.tsx",
        render_source_file=SOURCE_OWNER,
        render_symbol="InventoryWorkspaceView",
        owner_file=SOURCE_OWNER,
        owner_symbol="InventoryWorkspaceView",
        class_name="productFicha",
        tag_name="section",
        widget_kind="control",
        text_hint="",
        instance_policy="SINGLE_OR_STATIC",
        data_attributes={
            "data-prisma-visual-pilot": "pc-stock-ficha-tablet-licenses-v1",
            "data-prisma-surface": "pc",
            "data-prisma-route": "/stock",
            "data-prisma-owner": "StockFicha",
            "data-prisma-region": "ZONE.pc.stock.detail",
            "data-prisma-slot": "SLOT.pc.stock.detail.primary",
            "data-prisma-component-ui-id": PILOT_UI,
            "data-prisma-recipe": "REC.panel.operational.cloudglass",
            "data-prisma-visual-stack": "VSTACK.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1",
            "data-prisma-binding": binding_id,
            "data-prisma-adapter": "ADP.PC.DENSE.CLOUDGLASS.V1",
            "data-prisma-neutral-layer": "LYR.SURFACE.OPERATIONAL.DETAIL",
            "data-prisma-source-owner": "inventory-workspace.tsx",
            "data-prisma-css-owner": "pc-inventory-master-detail.module.css",
        },
        source_hash="A" * 64,
    )


def css_target(source_hash: str = "B" * 64) -> CssTarget:
    return CssTarget(
        class_name="productFicha",
        selector='.productFicha[data-prisma-visual-pilot="pc-stock-ficha-tablet-licenses-v1"]',
        source_file=CSS_OWNER,
        source_hash=source_hash,
        pseudo_element=None,
        state_selector="default",
        at_rule=None,
        anchor_kind="CSS_MODULE_CLASS",
        target_role="ROOT",
        declarations={},
    )


def canonical_component(
    owner_hash: str = "A" * 64,
    style_hash: str = "B" * 64,
) -> dict:
    return {
        "runtimeAlias": "pc",
        "surfaceId": "SURF.pc.stock",
        "routeId": "ROUTE.pc.stock",
        "routePath": "/stock",
        "regionId": "ZONE.pc.stock.main",
        "slotId": "SLOT.pc.stock.main.inventory.product_ficha",
        "ownerId": "OWN.pc.inventory_workspace",
        "ownerFile": SOURCE_OWNER,
        "ownerSymbol": "InventoryWorkspaceView",
        "componentId": "WGT.pc.stock.components_inventory_inventory_workspace.product_ficha",
        "componentUiId": HEURISTIC_UI,
        "neutralMeaningId": None,
        "bindingId": None,
        "layerId": None,
        "implementationLayerId": None,
        "adapterId": "ADP.PC.ADMIN.V2",
        "visualTargets": [{
            "styleSourceFile": CSS_OWNER,
            "sourceHash": style_hash,
            "implementationLayerId": None,
        }],
        "evidenceRefs": [],
        "sourceHashes": {SOURCE_OWNER: owner_hash, CSS_OWNER: style_hash},
        "targetResolutionStatus": "BLOCKED_BY_MISSING_LAYER",
        "applicationReadiness": "BLOCKED",
        "blockingReasons": [
            "MISSING_CERTIFIED_LAYER",
            "MISSING_IMPLEMENTATION_LAYER",
            "MISSING_VISUAL_BINDING",
            "NEUTRAL_MEANING_NOT_PROVEN",
        ],
    }


class CertifiedPilotCrosswalkNegativeTests(unittest.TestCase):
    def make_index(self, root: Path) -> dict:
        contract = (
            root
            / "apps/terminal-de-venta-system/products/pc/app/docs/visual-pilots"
            / "PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.contract.json"
        )
        contract.parent.mkdir(parents=True, exist_ok=True)
        contract.write_text(json.dumps(pilot_payload()), encoding="utf-8")
        return load_certified_pilot_contracts(root)

    def assert_withheld_without_mutation(
        self,
        candidate: UiCandidate,
        targets: list[CssTarget],
        component: dict,
        index: dict,
        expected_reason: str,
    ) -> None:
        before = json.loads(json.dumps(component))
        alias, conflict = certified_pilot_alias_for_candidate(candidate, targets, component, index)
        self.assertIsNone(alias)
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict["aliasId"], PILOT_UI)
        self.assertEqual(conflict["resolution"], "ALIAS_WITHHELD")
        self.assertIn(expected_reason, conflict["blockingReasons"])
        self.assertEqual(component, before)

    def test_certified_pilot_with_binding_marker_drift_is_withheld(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_withheld_without_mutation(
                candidate_with_binding("BND.CONFLICT"),
                [css_target()],
                canonical_component(),
                self.make_index(Path(tmp)),
                "CERTIFIED_PILOT_MARKER_MISMATCH:data-prisma-binding",
            )

    def test_render_source_hash_drift_is_withheld(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_withheld_without_mutation(
                candidate_with_binding(CERTIFIED_BINDING),
                [css_target()],
                canonical_component(owner_hash="C" * 64),
                self.make_index(Path(tmp)),
                "CERTIFIED_PILOT_RENDER_SOURCE_HASH_MISMATCH",
            )

    def test_style_source_hash_drift_is_withheld(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assert_withheld_without_mutation(
                candidate_with_binding(CERTIFIED_BINDING),
                [css_target("B" * 64)],
                canonical_component(style_hash="D" * 64),
                self.make_index(Path(tmp)),
                "CERTIFIED_PILOT_STYLE_SOURCE_HASH_MISMATCH",
            )


if __name__ == "__main__":
    unittest.main()
