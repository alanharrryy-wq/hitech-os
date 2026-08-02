from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

from .contracts import (
    ADAPTERS,
    SCHEMA_VERSION,
    record_schema,
    slug,
    stable_id,
    validate_record,
    validate_schema_subset,
)
from .discovery import (
    CssTarget,
    UiCandidate,
    extract_ui_candidates_from_file,
    make_state_support,
    parallel_hash,
    route_path_from_file,
)
from .runner import (
    GOLDEN_BINDING_ID,
    GOLDEN_IMPLEMENTATION_LAYER_ID,
    GOLDEN_LAYER_ID,
    aliases_have_cycle,
    coverage_for,
    deduplicate_records,
    record_from_candidate,
    run_uimap,
    selector_authority,
    validate_alias_targets,
    validate_outputs,
    visual_target_rows,
)

FIXED_TIME = "2026-07-26T18:00:00Z"


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def fixture_tree(root: Path) -> tuple[Path, Path, Path]:
    product = root / "product"
    governor = root / "governor"
    route = product / "apps/terminal-de-venta-system/products/tablet/app/app/pos/page.tsx"
    component = product / "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos-ticket-panel.tsx"
    css = product / "apps/terminal-de-venta-system/products/tablet/app/components/pos/pos.module.css"
    write(route, 'import { PosTicketPanel } from "../../components/pos/pos-ticket-panel"; export default function Page(){return <PosTicketPanel/>;}')
    write(component, '''
import styles from "./pos.module.css";
export function PosTicketPanel(){
  return <button className={styles.cobrarReferenceButton} data-prisma-state="default"><span className={styles.cobrarCopy}>Cobrar</span></button>;
}
''')
    write(css, '''
.cobrarReferenceButton { position: relative; display: grid; background: #123; }
.cobrarReferenceButton:hover { filter: brightness(1.1); }
.cobrarReferenceButton:disabled { opacity: .5; }
.cobrarReferenceButton::before { content: ""; }
.cobrarCopy { display: grid; }
''')
    certification = {
        "certifications": [{
            "bindingId": GOLDEN_BINDING_ID,
            "layerId": GOLDEN_LAYER_ID,
            "expectedImplementationLayerId": GOLDEN_IMPLEMENTATION_LAYER_ID,
            "selector": ".cobrarReferenceButton",
        }]
    }
    write(governor / "authority/rifat/identity/bindings/cobrar.binding.json", json.dumps(certification))
    full_stack = {
        "trace": {
            "surfaceId": "tablet",
            "ownerId": "products.tablet.app.components.pos.pos.ticket.panel.tsx",
            "routeId": "tablet.pos.route",
            "regionId": "products.tablet.app.components.pos.pos.ticket.panel.tsx.pos.buttons",
            "slotId": "tablet.any.products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton.layer",
            "componentUiId": "products.tablet.app.components.pos.pos.ticket.panel.tsx",
            "layerId": GOLDEN_LAYER_ID,
            "implementationLayerId": GOLDEN_IMPLEMENTATION_LAYER_ID,
            "selector": ".cobrarReferenceButton",
        },
        "bindingRequirements": {
            "bindingId": GOLDEN_BINDING_ID,
            "layerIdRequired": GOLDEN_LAYER_ID,
            "implementationLayerIdRequired": GOLDEN_IMPLEMENTATION_LAYER_ID,
        },
    }
    evidence = root / "golden.json"
    write(evidence, json.dumps(full_stack))
    return product, governor, evidence


def minimal_record(component_ui_id: str, component_id: str, owner_file: str) -> dict:
    support = {state: "NOT_EVALUATED" for state in (
        "default", "hover", "focus", "focus-visible", "pressed", "disabled", "loading", "reduced-motion",
        "success", "warning", "error",
    )}
    support["default"] = "SOURCE_DEFINED"
    return {
        "schema": "prisma.ui.component-record.v1",
        "schemaVersion": SCHEMA_VERSION,
        "runtimeAlias": "pc",
        "surfaceId": "SURF.pc.home",
        "interfaceId": "IFC.pc.home.interface",
        "routeId": "ROUTE.pc.home",
        "routePath": "/",
        "regionId": "ZONE.pc.home.main",
        "slotId": f"SLOT.pc.home.main.{component_id.split('.')[-1]}",
        "componentId": component_id,
        "componentUiId": component_ui_id,
        "widgetTypeId": "WID.button",
        "neutralMeaningId": None,
        "relatedNeutralIds": [],
        "ownerId": "OWN.pc.owner",
        "ownerFile": owner_file,
        "ownerSymbol": "Owner",
        "renderSourceFile": owner_file,
        "renderSymbol": "Owner",
        "visualTargets": [],
        "bindingId": None,
        "layerId": None,
        "implementationLayerId": None,
        "adapterId": ADAPTERS["pc"],
        "recipeCompatibility": {"coverageStatus": "NOT_EVALUATED", "compatibleRecipeIds": [], "hoverPolicy": "native-hover"},
        "stateSupport": support,
        "evidenceRefs": [{"evidenceType": "RENDER_SOURCE", "sourceFile": owner_file, "sourceHash": "A" * 64}],
        "sourceHashes": {"ownerFile": "A" * 64},
        "ndcStatus": "CANDIDATE",
        "confidence": "LOW",
        "targetResolutionStatus": "PARTIAL",
        "applicationReadiness": "BLOCKED",
        "blockingReasons": ["TEST"],
        "instancePolicy": "SINGLE_OR_STATIC",
        "projectionOfComponentId": None,
        "legacyIdPreserved": False,
    }


class UimapTests(unittest.TestCase):
    def test_01_golden_fixture_cobrar(self):
        with tempfile.TemporaryDirectory() as temp:
            product, governor, evidence = fixture_tree(Path(temp))
            out = Path(temp) / "out"
            result = run_uimap(str(product), str(governor), str(out), str(evidence), run_timestamp=FIXED_TIME)
            self.assertTrue(result["ok"], result["validation"])
            atlas = json.loads((out / "atlas/PRISMA_UI_COMPONENT_ATLAS.json").read_text(encoding="utf-8"))
            golden = [r for r in atlas["components"] if r.get("bindingId") == GOLDEN_BINDING_ID]
            self.assertEqual(len(golden), 1)
            self.assertEqual(golden[0]["layerId"], GOLDEN_LAYER_ID)
            self.assertEqual(golden[0]["implementationLayerId"], GOLDEN_IMPLEMENTATION_LAYER_ID)
            self.assertEqual(golden[0]["recipeCompatibility"]["coverageStatus"], "CURRENT_SOURCE_COVERAGE_COMPLETE")
            self.assertEqual(golden[0]["routePath"], "/pos")
            self.assertEqual(golden[0]["routeId"], "ROUTE.tb.pos")
            self.assertEqual(golden[0]["componentUiId"], "TB-POS-PAY-COBRAR-BTN-01")
            self.assertEqual(golden[0]["widgetTypeId"], "WID.button")
            self.assertEqual(golden[0]["surfaceId"], "SURF.tb.pos")
            aliases = json.loads((out / "atlas/PRISMA_UI_ALIAS_REGISTRY.json").read_text(encoding="utf-8"))
            legacy = [row for row in aliases["aliases"] if row.get("reason") == "CERTIFIED_LEGACY_ID_PRESERVED"]
            self.assertEqual(len(legacy), 6)

    def test_02_collision_ids_blocked_without_ordinal_rewrite(self):
        a = minimal_record("PC-HOME-MAIN-X-BTN-01", "WGT.pc.home.x", "a.tsx")
        b = minimal_record("PC-HOME-MAIN-X-BTN-01", "WGT.pc.home.y", "b.tsx")
        records, _, conflicts = deduplicate_records([a, b])
        self.assertTrue(conflicts)
        self.assertTrue(all(r["targetResolutionStatus"] == "BLOCKED_BY_CONFLICT" for r in records))
        self.assertEqual({r["componentUiId"] for r in records}, {"PC-HOME-MAIN-X-BTN-01"})
        self.assertFalse(any("projection_" in r["componentId"] for r in records))
        self.assertTrue(all(
            row["resolution"] == "UNRESOLVED_REQUIRES_ROUTE_OR_OWNER_REPAIR"
            for row in conflicts
        ))

    def test_03_legacy_alias_registry(self):
        a = minimal_record("PC-HOME-MAIN-X-BTN-01", "WGT.pc.home.x", "a.tsx")
        b = json.loads(json.dumps(a))
        b["componentUiId"] = "legacy.component.path.tsx"
        records, aliases, _ = deduplicate_records([a, b])
        self.assertEqual(len(records), 1)
        self.assertEqual(len(aliases), 1)

    def test_04_alias_circular_blocked(self):
        aliases = [
            {"aliasId": "A", "canonicalComponentUiId": "B"},
            {"aliasId": "B", "canonicalComponentUiId": "A"},
        ]
        self.assertTrue(aliases_have_cycle(aliases))

    def test_05_shared_ui_multiple_projections(self):
        source = minimal_record("SHARED-UI-MAIN-BUTTON-BTN-01", "WGT.shared.ui.button", "packages/ui/button.tsx")
        projection = minimal_record("PC-HOME-MAIN-BUTTON-BTN-01", "WGT.pc.home.button", "apps/pc/page.tsx")
        projection["projectionOfComponentId"] = source["componentId"]
        self.assertEqual(projection["projectionOfComponentId"], "WGT.shared.ui.button")
        self.assertFalse(validate_record(projection))

    def test_06_generated_projection_do_not_patch(self):
        target = CssTarget("x", ".x", "generated/x.css", "A" * 64, None, "default", None, "CSS_SELECTOR", "ROOT")
        rows = visual_target_rows([target], "impl.x", True)
        self.assertEqual(rows[0]["anchorKind"], "GENERATED_PROJECTION")
        self.assertEqual(rows[0]["patchPolicy"], "DO_NOT_PATCH_GENERATED")

    def test_07_multiple_owner_blocked(self):
        candidate = UiCandidate(
            runtime_alias="pc", route_path="/", route_id="ROUTE.pc.home", route_source_file="app/page.tsx",
            render_source_file="components/x.tsx", render_symbol="X", owner_file="components/x.tsx", owner_symbol="X",
            class_name="xButton", tag_name="button", widget_kind="button", text_hint="X", instance_policy="SINGLE_OR_STATIC",
            data_attributes={}, source_hash="A" * 64, multiple_owner_candidates=["a.tsx", "b.tsx"],
        )
        record = record_from_candidate(candidate, [], {}, 1, {}, [])
        self.assertEqual(record["targetResolutionStatus"], "BLOCKED_BY_CONFLICT")
        self.assertIn("MULTIPLE_OWNER_CANDIDATES", record["blockingReasons"])

    def test_08_repeated_by_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "list.tsx"
            write(source, 'export function List(){return items.map((item)=><button className="rowButton">{item.name}</button>)}')
            hashes = parallel_hash([source])
            rows = extract_ui_candidates_from_file("pc", source, root, [], hashes[source])
            self.assertTrue(any(row.instance_policy == "REPEATED_BY_DATA" for row in rows))

    def test_09_touch_hover_substitute_pressed(self):
        target = CssTarget("x", ".x:active", "x.css", "A" * 64, None, "pressed", None, "CSS_SELECTOR", "CONTROL")
        support = make_state_support([target], "tb")
        self.assertEqual(support["hover"], "NOT_APPLICABLE")
        self.assertEqual(support["pressed"], "SOURCE_DEFINED")

    def test_10_recipe_coverage_distinction(self):
        with tempfile.TemporaryDirectory() as temp:
            product, governor, evidence = fixture_tree(Path(temp))
            out = Path(temp) / "out"
            run_uimap(str(product), str(governor), str(out), str(evidence), run_timestamp=FIXED_TIME)
            atlas = json.loads((out / "atlas/PRISMA_UI_COMPONENT_ATLAS.json").read_text(encoding="utf-8"))
            golden = next(r for r in atlas["components"] if r.get("bindingId") == GOLDEN_BINDING_ID)
            self.assertNotEqual(golden["recipeCompatibility"]["coverageStatus"], "FULL_VISUAL_STATE_RECIPE_COMPLETE")

    def test_11_source_drift_gate(self):
        validation = validate_outputs([], [], [], "A", "B", "C", "C")
        self.assertFalse(validation["ok"])
        self.assertIn("product_source_mutated", validation["errors"])

    def test_12_corrupt_zip_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "bad.zip"
            path.write_bytes(b"not a zip")
            with self.assertRaises(zipfile.BadZipFile):
                with zipfile.ZipFile(path) as archive:
                    archive.testzip()

    def test_13_rerun_deterministic(self):
        with tempfile.TemporaryDirectory() as temp:
            product, governor, evidence = fixture_tree(Path(temp))
            out1, out2 = Path(temp) / "out1", Path(temp) / "out2"
            r1 = run_uimap(str(product), str(governor), str(out1), str(evidence), run_timestamp=FIXED_TIME)
            r2 = run_uimap(str(product), str(governor), str(out2), str(evidence), run_timestamp=FIXED_TIME)
            self.assertEqual(r1["canonicalAtlasChecksum"], r2["canonicalAtlasChecksum"])

    def test_14_idempotent_same_output(self):
        with tempfile.TemporaryDirectory() as temp:
            product, governor, evidence = fixture_tree(Path(temp))
            out = Path(temp) / "out"
            r1 = run_uimap(str(product), str(governor), str(out), str(evidence), run_timestamp=FIXED_TIME)
            r2 = run_uimap(str(product), str(governor), str(out), str(evidence), run_timestamp=FIXED_TIME)
            self.assertEqual(r1["canonicalAtlasChecksum"], r2["canonicalAtlasChecksum"])

    def test_15_product_byte_for_byte_intact(self):
        with tempfile.TemporaryDirectory() as temp:
            product, governor, evidence = fixture_tree(Path(temp))
            before = {p.relative_to(product).as_posix(): p.read_bytes() for p in product.rglob("*") if p.is_file()}
            out = Path(temp) / "out"
            result = run_uimap(str(product), str(governor), str(out), str(evidence), run_timestamp=FIXED_TIME)
            after = {p.relative_to(product).as_posix(): p.read_bytes() for p in product.rglob("*") if p.is_file()}
            self.assertTrue(result["validation"]["gates"]["productByteForByteIntact"])
            self.assertEqual(before, after)



    def test_16_strict_schema_rejects_legacy_component_id(self):
        record = minimal_record("PC-HOME-MAIN-X-BTN-01", "WGT.pc.home.x", "a.tsx")
        record["componentUiId"] = "legacy.component.path.tsx"
        errors = validate_schema_subset(record, record_schema())
        self.assertTrue(any(error.endswith(":pattern") for error in errors))

    def test_17_zero_denominator_is_not_evaluated(self):
        metrics = coverage_for([], [])
        self.assertEqual(metrics["routeCoverage"], "NOT_EVALUATED")
        self.assertEqual(metrics["identificationCoverage"], "NOT_EVALUATED")

    def test_18_previous_batch_is_superseded_and_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            product, governor, evidence = fixture_tree(root)
            prior = root / "prior"
            prior.mkdir()
            write(
                prior / "01_tb.json",
                json.dumps({
                    "schema": "prisma.ui.component-batch.v1",
                    "schemaVersion": "1.0.0",
                    "batchId": "BATCH.tb.legacy0000000000",
                    "supersedesBatchId": None,
                    "contractHash": "A" * 64,
                    "runtimeAlias": "tb",
                    "sourceSnapshotHash": "B" * 64,
                    "components": [],
                    "aliases": [],
                    "conflicts": [],
                    "coverage": {},
                    "integrity": {},
                }),
            )
            out = root / "out"
            result = run_uimap(
                str(product),
                str(governor),
                str(out),
                str(evidence),
                run_timestamp=FIXED_TIME,
                previous_batches_source=str(prior),
            )
            self.assertTrue(result["ok"], result["validation"])
            batch = json.loads((out / "batches/01_tb.json").read_text(encoding="utf-8"))
            self.assertEqual(batch["supersedesBatchId"], "BATCH.tb.legacy0000000000")
            self.assertTrue((out / "batches/history/BATCH.tb.legacy0000000000.json").is_file())

    def test_19_source_resolved_rejects_noncanonical_identity(self):
        record = minimal_record("PC-HOME-MAIN-X-BTN-01", "WGT.pc.home.x", "a.tsx")
        record.update({
            "surfaceId": "pc",
            "bindingId": "BND.ACT.PRIMARY.PC.HOME.X.V1",
            "layerId": "LYR.ACT.PRIMARY.PC.HOME.X.BASE",
            "implementationLayerId": "apps.pc.x",
            "visualTargets": [{
                "visualTargetId": "VTR.PC-HOME-MAIN-X-BTN-01.CONTROL.01",
                "targetRole": "CONTROL",
                "styleSourceFile": "x.css",
                "anchorKind": "CSS_SELECTOR",
                "anchorValue": "x",
                "selector": ".x",
                "pseudoElement": None,
                "stateSelector": "default",
                "atRule": None,
                "implementationLayerId": "apps.pc.x",
                "sourceHash": "A" * 64,
            }],
            "neutralMeaningId": "ACT.sale.checkout",
            "ndcStatus": "CONFIRMED",
            "confidence": "HIGH",
            "targetResolutionStatus": "SOURCE_RESOLVED",
            "applicationReadiness": "ELIGIBLE_FOR_AUTHORITY_PREFLIGHT",
            "blockingReasons": [],
        })
        errors = validate_record(record)
        self.assertIn("invalid_id_grammar:surfaceId", errors)
        self.assertIn("source_resolved_identity_contract_invalid", errors)

    def test_20_physical_layer_id_is_not_emitted_as_neutral_layer_id(self):
        physical = "products.chart.lab.app.app.globals.css.canvas.toolbar"
        authority = {
            "layersBySelector": {
                ".canvasToolbar": [{
                    "selector": ".canvasToolbar",
                    "layerId": physical,
                    "implementationLayerId": None,
                    "sourceFile": "layers.json",
                    "sourceHash": "A" * 64,
                }]
            },
            "bindingsBySelector": {},
        }
        resolved, blockers = selector_authority(authority, ".canvasToolbar")
        self.assertEqual(blockers, [])
        self.assertIsNotNone(resolved)
        self.assertIsNone(resolved["layerId"])
        self.assertEqual(resolved["implementationLayerId"], physical)
        self.assertEqual(
            resolved["normalization"]["physicalLayerIdsReclassified"],
            [physical],
        )

    def test_21_same_owner_dedupe_groups_keep_precise_alias_targets(self):
        owner = "components/shared-owner.tsx"
        alpha = minimal_record("PC-HOME-MAIN-ALPHA-BTN-01", "WGT.pc.home.alpha", owner)
        alpha_alias = json.loads(json.dumps(alpha))
        alpha_alias["componentUiId"] = "PC-HOME-MAIN-ALPHA-BTN-02"
        beta = minimal_record("PC-HOME-MAIN-BETA-BTN-01", "WGT.pc.home.beta", owner)
        beta_alias = json.loads(json.dumps(beta))
        beta_alias["componentUiId"] = "PC-HOME-MAIN-BETA-BTN-02"

        records, aliases, conflicts = deduplicate_records([
            alpha,
            alpha_alias,
            beta,
            beta_alias,
        ])
        self.assertFalse(conflicts)
        self.assertEqual(len(records), 2)
        targets = {row["aliasId"]: row["canonicalComponentUiId"] for row in aliases}
        self.assertEqual(
            targets["PC-HOME-MAIN-ALPHA-BTN-02"],
            "PC-HOME-MAIN-ALPHA-BTN-01",
        )
        self.assertEqual(
            targets["PC-HOME-MAIN-BETA-BTN-02"],
            "PC-HOME-MAIN-BETA-BTN-01",
        )
        self.assertEqual(validate_alias_targets(records, aliases), [])

    def test_22_golden_owner_is_not_an_alias_sink(self):
        owner = "products/tablet/app/components/pos/pos-ticket-panel.tsx"
        golden = minimal_record(
            "TB-POS-PAY-COBRAR-BTN-01",
            "WGT.tb.pos.cobrar",
            owner,
        )
        unrelated = minimal_record(
            "TB-HOME-MAIN-TICKET-PANEL-PNL-01",
            "WGT.tb.home.ticket_panel",
            owner,
        )
        unrelated_alias = json.loads(json.dumps(unrelated))
        unrelated_alias["componentUiId"] = "TB-HOME-MAIN-TICKET-PANEL-PNL-02"

        records, aliases, conflicts = deduplicate_records([
            golden,
            unrelated,
            unrelated_alias,
        ])
        self.assertFalse(conflicts)
        alias = next(
            row for row in aliases
            if row["aliasId"] == "TB-HOME-MAIN-TICKET-PANEL-PNL-02"
        )
        self.assertEqual(
            alias["canonicalComponentUiId"],
            "TB-HOME-MAIN-TICKET-PANEL-PNL-01",
        )
        self.assertNotEqual(alias["canonicalComponentUiId"], golden["componentUiId"])
        self.assertEqual(validate_alias_targets(records, aliases), [])

    def test_23_alias_provenance_mismatch_is_blocked(self):
        canonical = minimal_record(
            "PC-HOME-MAIN-BETA-BTN-01",
            "WGT.pc.home.beta",
            "components/beta.tsx",
        )
        aliases = [{
            "aliasId": "PC-HOME-MAIN-BETA-BTN-02",
            "canonicalComponentUiId": canonical["componentUiId"],
            "canonicalComponentId": "WGT.pc.home.wrong",
            "canonicalOwnerFile": "components/wrong.tsx",
            "dedupeKeyHash": "A" * 64,
            "reason": "SAME_OWNER_PROJECTION_DEDUPLICATED",
            "status": "INTERNAL",
        }]
        errors = validate_alias_targets([canonical], aliases)
        self.assertTrue(any(error.startswith("alias_owner_provenance_mismatch:") for error in errors))
        self.assertTrue(any(error.startswith("alias_component_provenance_mismatch:") for error in errors))

    def test_24_next_route_boundaries_are_route_entrypoints(self):
        root = Path("products/pc/app")
        self.assertEqual(
            route_path_from_file(root, root / "app/audit/error.tsx"),
            ("/audit", "error_boundary"),
        )
        self.assertEqual(
            route_path_from_file(root, root / "app/settings/license/loading.tsx"),
            ("/settings/license", "loading"),
        )

    def test_25_source_owner_identity_prevents_route_collision(self):
        def candidate(route: str, owner: str) -> UiCandidate:
            return UiCandidate(
                runtime_alias="pc",
                route_path=route,
                route_id=stable_id("ROUTE", "pc", slug(route)),
                route_source_file=owner,
                render_source_file=owner,
                render_symbol="Error",
                owner_file=owner,
                owner_symbol="Error",
                class_name="btn",
                tag_name="button",
                widget_kind="button",
                text_hint="Retry",
                instance_policy="SINGLE_OR_STATIC",
                data_attributes={},
                source_hash="A" * 64,
            )

        audit = record_from_candidate(
            candidate("/audit", "apps/terminal-de-venta-system/products/pc/app/app/audit/error.tsx"),
            [],
            {},
            1,
            {},
            [],
        )
        catalog = record_from_candidate(
            candidate("/catalog", "apps/terminal-de-venta-system/products/pc/app/app/catalog/error.tsx"),
            [],
            {},
            1,
            {},
            [],
        )
        records, _, conflicts = deduplicate_records([catalog, audit])
        reversed_records, _, reversed_conflicts = deduplicate_records([
            json.loads(json.dumps(audit)),
            json.loads(json.dumps(catalog)),
        ])
        self.assertFalse(conflicts)
        self.assertFalse(reversed_conflicts)
        self.assertEqual(len({record["componentId"] for record in records}), 2)
        self.assertEqual(len({record["slotId"] for record in records}), 2)
        self.assertEqual(len({record["componentUiId"] for record in records}), 2)
        self.assertEqual(
            [(record["ownerFile"], record["componentId"], record["slotId"]) for record in records],
            [(record["ownerFile"], record["componentId"], record["slotId"]) for record in reversed_records],
        )
        self.assertFalse(any("projection_" in record["componentId"] for record in records))
        self.assertFalse(any("_slot_" in record["slotId"] for record in records))


if __name__ == "__main__":
    unittest.main(verbosity=2)
