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
CANONICAL_UI = "PC-STOCK-MAIN-COMPONENTS-INVENTORY-INVENTORY-WORKSPACE-PRODUCT-FICHA-TAB-01"
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
        "routeId": "ROUTE.pc.stock",
        "ownerFile": SOURCE_OWNER,
        "componentId": "WGT.pc.stock.components_inventory_inventory_workspace.product_ficha",
        "componentUiId": CANONICAL_UI,
        "adapterId": "ADP.PC.ADMIN.V2",
    }


class CertifiedPilotCrosswalkNegativeTests(unittest.TestCase):
    def test_certified_pilot_with_binding_marker_drift_is_withheld(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            contract = (
                root
                / "apps/terminal-de-venta-system/products/pc/app/docs/visual-pilots"
                / "PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.contract.json"
            )
            contract.parent.mkdir(parents=True, exist_ok=True)
            contract.write_text(json.dumps(pilot_payload()), encoding="utf-8")
            index = load_certified_pilot_contracts(root)

            alias, conflict = certified_pilot_alias_for_candidate(
                candidate_with_binding("BND.CONFLICT"),
                [css_target()],
                canonical_component(),
                index,
            )

            self.assertIsNone(alias)
            self.assertIsNotNone(conflict)
            self.assertEqual(conflict["aliasId"], PILOT_UI)
            self.assertEqual(conflict["resolution"], "ALIAS_WITHHELD")
            self.assertIn(
                "CERTIFIED_PILOT_MARKER_MISMATCH:data-prisma-binding",
                conflict["blockingReasons"],
            )
            self.assertNotIn(
                "CERTIFIED_PILOT_CONTRACT_NOT_FOUND",
                conflict["blockingReasons"],
            )


if __name__ == "__main__":
    unittest.main()
