from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

from code_atlas.app_map.uimap.governed_markers import (
    certified_pilot_alias_for_candidate,
    load_certified_pilot_contracts,
)

SOURCE_OWNER = "apps/terminal-de-venta-system/products/pc/app/components/inventory/inventory-workspace.tsx"
CSS_OWNER = "apps/terminal-de-venta-system/products/pc/app/components/inventory/pc-inventory-master-detail.module.css"
PILOT_UI = "PC-STOCK-FICHA-PANEL-01"
CANONICAL_UI = "PC-STOCK-MAIN-COMPONENTS-INVENTORY-INVENTORY-WORKSPACE-PRODUCT-FICHA-TAB-01"


def contract_payload() -> dict:
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
            "bindingId": "BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1",
            "adapterId": "ADP.PC.DENSE.CLOUDGLASS.V1",
            "neutralLayerId": "LYR.SURFACE.OPERATIONAL.DETAIL",
            "implementationLayerId": "products.pc.app.components.inventory.pc.inventory.master.detail.module.css.productficha",
            "runtimeSelector": "[data-pcinv-product-ficha=\"stock\"]",
            "sourceOwner": SOURCE_OWNER,
            "cssOwner": CSS_OWNER,
        },
    }


def candidate() -> SimpleNamespace:
    return SimpleNamespace(
        runtime_alias="pc",
        route_path="/stock",
        route_id="ROUTE.pc.stock",
        render_source_file=SOURCE_OWNER,
        owner_file=SOURCE_OWNER,
        source_hash="A" * 64,
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
            "data-prisma-binding": "BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1",
            "data-prisma-adapter": "ADP.PC.DENSE.CLOUDGLASS.V1",
            "data-prisma-neutral-layer": "LYR.SURFACE.OPERATIONAL.DETAIL",
            "data-prisma-source-owner": "inventory-workspace.tsx",
            "data-prisma-css-owner": "pc-inventory-master-detail.module.css",
        },
    )


def style_target(source_hash: str = "B" * 64) -> SimpleNamespace:
    return SimpleNamespace(
        source_file=CSS_OWNER,
        source_hash=source_hash,
        selector=".productFicha",
    )


def canonical(render_hash: str = "A" * 64, style_hash: str = "B" * 64) -> dict:
    return {
        "runtimeAlias": "pc",
        "routeId": "ROUTE.pc.stock",
        "ownerFile": SOURCE_OWNER,
        "componentId": "WGT.pc.stock.components_inventory_inventory_workspace.product_ficha",
        "componentUiId": CANONICAL_UI,
        "sourceHashes": {
            "ownerFile": render_hash,
            "renderSourceFile": render_hash,
            CSS_OWNER: style_hash,
        },
    }


class CertifiedPilotHashGateTests(unittest.TestCase):
    def make_index(self, root: Path) -> dict:
        path = (
            root
            / "apps/terminal-de-venta-system/products/pc/app/docs/visual-pilots"
            / "PC_STOCK_FICHA_TABLET_LICENSES_VISUAL_PILOT_V1.contract.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(contract_payload()), encoding="utf-8")
        return load_certified_pilot_contracts(root)

    def run_case(self, root: Path, component: dict, target: SimpleNamespace):
        before = deepcopy(component)
        alias, conflict = certified_pilot_alias_for_candidate(
            candidate(), [target], component, self.make_index(root)
        )
        self.assertEqual(component, before)
        return alias, conflict

    def test_real_uimap_provenance_slots_allow_exact_alias_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            alias, conflict = self.run_case(Path(tmp), canonical(), style_target())
            self.assertIsNone(conflict)
            self.assertEqual(alias["aliasId"], PILOT_UI)
            self.assertEqual(alias["canonicalComponentUiId"], CANONICAL_UI)
            self.assertEqual(alias["reason"], "CERTIFIED_VISUAL_PILOT_CROSSWALK")

    def test_render_hash_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            alias, conflict = self.run_case(
                Path(tmp), canonical(render_hash="C" * 64), style_target()
            )
            self.assertIsNone(alias)
            self.assertIn(
                "CERTIFIED_PILOT_RENDER_SOURCE_HASH_MISMATCH",
                conflict["blockingReasons"],
            )

    def test_style_hash_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            alias, conflict = self.run_case(
                Path(tmp), canonical(style_hash="D" * 64), style_target()
            )
            self.assertIsNone(alias)
            self.assertIn(
                "CERTIFIED_PILOT_STYLE_SOURCE_HASH_MISMATCH",
                conflict["blockingReasons"],
            )


if __name__ == "__main__":
    unittest.main()
