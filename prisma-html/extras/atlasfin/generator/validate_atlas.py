from __future__ import annotations

import argparse
import json
from pathlib import Path

PAGES = ["index.html", "a-fundamentos.html", "b-materiales.html", "c-acciones.html", "d-entrada-texto.html", "e-seleccion-filtros.html", "f-navegacion.html", "g-tablas.html", "h-listas.html", "i-paneles-cards.html", "j-expansion.html", "k-estados-feedback.html", "l-carga-progreso.html", "m-overlays.html", "n-operativos.html", "o-patrones-pantalla.html", "p-movimiento.html", "q-responsive-accesibilidad.html", "r-contenido.html", "s-analitica.html", "t-archivos-medios.html", "u-calendario.html", "v-comercio-pagos.html", "w-identidad-seguridad.html", "x-sistema-diagnostico.html", "y-i18n-impresion-offline.html", "z-gobierno.html"]
SCHEMAS = ["PRISMA_VISUAL_PROPERTY_REGISTRY_V1", "PRISMA_VISUAL_FAMILY_REGISTRY_V1", "PRISMA_VISUAL_PRESET_REGISTRY_V1", "PRISMA_VISUAL_RECIPE_REGISTRY_V4", "PRISMA_VISUAL_STATE_REGISTRY_V1", "PRISMA_VISUAL_VARIANT_REGISTRY_V1", "PRISMA_SURFACE_ADAPTER_REGISTRY_V2", "PRISMA_VISUAL_ASSET_REGISTRY_V1", "PRISMA_PORTABLE_VISUAL_TRANSFER_V2", "PRISMA_VISUAL_BINDING_REQUIREMENTS_V1", "PRISMA_VISUAL_RECIPE_COVERAGE_V1", "PRISMA_VISUAL_MIGRATION_REPORT_V1", "PRISMA_VISUAL_IMPORT_INSPECTION_V1", "PRISMA_VISUAL_DELTA_V2", "PRISMA_VISREC2_CONSOLE_STATE_V2"]
MODULES = ["runtime.js", "selection-engine.js", "fingerprint-engine.js", "property-engine.js", "recipe-engine.js", "state-engine.js", "adapter-engine.js", "compatibility-engine.js", "preview-engine.js", "export-engine.js", "migration-engine.js", "import-inspector.js", "checksum-engine.js", "console-engine.js"]
VISREC2_TASK_COUNT = 20
VISIBLE_CONTROL_COUNTS = {"properties": 12, "states": 12, "variants": 8, "targets": 4, "transferModes": 3}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("atlas_root")
    parser.add_argument("--report", required=True)
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
        "schema": "PRISMA_VISREC2_ATLAS_VALIDATION_V2",
        "pageCoverage": f"{len(PAGES)}/{len(PAGES)}",
        "taskCoverage": f"{len(transfer.get('tasks', []))}/{VISREC2_TASK_COUNT}",
        "visibleControlsPreserved": not any(issue["code"] == "VISIBLE_CONTROL_DRIFT" for issue in issues),
        "additionalVisibleControls": 0,
        "instructionOnly": transfer.get("instruction_only"),
        "issues": issues,
    }
    report_path = Path(args.report).resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
