from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from code_atlas.app_map.uimap.contracts import SCHEMA_VERSION, add_integrity
from code_atlas.ui_bridge.binding_promotion import build_binding_promotion_report
from code_atlas.ui_bridge.canonical import file_sha256
from code_atlas.ui_bridge.consistency import audit_visual_authority
from code_atlas.ui_bridge.multisurface import build_multisurface_plan
from code_atlas.ui_bridge.recipes import RecipeRepository
from code_atlas.ui_bridge.repository import BridgeRepository


def component(runtime: str, source_file: str, component_ui_id: str) -> dict:
    runtime_meta = {
        "tb": {
            "surface": "SURF.tb.pos",
            "interface": "IFC.tb.retail.pos_sale",
            "route": "ROUTE.tb.pos",
            "path": "/pos",
            "region": "ZONE.tb.pos.payment",
            "slot": "SLOT.tb.pos.payment.primary",
            "owner": "OWN.tb.pos",
            "adapter": "ADP.TB.TOUCH.V2",
        },
        "pc": {
            "surface": "SURF.pc.admin",
            "interface": "IFC.pc.admin.sales",
            "route": "ROUTE.pc.sales",
            "path": "/sales",
            "region": "ZONE.pc.sales.primary",
            "slot": "SLOT.pc.sales.primary.action",
            "owner": "OWN.pc.sales",
            "adapter": "ADP.PC.ADMIN.V2",
        },
        "mb": {
            "surface": "SURF.mb.owner",
            "interface": "IFC.mb.owner.home",
            "route": "ROUTE.mb.home",
            "path": "/",
            "region": "ZONE.mb.home.primary",
            "slot": "SLOT.mb.home.primary.action",
            "owner": "OWN.mb.home",
            "adapter": "ADP.MB.TOUCH.V2",
        },
    }[runtime]
    component_id = f"WGT.{runtime}.test.primary_action"
    binding = f"BND.TEST.{runtime.upper()}.PRIMARY.V1"
    layer = f"LYR.TEST.{runtime.upper()}.PRIMARY"
    implementation = f"products.{runtime}.test.primary.root"
    return {
        "schema": "prisma.ui.component-record.v1",
        "schemaVersion": SCHEMA_VERSION,
        "runtimeAlias": runtime,
        "surfaceId": runtime_meta["surface"],
        "interfaceId": runtime_meta["interface"],
        "routeId": runtime_meta["route"],
        "routePath": runtime_meta["path"],
        "regionId": runtime_meta["region"],
        "slotId": runtime_meta["slot"],
        "componentId": component_id,
        "componentUiId": component_ui_id,
        "widgetTypeId": "WID.button.primary",
        "neutralMeaningId": "ACT.sale.checkout",
        "relatedNeutralIds": ["ENT.sale"],
        "ownerId": runtime_meta["owner"],
        "ownerFile": source_file,
        "ownerSymbol": "PrimaryAction",
        "renderSourceFile": source_file,
        "renderSymbol": "PrimaryAction",
        "visualTargets": [
            {
                "visualTargetId": f"VTR.{component_ui_id}.ROOT",
                "targetRole": "ROOT",
                "styleSourceFile": source_file,
                "anchorKind": "CSS_SELECTOR",
                "anchorValue": ".root",
                "selector": ".root",
                "pseudoElement": None,
                "stateSelector": "default",
                "atRule": None,
                "implementationLayerId": implementation,
                "sourceHash": "0" * 64,
            }
        ],
        "bindingId": binding,
        "layerId": layer,
        "implementationLayerId": implementation,
        "adapterId": runtime_meta["adapter"],
        "recipeCompatibility": {
            "coverageStatus": "CURRENT_SOURCE_COVERAGE_COMPLETE",
            "compatibleRecipeIds": ["REC.test.primary"],
            "hoverPolicy": "substitute-pressed",
        },
        "stateSupport": {
            "default": "SOURCE_DEFINED",
            "hover": "SOURCE_DEFINED",
            "focus": "SOURCE_DEFINED",
            "focus-visible": "SOURCE_DEFINED",
            "pressed": "SOURCE_DEFINED",
            "disabled": "SOURCE_DEFINED",
            "loading": "SOURCE_DEFINED",
            "reduced-motion": "SOURCE_DEFINED",
            "success": "NOT_APPLICABLE",
            "warning": "NOT_APPLICABLE",
            "error": "NOT_APPLICABLE",
        },
        "evidenceRefs": [
            {"evidenceType": "UNIT_TEST", "sourceFile": "test_ui_bridge_multisurface.py"}
        ],
        "sourceHashes": {source_file: "0" * 64},
        "ndcStatus": "CONFIRMED",
        "confidence": "VERY_HIGH",
        "targetResolutionStatus": "SOURCE_RESOLVED",
        "applicationReadiness": "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT",
        "blockingReasons": [],
        "instancePolicy": "SINGLE_OR_STATIC",
        "projectionOfComponentId": None,
        "legacyIdPreserved": False,
    }


def repository(root: Path, include_mobile: bool = True) -> BridgeRepository:
    specs = [
        ("tb", "products/tb/root.css", "TB-POS-PAY-ACTION-BTN-01"),
        ("pc", "products/pc/root.css", "PC-ADMIN-SALES-ACTION-BTN-01"),
    ]
    if include_mobile:
        specs.append(("mb", "products/mb/root.css", "MB-OWNER-HOME-ACTION-BTN-01"))
    batches = []
    for runtime, rel, ui_id in specs:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(".root{color:red}", encoding="utf-8")
        row = component(runtime, rel, ui_id)
        digest = file_sha256(path).upper()
        row["sourceHashes"] = {rel: digest}
        row["visualTargets"][0]["sourceHash"] = digest
        batch = add_integrity(
            {
                "schema": "prisma.ui.component-batch.v1",
                "schemaVersion": SCHEMA_VERSION,
                "batchId": f"BATCH.{runtime}.multisurfacetest0001",
                "supersedesBatchId": None,
                "contractHash": "A" * 64,
                "runtimeAlias": runtime,
                "sourceSnapshotHash": "F" * 64,
                "components": [row],
                "aliases": [],
                "conflicts": [],
                "coverage": {},
                "integrity": {},
            }
        )
        batches.append(batch)
    return BridgeRepository(batches, [])


def recipes(root: Path) -> RecipeRepository:
    path = root / "recipe.json"
    path.write_text(
        json.dumps(
            {
                "recipeId": "REC.test.primary",
                "compatibleWidgetTypeIds": ["WID.button.primary"],
                "values": {
                    "visualStack": {
                        "units": [
                            {
                                "unitId": "root",
                                "kind": "BASE_SELECTOR",
                                "selector": ".root",
                                "applicationPolicy": "EXPLICIT_REPLACE_VISUAL_PRESERVE_STRUCTURE",
                                "properties": {
                                    "color": {
                                        "mode": "TOKEN",
                                        "value": "color.accentText",
                                    }
                                },
                            }
                        ]
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    return RecipeRepository.load([path])


class MultiSurfacePlanTests(unittest.TestCase):
    def test_exact_neutral_meaning_plans_all_three_surfaces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = repository(root)
            recipe_repo = recipes(root)
            plan, diff = build_multisurface_plan(
                repo,
                recipe_repo,
                str(root),
                source_component="TB-POS-PAY-ACTION-BTN-01",
            )
            self.assertEqual(plan["status"], "PLAN_READY_FOR_REVIEW")
            self.assertEqual(plan["neutralMeaningId"], "ACT.sale.checkout")
            self.assertEqual(
                [row["runtimeAlias"] for row in plan["surfaces"]],
                ["tb", "pc", "mb"],
            )
            self.assertEqual(
                [row["matchCount"] for row in plan["surfaces"]],
                [1, 1, 1],
            )
            self.assertFalse(plan["applicationEnabled"])
            self.assertEqual(diff["status"], "DIFF_READY")
            self.assertEqual(len(diff["targets"]), 3)

    def test_missing_mobile_fails_closed_when_exhaustive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = repository(root, include_mobile=False)
            plan, _ = build_multisurface_plan(
                repo,
                recipes(root),
                str(root),
                neutral_meaning_id="ACT.sale.checkout",
            )
            self.assertEqual(plan["status"], "PLAN_BLOCKED")
            self.assertTrue(
                any(
                    reason.startswith("SURFACE_HAS_NO_EXACT_NEUTRAL_MATCH:mb:")
                    for reason in plan["blockingReasons"]
                )
            )

    def test_binding_promotion_never_fills_missing_coordinates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = repository(root)
            pc = repo.component("PC-ADMIN-SALES-ACTION-BTN-01")
            pc["layerId"] = None
            report, gaps = build_binding_promotion_report(repo)
            self.assertEqual(report["componentCount"], 3)
            self.assertEqual(report["promotableCount"], 2)
            pc_gap = next(
                row
                for row in gaps["rows"]
                if row["componentUiId"] == "PC-ADMIN-SALES-ACTION-BTN-01"
            )
            self.assertIn("MISSING_COORDINATE:layerId", pc_gap["blockingReasons"])
            self.assertIsNone(pc_gap["layerId"])


class VisualAuthorityConsistencyTests(unittest.TestCase):
    def _governor(self, root: Path, stale_contract: bool) -> Path:
        def write(rel: str, value: object) -> None:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(value, str):
                path.write_text(value, encoding="utf-8")
            else:
                path.write_text(json.dumps(value), encoding="utf-8")

        write(
            "authority/rifat/identity/contract/PRISMA_IDENTITY_BINDING_CONTRACT.md",
            (
                "The current Tablet `Cobrar` candidate remains blocked because the compact layer index does not publish an exact `layerId`."
                if stale_contract
                else "Cobrar resolution follows the current element binding registry and must fail closed on drift."
            ),
        )
        write(
            "authority/rifat/identity/registries/element-bindings.registry.json",
            {
                "bindings": [
                    {
                        "bindingId": "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1",
                        "targets": [
                            {
                                "status": "RESOLVED",
                                "layerId": "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE",
                            }
                        ],
                    }
                ]
            },
        )
        write(
            "authority/rifat/identity/registries/bindings.registry.json",
            {
                "bindings": [
                    {
                        "surface": "pc",
                        "readiness": "BLOCKED_BY_MISSING_VISUAL_CONTROL_BINDINGS",
                        "ownerSource": None,
                        "slotSource": None,
                        "layerSource": None,
                        "missing": ["surface-specific-layer-map"],
                    },
                    {
                        "surface": "mobile",
                        "readiness": "BLOCKED_BY_MISSING_VISUAL_CONTROL_BINDINGS",
                        "ownerSource": None,
                        "slotSource": None,
                        "layerSource": None,
                        "missing": ["surface-specific-layer-map"],
                    },
                ]
            },
        )
        write(
            "extras/atlasfin/assets/data/surface-adapter.registry.json",
            {
                "items": [
                    {"id": "ADP.TB.TOUCH.V2"},
                    {"id": "ADP.PC.ADMIN.V2"},
                    {"id": "ADP.MB.TOUCH.V2"},
                ]
            },
        )
        write(
            "extras/atlasfin/assets/data/visual.recipe.registry.json",
            {
                "elements": [
                    {
                        "component_id": "ATL-TEST-01",
                        "semantic_id": "VIS.TEST",
                        "target_bindings": [
                            {
                                "surface_id": "SURF.PC.ADMIN",
                                "status": "BLOCKED_BY_MISSING_ELEMENT_BINDING",
                            },
                            {
                                "surface_id": "SURF.MB.OWNER",
                                "status": "BLOCKED_BY_MISSING_ELEMENT_BINDING",
                            },
                        ],
                    }
                ]
            },
        )
        return root

    def test_stale_cobrar_contract_is_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._governor(Path(tmp), stale_contract=True)
            report = audit_visual_authority(root)
            self.assertEqual(report["status"], "BLOCKED")
            self.assertTrue(
                any(
                    issue["code"] == "STALE_COBRAR_BINDING_CONTRACT"
                    for issue in report["issues"]
                )
            )

    def test_consistent_authority_passes_with_explicit_pc_mobile_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._governor(Path(tmp), stale_contract=False)
            report = audit_visual_authority(root)
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                report["checks"]["pcMobilePendingVisualProjectionBindingCount"],
                2,
            )


if __name__ == "__main__":
    unittest.main()
