from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from code_atlas.ui_bridge.projection import build_projection_map


class FakeRepository:
    def __init__(self, components):
        self.batches = [{"batchId": "BATCH.test.01", "components": components}]


class FakeRecipes:
    def compatible(self, component):
        return [{"recipeId": "REC.button.primary"}]


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def governor_fixture(root: Path) -> None:
    write_json(
        root / "extras/atlasfin/assets/data/surface-adapter.registry.json",
        {
            "schema": "PRISMA_SURFACE_ADAPTER_REGISTRY_V2",
            "version": "2.0.0",
            "items": [
                {"id": "ADP.TB.TOUCH.V2"},
                {"id": "ADP.PC.ADMIN.V2"},
                {"id": "ADP.MB.TOUCH.V2"},
            ],
        },
    )
    write_json(
        root / "authority/rifat/identity/registries/bindings.registry.json",
        {
            "schema": "prisma.identity.bindings.registry.v1",
            "version": "1.0.0",
            "bindings": [
                {"surface": "tablet", "readiness": "CERTIFIED_BINDING_SOURCE", "missing": []},
                {"surface": "pc", "readiness": "BLOCKED_BY_MISSING_VISUAL_CONTROL_BINDINGS", "missing": ["layer"]},
                {"surface": "mobile", "readiness": "BLOCKED_BY_MISSING_VISUAL_CONTROL_BINDINGS", "missing": ["layer"]},
            ],
        },
    )
    write_json(
        root / "authority/rifat/identity/registries/element-bindings.registry.json",
        {
            "schema": "prisma.identity.element-bindings.registry.v1",
            "version": "1.1.0",
            "status": "SOURCE_READY_ONE_RESOLVED_BINDING",
            "instructionOnly": True,
            "runtimeMutationAllowed": False,
            "productApplicationAllowed": False,
            "bindings": [{"status": "RESOLVED"}],
        },
    )
    write_json(
        root / "extras/atlasfin/assets/data/visual.recipe.registry.json",
        {
            "bundle": {"version": "3.0.0"},
            "capabilities": {"directProductMutation": False},
            "elements": [
                {
                    "target_bindings": [
                        {"surface_id": "SURF.TB.POS", "status": "BLOCKED_BY_MISSING_ELEMENT_BINDING"}
                    ]
                }
            ],
        },
    )


def resolved_component():
    return {
        "runtimeAlias": "pc",
        "surfaceId": "SURF.pc.backoffice",
        "interfaceId": "IFC.pc.stock",
        "routeId": "ROUTE.pc.stock",
        "routePath": "/stock",
        "regionId": "ZONE.pc.stock.detail",
        "slotId": "SLOT.pc.stock.detail.primary",
        "componentId": "WGT.pc.stock.ficha",
        "componentUiId": "PC-STOCK-FICHA-PANEL-01",
        "ownerId": "OWN.pc.inventory.stock_ficha",
        "ownerFile": "products/pc/app/components/inventory/inventory-workspace.tsx",
        "ownerSymbol": "StockFicha",
        "renderSourceFile": "products/pc/app/components/inventory/inventory-workspace.tsx",
        "renderSymbol": "StockFicha",
        "bindingId": "BND.SURFACE.OPERATIONAL.PC.STOCK.FICHA.V1",
        "layerId": "LYR.SURFACE.OPERATIONAL.DETAIL",
        "implementationLayerId": "products.pc.app.components.inventory.productficha",
        "adapterId": "ADP.PC.ADMIN.V2",
        "neutralMeaningId": "VIS.surface.operational.detail",
        "relatedNeutralIds": [],
        "ndcStatus": "CONFIRMED",
        "confidence": "VERY_HIGH",
        "targetResolutionStatus": "SOURCE_RESOLVED",
        "applicationReadiness": "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT",
        "blockingReasons": [],
        "sourceHashes": {"ownerFile": "A" * 64},
        "visualTargets": [{"visualTargetId": "VT.pc.stock.ficha"}],
        "recipeCompatibility": {"recipeIds": ["REC.button.primary"]},
    }


class ProjectionMapTests(unittest.TestCase):
    def test_ready_component_is_promoted_to_exact_target_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            governor = Path(tmp) / "prisma-html"
            governor_fixture(governor)
            repo = FakeRepository([resolved_component()])
            with patch(
                "code_atlas.ui_bridge.projection.resolve_component",
                return_value={"status": "ELIGIBLE_FOR_READ_ONLY_PLAN", "blockingReasons": []},
            ), patch(
                "code_atlas.ui_bridge.projection.build_plan",
                return_value=(
                    {
                        "planId": "BRPLAN.test",
                        "status": "PLAN_READY_FOR_REVIEW",
                        "blockingReasons": [],
                        "operations": [{"unitId": "root"}],
                        "applicationEnabled": False,
                    },
                    {"checksum": "abc", "sourceMutationPerformed": False},
                ),
            ):
                payload, blockers = build_projection_map(
                    repo,
                    FakeRecipes(),
                    product_root=str(Path(tmp) / "product"),
                    governor_root=str(governor),
                    surfaces=["pc"],
                )
            self.assertEqual(payload["status"], "SOURCE_READY")
            self.assertEqual(payload["authorityPreflightReadyCount"], 1)
            self.assertFalse(payload["applicationEnabled"])
            self.assertEqual(payload["components"][0]["status"], "READY_FOR_EXACT_TARGET_AUTHORITY_PREFLIGHT")
            self.assertEqual(blockers["status"], "PASS_NO_BLOCKERS")

    def test_missing_trace_remains_explicitly_blocked(self):
        component = resolved_component()
        component["slotId"] = None
        component["targetResolutionStatus"] = "PARTIAL"
        component["applicationReadiness"] = "BLOCKED"
        with tempfile.TemporaryDirectory() as tmp:
            governor = Path(tmp) / "prisma-html"
            governor_fixture(governor)
            repo = FakeRepository([component])
            with patch(
                "code_atlas.ui_bridge.projection.resolve_component",
                return_value={"status": "BLOCKED", "blockingReasons": ["TARGET_NOT_SOURCE_RESOLVED"]},
            ), patch(
                "code_atlas.ui_bridge.projection.build_plan",
                return_value=(
                    {
                        "planId": "BRPLAN.blocked",
                        "status": "PLAN_BLOCKED",
                        "blockingReasons": ["TARGET_NOT_SOURCE_RESOLVED"],
                        "operations": [],
                        "applicationEnabled": False,
                    },
                    {"checksum": "def", "sourceMutationPerformed": False},
                ),
            ):
                payload, blockers = build_projection_map(
                    repo,
                    FakeRecipes(),
                    product_root=str(Path(tmp) / "product"),
                    governor_root=str(governor),
                    surfaces=["pc"],
                )
            self.assertEqual(payload["authorityPreflightReadyCount"], 0)
            self.assertEqual(payload["components"][0]["status"], "BLOCKED_BY_INCOMPLETE_EXACT_MAPPING")
            self.assertIn("MISSING_TRACE:slotId", payload["components"][0]["blockingReasons"])
            self.assertEqual(blockers["status"], "EXPLICIT_BLOCKERS_PRESENT")


if __name__ == "__main__":
    unittest.main()
