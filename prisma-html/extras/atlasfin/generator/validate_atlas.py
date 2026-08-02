from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

PAGES = ["index.html", "a-fundamentos.html", "b-materiales.html", "c-acciones.html", "d-entrada-texto.html", "e-seleccion-filtros.html", "f-navegacion.html", "g-tablas.html", "h-listas.html", "i-paneles-cards.html", "j-expansion.html", "k-estados-feedback.html", "l-carga-progreso.html", "m-overlays.html", "n-operativos.html", "o-patrones-pantalla.html", "p-movimiento.html", "q-responsive-accesibilidad.html", "r-contenido.html", "s-analitica.html", "t-archivos-medios.html", "u-calendario.html", "v-comercio-pagos.html", "w-identidad-seguridad.html", "x-sistema-diagnostico.html", "y-i18n-impresion-offline.html", "z-gobierno.html"]
SCHEMAS = ["PRISMA_VISUAL_PROPERTY_REGISTRY_V1", "PRISMA_VISUAL_FAMILY_REGISTRY_V1", "PRISMA_VISUAL_PRESET_REGISTRY_V1", "PRISMA_VISUAL_RECIPE_REGISTRY_V4", "PRISMA_VISUAL_STATE_REGISTRY_V1", "PRISMA_VISUAL_VARIANT_REGISTRY_V1", "PRISMA_SURFACE_ADAPTER_REGISTRY_V2", "PRISMA_VISUAL_ASSET_REGISTRY_V1", "PRISMA_PORTABLE_VISUAL_TRANSFER_V2", "PRISMA_VISUAL_BINDING_REQUIREMENTS_V1", "PRISMA_VISUAL_RECIPE_COVERAGE_V1", "PRISMA_VISUAL_MIGRATION_REPORT_V1", "PRISMA_VISUAL_IMPORT_INSPECTION_V1", "PRISMA_VISUAL_DELTA_V2", "PRISMA_VISREC2_CONSOLE_STATE_V2", "PRISMA_ATLASFIN_VISUAL_CONTROL_PILOT_V1", "PRISMA_ATLASFIN_VISUAL_APPLICATION_REQUEST_V1", "PRISMA_ATLASFIN_VISUAL_APPLICATION_RESULT_V1", "PRISMA_ATLASFIN_VISUAL_APPLICATION_EVIDENCE_BUNDLE_V1"]
MODULES = ["runtime.js", "selection-engine.js", "fingerprint-engine.js", "property-engine.js", "recipe-engine.js", "state-engine.js", "adapter-engine.js", "compatibility-engine.js", "preview-engine.js", "export-engine.js", "migration-engine.js", "import-inspector.js", "checksum-engine.js", "console-engine.js", "governed-control-engine.js"]
VISREC2_TASK_COUNT = 20
VISIBLE_CONTROL_COUNTS = {"properties": 12, "states": 12, "variants": 8, "targets": 4, "transferModes": 3}


def canonical_sha256(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("atlas_root")
    parser.add_argument("--report")
    args = parser.parse_args()
    atlas = Path(args.atlas_root).resolve()
    issues = []

    for page in PAGES:
        path = atlas / page
        if not path.is_file():
            issues.append({"code": "PAGE_MISSING", "page": page})
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for marker in ['href="assets/css/visual-recipe-dock.css"', 'src="assets/data/visual.recipe.registry.js"', 'src="assets/js/atlas.js"']:
            if text.count(marker) != 1:
                issues.append({"code": "PAGE_SHARED_RUNTIME", "page": page, "marker": marker, "actual": text.count(marker)})

    data = atlas / "assets" / "data"
    schema_dir = atlas / "schemas" / "visual"
    module_dir = atlas / "assets" / "js" / "visrec2"
    registry_names = [
        "visual-property.registry.json", "visual-family.registry.json",
        "visual-preset.registry.json", "visual-recipe.registry.json",
        "visual-state.registry.json", "visual-variant.registry.json",
        "surface-adapter.registry.json", "visual-asset.registry.json",
        "field-alias.registry.json", "registry-index.json",
    ]
    for name in registry_names:
        if not (data / name).is_file():
            issues.append({"code": "REGISTRY_MISSING", "path": name})
    for schema_id in SCHEMAS:
        path = schema_dir / f"{schema_id}.schema.json"
        if not path.is_file():
            issues.append({"code": "SCHEMA_MISSING", "path": path.name})
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for field in ["$id", "$schema", "title", "version", "required", "additionalProperties", "x-discriminator", "examples", "x-migration"]:
            if field not in payload:
                issues.append({"code": "SCHEMA_METADATA", "schema": schema_id, "field": field})
    for name in MODULES:
        if not (module_dir / name).is_file():
            issues.append({"code": "MODULE_MISSING", "path": name})

    pilot_json_path = data / "visual-control.cobrar.pilot.json"
    pilot_js_path = data / "visual-control.cobrar.pilot.js"
    application_json_path = data / "visual-application.cobrar.current.json"
    application_js_path = data / "visual-application.cobrar.current.js"
    index_text = (atlas / "index.html").read_text(encoding="utf-8", errors="replace")
    for marker in [
        'src="assets/js/visrec2/governed-control-engine.js"',
        "data-atlas-control-open",
        "data-atlas-control-panel",
        "data-atlas-control-content",
    ]:
        if index_text.count(marker) != 1:
            issues.append({"code": "CANONICAL_CONTROL_MARKER", "marker": marker, "actual": index_text.count(marker)})
    if "Lote futuro" in index_text:
        issues.append({"code": "FUTURE_BATCH_MARKER_PRESENT"})

    pilot = None
    if not pilot_json_path.is_file():
        issues.append({"code": "CONTROL_PILOT_MISSING", "path": pilot_json_path.name})
    else:
        pilot_text = pilot_json_path.read_text(encoding="utf-8")
        pilot = json.loads(pilot_text)
        if re.search(r"[A-Za-z]:\\\\", pilot_text) or "file://" in pilot_text.lower():
            issues.append({"code": "CONTROL_PILOT_LOCAL_PATH"})
        expected_pilot = {
            "surfaceId": "SURF.tb.pos",
            "routeId": "ROUTE.tb.pos",
            "ownerId": "OWN.tb.pos_ticket_panel",
            "regionId": "ZONE.tb.pos.payment",
            "slotId": "SLOT.tb.pos.payment.cobrar",
            "componentUiId": "TB-POS-PAY-COBRAR-BTN-01",
            "selector": ".cobrarReferenceButton",
            "layerId": "LYR.ACT.PRIMARY.TABLET.POS.COBRAR.BASE",
            "implementationLayerId": "products.tablet.app.components.pos.pos.module.css.cobrarreferencebutton",
            "bindingId": "BND.ACT.PRIMARY.TABLET.POS.COBRAR.V1",
        }
        for field, expected in expected_pilot.items():
            actual = pilot.get("pilot", {}).get(field)
            if actual != expected:
                issues.append({"code": "CONTROL_PILOT_HIERARCHY", "field": field, "expected": expected, "actual": actual})
        safety = pilot.get("safety", {})
        plan = pilot.get("plan", {})
        if pilot.get("status") != "READY_FOR_SOURCE_ONLY_PLANNING":
            issues.append({"code": "CONTROL_PLANNING_STATUS", "actual": pilot.get("status")})
        if any(safety.get(field) is not False for field in ["runtimeMutationAllowed", "productApplicationAllowed", "sourceMutationPerformed"]):
            issues.append({"code": "CONTROL_MUTATION_GUARD", "actual": safety})
        if plan.get("applicationEnabled") is not False or plan.get("status") != "PLAN_READY_FOR_REVIEW":
            issues.append({"code": "CONTROL_BRIDGE_GUARD", "actual": {"applicationEnabled": plan.get("applicationEnabled"), "status": plan.get("status")}})
        if plan.get("operationCount") != 11 or len(plan.get("operations", [])) != 11:
            issues.append({"code": "CONTROL_PLAN_OPERATION_COUNT", "actual": plan.get("operationCount")})
        if pilot.get("recipe", {}).get("plannedPropertyCount") != 89 or pilot.get("recipe", {}).get("missingPropertyCount") != 0:
            issues.append({"code": "CONTROL_RECIPE_COVERAGE_COUNTS", "actual": pilot.get("recipe")})
        if sum(operation.get("propertyCount", 0) for operation in plan.get("operations", []) if isinstance(operation, dict)) != 89:
            issues.append({"code": "CONTROL_PLAN_PROPERTY_COUNT"})
        if plan.get("blockingReasons"):
            issues.append({"code": "CONTROL_SOURCE_PLAN_BLOCKED", "actual": plan.get("blockingReasons")})
        gate_statuses = {gate.get("gateId"): gate.get("status") for gate in pilot.get("gates", []) if isinstance(gate, dict)}
        required_gate_statuses = {
            "RECIPE_COVERAGE_FRESHNESS": "PASS",
            "MAMASTROPHIC_VISUAL_EVIDENCE": "SOURCE_EVIDENCE_AVAILABLE_RUNTIME_REVIEW_REQUIRED",
            "PRODUCT_APPLICATION": "DISABLED_BY_CONTRACT",
        }
        for gate_id, expected in required_gate_statuses.items():
            if gate_statuses.get(gate_id) != expected:
                issues.append({"code": "CONTROL_GATE_TRUTH", "gateId": gate_id, "expected": expected, "actual": gate_statuses.get(gate_id)})
        if pilot.get("evidence", {}).get("runtime", {}).get("status") != "NOT_CERTIFIED":
            issues.append({"code": "CONTROL_RUNTIME_PROMOTION"})
        rendering = pilot.get("rendering", {})
        if rendering.get("loadPolicy") != "LAZY_ON_EXPLICIT_OPEN" or rendering.get("initialOperationRenderCount") != 0 or rendering.get("operationPageSize") != 4:
            issues.append({"code": "CONTROL_RENDERING_POLICY", "actual": rendering})
        integrity = pilot.get("integrity", {})
        payload_without_integrity = dict(pilot)
        payload_without_integrity.pop("integrity", None)
        if integrity.get("canonicalPayloadSha256") != canonical_sha256(payload_without_integrity):
            issues.append({"code": "CONTROL_INTEGRITY"})

    if not pilot_js_path.is_file():
        issues.append({"code": "CONTROL_PILOT_JS_MISSING", "path": pilot_js_path.name})
    elif pilot is not None:
        js_text = pilot_js_path.read_text(encoding="utf-8")
        prefix = "window.PRISMA_ATLASFIN_VISUAL_CONTROL = "
        if not js_text.startswith(prefix) or not js_text.endswith(";\n"):
            issues.append({"code": "CONTROL_PILOT_JS_WRAPPER"})
        else:
            js_payload = json.loads(js_text[len(prefix):-2])
            if js_payload != pilot:
                issues.append({"code": "CONTROL_PILOT_JS_PARITY"})

    application = None
    if not application_json_path.is_file():
        issues.append({"code": "CONTROL_APPLICATION_MISSING", "path": application_json_path.name})
    else:
        application_text = application_json_path.read_text(encoding="utf-8")
        application = json.loads(application_text)
        if re.search(r"[A-Za-z]:\\\\", application_text) or "file://" in application_text.lower():
            issues.append({"code": "CONTROL_APPLICATION_LOCAL_PATH"})
        if application.get("schema") != "PRISMA_ATLASFIN_VISUAL_APPLICATION_RESULT_V1":
            issues.append({"code": "CONTROL_APPLICATION_SCHEMA", "actual": application.get("schema")})
        if application.get("status") != "APPLIED_AND_RUNTIME_VISUAL_CERTIFIED":
            issues.append({"code": "CONTROL_APPLICATION_STATUS", "actual": application.get("status")})
        if application.get("productFileCount") != 1 or len(application.get("productFiles", [])) != 1:
            issues.append({"code": "CONTROL_APPLICATION_SCOPE", "actual": application.get("productFiles")})
        preview = application.get("preview", {})
        evidence = preview.get("evidenceBundle", {})
        post_plan = preview.get("postApplicationPlan", {})
        if post_plan.get("status") != "NO_ACTIONABLE_DIFF" or post_plan.get("changedLineCount") != 0:
            issues.append({"code": "CONTROL_APPLICATION_POST_PLAN", "actual": post_plan})
        if evidence.get("comparison", {}).get("pixel", {}).get("visuallyChanged") is not True:
            issues.append({"code": "CONTROL_APPLICATION_VISUAL_DIFF"})
        if evidence.get("console", {}).get("newErrorCount") != 0:
            issues.append({"code": "CONTROL_APPLICATION_CONSOLE_REGRESSION"})
        if evidence.get("network", {}).get("status") != "PASS_NO_TARGET_NETWORK_FAILURES":
            issues.append({"code": "CONTROL_APPLICATION_NETWORK"})
        if application.get("rollback", {}).get("ready") is not True:
            issues.append({"code": "CONTROL_APPLICATION_ROLLBACK"})
        integrity = application.get("integrity", {})
        payload_without_integrity = dict(application)
        payload_without_integrity.pop("integrity", None)
        if integrity.get("canonicalPayloadSha256") != canonical_sha256(payload_without_integrity):
            issues.append({"code": "CONTROL_APPLICATION_INTEGRITY"})

    if not application_js_path.is_file():
        issues.append({"code": "CONTROL_APPLICATION_JS_MISSING", "path": application_js_path.name})
    elif application is not None:
        application_js = application_js_path.read_text(encoding="utf-8")
        prefix = "window.PRISMA_ATLASFIN_VISUAL_APPLICATION = "
        if not application_js.startswith(prefix) or not application_js.endswith(";\n"):
            issues.append({"code": "CONTROL_APPLICATION_JS_WRAPPER"})
        elif json.loads(application_js[len(prefix):-2]) != application:
            issues.append({"code": "CONTROL_APPLICATION_JS_PARITY"})

    control_module_path = module_dir / "governed-control-engine.js"
    if control_module_path.is_file():
        control_text = control_module_path.read_text(encoding="utf-8", errors="replace")
        for marker in ['document.createElement("script")', ".slice(", "operationPageSize", "searchText", "visual-application.cobrar.current.js", "data-atlas-application-action"]:
            if marker not in control_text:
                issues.append({"code": "CONTROL_RUNTIME_MARKER", "marker": marker})
        control_css = (atlas / "assets/css/visual-recipe-dock.css").read_text(encoding="utf-8", errors="replace")
        if "content-visibility: auto" not in control_css or "contain-intrinsic-size" not in control_css:
            issues.append({"code": "CONTROL_VIRTUALIZATION_MISSING"})

    master = json.loads((data / "visual.recipe.registry.json").read_text(encoding="utf-8"))
    transfer = master.get("transfer_console", {})
    if master.get("schema") != "PRISMA_VISUAL_RECIPE_REGISTRY_V4":
        issues.append({"code": "MASTER_SCHEMA", "actual": master.get("schema")})
    if transfer.get("schema") != "PRISMA_VISREC2_CONSOLE_STATE_V2":
        issues.append({"code": "CONSOLE_SCHEMA", "actual": transfer.get("schema")})
    if transfer.get("export_schema") != "PRISMA_PORTABLE_VISUAL_TRANSFER_V2":
        issues.append({"code": "EXPORT_SCHEMA", "actual": transfer.get("export_schema")})
    if transfer.get("visible_control_contract", {}).get("counts") != VISIBLE_CONTROL_COUNTS:
        issues.append({"code": "VISIBLE_CONTROL_DRIFT", "actual": transfer.get("visible_control_contract", {}).get("counts")})
    if transfer.get("visible_control_contract", {}).get("additionalControlCount") != 0:
        issues.append({"code": "ADDITIONAL_VISIBLE_CONTROLS"})
    if len(transfer.get("tasks", [])) != VISREC2_TASK_COUNT:
        issues.append({"code": "TASK_COUNT", "actual": len(transfer.get("tasks", []))})
    if not transfer.get("instruction_only") or transfer.get("direct_target_mutation") is not False:
        issues.append({"code": "MUTATION_GUARD"})
    if "PRISMA_PORTABLE_VISUAL_TRANSFER_V1" not in master.get("legacy_export_schemas", []):
        issues.append({"code": "V1_NOT_PRESERVED"})

    asset_registry = json.loads((data / "visual-asset.registry.json").read_text(encoding="utf-8"))
    for item in asset_registry.get("items", []):
        ref = str(item.get("portableReference", ""))
        if ":\\" in ref or ref.startswith("/"):
            issues.append({"code": "LOCAL_ASSET_PATH", "assetId": item.get("assetId")})

    managed_text = "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in [atlas / "assets" / "css" / "visual-recipe-dock.css", *module_dir.glob("*.js")]
    )
    if "!important" in managed_text:
        issues.append({"code": "IMPORTANT_FOUND"})

    report = {
        "status": "PASS" if not issues else "FAIL",
        "schema": "PRISMA_VISREC2_ATLAS_VALIDATION_V3",
        "pageCoverage": f"{len(PAGES)}/{len(PAGES)}",
        "taskCoverage": f"{len(transfer.get('tasks', []))}/{VISREC2_TASK_COUNT}",
        "visibleControlsPreserved": not any(issue["code"] == "VISIBLE_CONTROL_DRIFT" for issue in issues),
        "additionalVisibleControls": 0,
        "instructionOnly": transfer.get("instruction_only"),
        "issues": issues,
    }
    if args.report:
        report_path = Path(args.report).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
