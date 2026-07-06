from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from code_atlas.core.io_utils import human_bytes, iter_project_files, safe_rel, write_json, write_text, iso_now
from code_atlas.coverage.atlas_audit import CoverageAuditConfig, run_audit, save_audit
from code_atlas.coverage.important_gate import evaluate_gate, save_gate
from code_atlas.db_glass.reality_check import run_reality_check, save_reality_check
from code_atlas.operational.evidence import run_operational_evidence


def build_tree_text(root: Path) -> str:
    lines = ["Code Atlas Todo El Show Plus Tree", f"Generated: {iso_now()}", f"Root: {root.resolve()}", "", "Tree:"]
    for p in iter_project_files(root):
        rel = safe_rel(p, root)
        depth = rel.count("/")
        size = human_bytes(p.stat().st_size) if p.exists() else "0 B"
        lines.append(f"{'  ' * depth}- {Path(rel).name} [{size}] :: {rel}")
    return "\n".join(lines) + "\n"


def run_todo_plus(project_root: Path, output_dir: Path, *, atlas_paths: tuple[Path, ...] = (), meta_paths: tuple[Path, ...] = (), package_paths: tuple[Path, ...] = (), allow_unknown_missing: bool = True) -> dict[str, Any]:
    root = project_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    coverage = run_audit(CoverageAuditConfig(root, atlas_paths, meta_paths, package_paths, output_dir))
    cov_json, cov_md = save_audit(coverage, output_dir)
    gate = evaluate_gate(coverage, allow_unknown_missing=allow_unknown_missing)
    gate_json, gate_md = save_gate(gate, output_dir)
    db = run_reality_check(root)
    db_json, db_md = save_reality_check(db, output_dir)
    operational = run_operational_evidence(root, output_dir / "operational_evidence")
    tree_path = write_text(output_dir / "full_tree.txt", build_tree_text(root))

    manifest = {
        "kind": "todo_el_show_manifest_plus_v1",
        "created_at": iso_now(),
        "project_root": str(root),
        "validation": "PASS" if coverage.get("validation") == "PASS" and gate.get("status") == "PASS" and db.get("validation") == "PASS" else "FAIL",
        "components": {
            "atlas_coverage_audit": {"validation": coverage.get("validation"), "json": str(cov_json), "md": str(cov_md), "counts": coverage.get("counts", {})},
            "important_files_gate": {"status": gate.get("status"), "json": str(gate_json), "md": str(gate_md), "blockers_count": gate.get("blockers_count", 0)},
            "db_reality_check": {"validation": db.get("validation"), "json": str(db_json), "md": str(db_md), "counts": db.get("counts", {}), "warnings": db.get("warnings", [])},
            "operational_evidence_atlas": {"status": operational.get("production_readiness"), "production_certified": operational.get("production_certified", False), "output_dir": operational.get("output_dir"), "exports": operational.get("exports", {})},
            "tree": {"path": str(tree_path)},
        },
    }
    manifest["output_policy"] = {
        "nested_bundle_zip": "disabled",
        "reason": "Todo El Show Plus is packed by the outer single-zip pipeline.",
        "reports_dir": str(output_dir),
    }
    manifest_json = write_json(output_dir / "todo_el_show_manifest_plus.json", manifest)
    manifest_md = write_text(output_dir / "todo_el_show_manifest_plus.md", render_manifest_md(manifest))
    manifest["manifest_json"] = str(manifest_json)
    manifest["manifest_md"] = str(manifest_md)
    write_json(manifest_json, manifest)
    return manifest


def render_manifest_md(manifest: dict[str, Any]) -> str:
    comp = manifest.get("components", {})
    lines = [
        "# Todo El Show Manifest Plus",
        "",
        f"- Project: `{manifest.get('project_root')}`",
        f"- Validation: **{manifest.get('validation')}**",
        "",
        "## Components",
        "",
    ]
    for name, data in comp.items():
        lines.append(f"### {name}")
        lines.append("")
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"- {k}: `{json.dumps(v, ensure_ascii=False)[:500]}`")
            else:
                lines.append(f"- {k}: `{v}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Todo El Show Manifest Plus.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out", default="reports/atlas_plus")
    parser.add_argument("--atlas", action="append", default=[])
    parser.add_argument("--meta", action="append", default=[])
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--strict-unknown-missing", action="store_true")
    args = parser.parse_args(argv)
    manifest = run_todo_plus(
        Path(args.project_root), Path(args.out),
        atlas_paths=tuple(Path(x) for x in args.atlas),
        meta_paths=tuple(Path(x) for x in args.meta),
        package_paths=tuple(Path(x) for x in args.package),
        allow_unknown_missing=not args.strict_unknown_missing,
    )
    print(f"Todo El Show Manifest Plus: {manifest['validation']} -> {manifest.get('manifest_md')}")
    return 0 if manifest["validation"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

# CATLAS_OPERATIONAL_V3_TODO_EL_SHOW_PLUS_BEGIN
TODO_EL_SHOW_PLUS_OPERATIONAL_EVIDENCE_V3={
  "id":"operational_evidence_atlas_v3",
  "status":"source_ready_not_production_certified",
  "monolith_dependency":False,
  "entrypoints":["code_atlas.operational.runner:run_operational_atlas","code_atlas.operational.cli:main"],
  "hard_rules":["ERD = structure","Operational Evidence = row-level evidence","Production Gate = certification","unknown_missing_provenance = no green","Multi-Tenant Leakage Guard blocks without real tenant/scope contract","Do not touch tools/code-atlas/code-atlas.py without explicit authorization"]
}
# CATLAS_OPERATIONAL_V3_TODO_EL_SHOW_PLUS_END
