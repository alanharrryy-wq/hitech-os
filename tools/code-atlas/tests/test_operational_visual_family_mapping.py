from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from code_atlas.ui_bridge.recipes import RecipeRepository
from code_atlas.ui_bridge.visual_family import (
    build_visual_family_mapping,
    load_visual_family_crosswalk,
)


def component(runtime: str, widget: str, suffix: str, source_hash: str = "A" * 64) -> dict:
    return {
        "runtimeAlias": runtime,
        "surfaceId": f"SURF.{runtime}.test",
        "interfaceId": f"IFC.{runtime}.test",
        "routeId": f"ROUTE.{runtime}.test",
        "routePath": "/test",
        "regionId": f"ZONE.{runtime}.test.primary",
        "slotId": f"SLOT.{runtime}.test.primary.{suffix}",
        "componentId": f"WGT.{runtime}.test.{suffix}",
        "componentUiId": f"{runtime.upper()}-TEST-{suffix.upper()}-01",
        "widgetTypeId": widget,
        "ownerId": f"OWN.{runtime}.test",
        "adapterId": {
            "tb": "ADP.TB.TOUCH.V2",
            "pc": "ADP.PC.ADMIN.V2",
            "mb": "ADP.MB.TOUCH.V2",
        }[runtime],
        "neutralMeaningId": None,
        "sourceHashes": {f"products/{runtime}/test.module.css": source_hash},
        "visualTargets": [
            {
                "visualTargetId": f"VTR.{runtime}.{suffix}.ROOT",
                "targetRole": "ROOT",
                "styleSourceFile": f"products/{runtime}/test.module.css",
                "anchorKind": "CSS_SELECTOR",
                "anchorValue": f".{suffix}",
                "selector": f".{suffix}",
                "pseudoElement": None,
                "stateSelector": "default",
                "atRule": None,
                "sourceHash": source_hash,
            }
        ],
        "evidenceRefs": [],
    }


class VisualFamilyMappingTests(unittest.TestCase):
    def _crosswalk(self, root: Path) -> dict:
        path = root / "crosswalk.json"
        path.write_text(
            json.dumps(
                {
                    "schema": "prisma.visual-family-crosswalk.v1",
                    "version": "1.0.0",
                    "meaningBoundary": {
                        "visualFamilyIdMayPopulateNeutralMeaningId": False
                    },
                    "governedMappings": [
                        {
                            "widgetTypeId": "WID.button",
                            "visualFamilyId": "VISFAM.button.v1",
                            "familyKind": "button",
                            "recipeId": "REC.button.governed.v2",
                            "basis": "TEST_EXPLICIT_AUTHORITY",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return load_visual_family_crosswalk(path)

    def _recipes(self, root: Path) -> RecipeRepository:
        path = root / "recipe.json"
        path.write_text(
            json.dumps(
                {
                    "recipeId": "REC.button.governed.v2",
                    "familyKind": "button",
                    "visualStack": {},
                }
            ),
            encoding="utf-8",
        )
        return RecipeRepository.load([path])

    def test_visual_family_is_separate_from_business_neutral_meaning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            components = {
                "tb": component("tb", "WID.button", "button"),
                "pc": component("pc", "WID.button", "button"),
                "mb": component("mb", "WID.button", "button"),
            }
            repo = SimpleNamespace(components_by_id=components)
            report, control = build_visual_family_mapping(
                repo,
                self._recipes(root),
                self._crosswalk(root),
            )
            self.assertEqual(report["totalVisualCandidateCount"], 3)
            self.assertEqual(report["totalSourceResolvedVisualBindingCount"], 3)
            self.assertEqual(report["totalVisualRecipeProjectionReadyCount"], 3)
            for row in report["rows"]:
                self.assertIsNone(row["neutralMeaningId"])
                self.assertEqual(row["visualFamilyId"], "VISFAM.button.v1")
                self.assertEqual(row["recipeId"], "REC.button.governed.v2")
                self.assertTrue(row["sourceResolvedVisualBinding"])
                self.assertTrue(row["visualRecipeProjectionReady"])
                self.assertTrue(row["visualBindingId"].startswith("BND.VIS."))
                self.assertTrue(row["visualTargets"][0]["visualLayerId"].startswith("LYR.VIS."))
                self.assertTrue(row["visualTargets"][0]["implementationLayerId"].startswith("ILYR.SRC."))
            self.assertEqual(set(control["surfaces"]), {"tb", "pc", "mb"})
            self.assertEqual(control["surfaces"]["pc"]["counts"]["layers"], 1)

    def test_unmapped_family_does_not_block_exact_physical_visual_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = SimpleNamespace(
                components_by_id={"control": component("pc", "WID.control", "control")}
            )
            report, _ = build_visual_family_mapping(
                repo,
                self._recipes(root),
                self._crosswalk(root),
            )
            row = report["rows"][0]
            self.assertTrue(row["sourceResolvedVisualBinding"])
            self.assertFalse(row["visualRecipeProjectionReady"])
            self.assertEqual(row["familyStatus"], "BLOCKED_BY_UNMAPPED_VISUAL_FAMILY")
            self.assertIsNone(row["neutralMeaningId"])

    def test_source_hash_drift_fails_visual_binding_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            row = component("pc", "WID.button", "button", "A" * 64)
            row["visualTargets"][0]["sourceHash"] = "B" * 64
            repo = SimpleNamespace(components_by_id={"pc": row})
            report, control = build_visual_family_mapping(
                repo,
                self._recipes(root),
                self._crosswalk(root),
            )
            mapped = report["rows"][0]
            self.assertFalse(mapped["sourceResolvedVisualBinding"])
            self.assertIn("VISUAL_TARGET_SOURCE_HASH_DRIFT:0", mapped["blockingReasons"])
            self.assertEqual(control["surfaces"], {})

    def test_generated_ids_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = SimpleNamespace(
                components_by_id={"tb": component("tb", "WID.button", "button")}
            )
            recipes = self._recipes(root)
            crosswalk = self._crosswalk(root)
            first, _ = build_visual_family_mapping(repo, recipes, crosswalk)
            second, _ = build_visual_family_mapping(repo, recipes, crosswalk)
            self.assertEqual(
                first["rows"][0]["visualBindingId"],
                second["rows"][0]["visualBindingId"],
            )
            self.assertEqual(
                first["rows"][0]["visualTargets"][0]["visualLayerId"],
                second["rows"][0]["visualTargets"][0]["visualLayerId"],
            )


if __name__ == "__main__":
    unittest.main()
