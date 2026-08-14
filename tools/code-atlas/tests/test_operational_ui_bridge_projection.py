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

    def test_later_corrective_batch_wins_for_same_component(self):
        stale = resolved_component()
        stale["slotId"] = None
        stale["targetResolutionStatus"] = "PARTIAL"
        current = resolved_component()
        with tempfile.TemporaryDirectory() as tmp:
            governor = Path(tmp) / "prisma-html"
            governor_fixture(governor)
            repo = FakeRepository([])
            repo.batches = [
                {"batchId": "BATCH.test.old", "components": [stale]},
                {"batchId": "BATCH.test.new", "components": [current]},
            ]
            with patch(
                "code_atlas.ui_bridge.projection.resolve_component",
                return_value={"status": "ELIGIBLE_FOR_READ_ONLY_PLAN", "blockingReasons": []},
            ), patch(
                "code_atlas.ui_bridge.projection.build_plan",
                return_value=(
                    {
                        "planId": "BRPLAN.corrective",
                        "status": "PLAN_READY_FOR_REVIEW",
                        "blockingReasons": [],
                        "operations": [{"unitId": "root"}],
                        "applicationEnabled": False,
                    },
                    {"checksum": "ghi", "sourceMutationPerformed": False},
                ),
            ):
                payload, _ = build_projection_map(
                    repo,
                    FakeRecipes(),
                    product_root=str(Path(tmp) / "product"),
                    governor_root=str(governor),
                    surfaces=["pc"],
                )
            self.assertEqual(payload["componentCount"], 1)
            self.assertEqual(payload["components"][0]["trace"]["slotId"], current["slotId"])
            self.assertEqual(payload["authorityPreflightReadyCount"], 1)

    def test_missing_authority_registry_fails_closed_globally(self):
        with tempfile.TemporaryDirectory() as tmp:
            governor = Path(tmp) / "prisma-html"
            governor_fixture(governor)
            (
                governor
                / "authority/rifat/identity/registries/element-bindings.registry.json"
            ).unlink()
            repo = FakeRepository([resolved_component()])
            with patch(
                "code_atlas.ui_bridge.projection.resolve_component",
                return_value={"status": "ELIGIBLE_FOR_READ_ONLY_PLAN", "blockingReasons": []},
            ), patch(
                "code_atlas.ui_bridge.projection.build_plan",
                return_value=(
                    {
                        "planId": "BRPLAN.authority-missing",
                        "status": "PLAN_READY_FOR_REVIEW",
                        "blockingReasons": [],
                        "operations": [{"unitId": "root"}],
                        "applicationEnabled": False,
                    },
                    {"checksum": "jkl", "sourceMutationPerformed": False},
                ),
            ):
                payload, blockers = build_projection_map(
                    repo,
                    FakeRecipes(),
                    product_root=str(Path(tmp) / "product"),
                    governor_root=str(governor),
                    surfaces=["pc"],
                )
            self.assertEqual(payload["status"], "BLOCKED_BY_GLOBAL_AUTHORITY_GAP")
            self.assertIn(
                "AUTHORITY:MISSING_OR_INVALID_ELEMENT_BINDING_REGISTRY",
                payload["globalBlockers"],
            )
            self.assertEqual(blockers["status"], "EXPLICIT_BLOCKERS_PRESENT")

    def test_projection_id_is_machine_path_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            governor_a = base / "machine-a" / "prisma-html"
            governor_b = base / "machine-b" / "nested" / "prisma-html"
            governor_fixture(governor_a)
            governor_fixture(governor_b)
            repo = FakeRepository([resolved_component()])
            plan = (
                {
                    "planId": "BRPLAN.stable",
                    "status": "PLAN_READY_FOR_REVIEW",
                    "blockingReasons": [],
                    "operations": [{"unitId": "root"}],
                    "applicationEnabled": False,
                },
                {"checksum": "mno", "sourceMutationPerformed": False},
            )
            with patch(
                "code_atlas.ui_bridge.projection.resolve_component",
                return_value={"status": "ELIGIBLE_FOR_READ_ONLY_PLAN", "blockingReasons": []},
            ), patch("code_atlas.ui_bridge.projection.build_plan", return_value=plan):
                first, _ = build_projection_map(
                    repo,
                    FakeRecipes(),
                    product_root=str(base / "product-a"),
                    governor_root=str(governor_a),
                    surfaces=["pc"],
                )
                second, _ = build_projection_map(
                    repo,
                    FakeRecipes(),
                    product_root=str(base / "product-b"),
                    governor_root=str(governor_b),
                    surfaces=["pc"],
                )
            self.assertEqual(first["projectionId"], second["projectionId"])
            self.assertEqual(
                first["authority"]["adapterRegistry"]["path"],
                "extras/atlasfin/assets/data/surface-adapter.registry.json",
            )

    def test_surface_blocked_count_includes_non_prefixed_blocked_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            governor = Path(tmp) / "prisma-html"
            governor_fixture(governor)
            repo = FakeRepository([resolved_component()])
            with patch(
                "code_atlas.ui_bridge.projection.resolve_component",
                return_value={"status": "BLOCKED", "blockingReasons": ["SOURCE_DRIFT_OR_MISSING"]},
            ), patch(
                "code_atlas.ui_bridge.projection.build_plan",
                return_value=(
                    {
                        "planId": "BRPLAN.drift",
                        "status": "PLAN_BLOCKED",
                        "blockingReasons": ["SOURCE_DRIFT_OR_MISSING"],
                        "operations": [{"unitId": "root"}],
                        "applicationEnabled": False,
                    },
                    {"checksum": "pqr", "sourceMutationPerformed": False},
                ),
            ):
                payload, _ = build_projection_map(
                    repo,
                    FakeRecipes(),
                    product_root=str(Path(tmp) / "product"),
                    governor_root=str(governor),
                    surfaces=["pc"],
                )
            self.assertEqual(
                payload["components"][0]["status"],
                "SOURCE_RESOLVED_WITH_EXPLICIT_BLOCKERS",
            )
            self.assertEqual(payload["surfaceSummary"]["pc"]["blockedCount"], 1)


if __name__ == "__main__":
    unittest.main()
