from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from code_atlas.core.io_utils import human_bytes, iso_now, iter_project_files, safe_rel, write_json, write_text
from code_atlas.coverage.atlas_audit import CoverageAuditConfig, run_audit, save_audit
from code_atlas.coverage.important_gate import evaluate_gate, save_gate
from code_atlas.db_glass.reality_check import run_reality_check, save_reality_check
from code_atlas.operational.evidence import run_operational_evidence


def build_tree_text(root: Path) -> str:
    lines = ["Code Atlas Todo Plus Tree", f"Generated: {iso_now()}", f"Root name: {root.name}", "", "Tree:"]
    for path in iter_project_files(root):
        rel = safe_rel(path, root)
        depth = rel.count("/")
        size = human_bytes(path.stat().st_size) if path.exists() else "0 B"
        lines.append(f"{'  ' * depth}- {Path(rel).name} [{size}] :: {rel}")
    return "\n".join(lines) + "\n"


def _out_ref(path: Path, output_dir: Path) -> str:
    try:
        return path.resolve().relative_to(output_dir.resolve()).as_posix()
    except Exception:
        return path.name


def run_todo_plus(
    project_root: Path,
    output_dir: Path,
    *,
    atlas_paths: tuple[Path, ...] = (),
    meta_paths: tuple[Path, ...] = (),
    package_paths: tuple[Path, ...] = (),
    allow_unknown_missing: bool = True,
) -> dict[str, Any]:
    root = project_root.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    coverage = run_audit(CoverageAuditConfig(root, atlas_paths, meta_paths, package_paths, output_dir))
    cov_json, cov_md = save_audit(coverage, output_dir)
    gate = evaluate_gate(coverage, allow_unknown_missing=allow_unknown_missing)
    gate_json, gate_md = save_gate(gate, output_dir)
    db = run_reality_check(root)
    db_json, db_md = save_reality_check(db, output_dir)
    operational = run_operational_evidence(root, output_dir / "operational_evidence")
    tree_path = write_text(output_dir / "full_tree.txt", build_tree_text(root))

    operational_status = str(operational.get("sourceHardeningStatus") or operational.get("status") or "UNKNOWN")
    manifest = {
        "kind": "todo_plus_manifest_v2",
        "created_at": iso_now(),
        "project_name": root.name,
        "project_path_digest": "sha256:" + hashlib.sha256(str(root).encode("utf-8", errors="ignore")).hexdigest()[:20],
        "environment_neutral": True,
        "validation": "PASS" if coverage.get("validation") == "PASS" and gate.get("status") == "PASS" and db.get("validation") == "PASS" else "FAIL",
        "productionCertified": False,
        "components": {
            "atlas_coverage_audit": {"validation": coverage.get("validation"), "json": _out_ref(cov_json, output_dir), "md": _out_ref(cov_md, output_dir), "counts": coverage.get("counts", {})},
            "important_files_gate": {"status": gate.get("status"), "json": _out_ref(gate_json, output_dir), "md": _out_ref(gate_md, output_dir), "blockers_count": gate.get("blockers_count", 0)},
            "db_reality_check": {"validation": db.get("validation"), "json": _out_ref(db_json, output_dir), "md": _out_ref(db_md, output_dir), "counts": db.get("counts", {}), "warnings": db.get("warnings", [])},
            "operational_evidence_atlas": {"status": operational_status, "productionCertified": bool(operational.get("productionCertified", False)), "output": "operational_evidence"},
            "tree": {"path": _out_ref(tree_path, output_dir)},
        },
        "output_policy": {
            "nested_bundle_zip": "disabled",
            "reason": "The outer caller controls final packaging.",
            "reports_dir": ".",
        },
    }
    manifest_json = write_json(output_dir / "todo_plus_manifest.json", manifest)
    manifest_md = write_text(output_dir / "todo_plus_manifest.md", render_manifest_md(manifest))
    manifest["manifest_json"] = _out_ref(manifest_json, output_dir)
    manifest["manifest_md"] = _out_ref(manifest_md, output_dir)
    write_json(manifest_json, manifest)
    return manifest


def render_manifest_md(manifest: dict[str, Any]) -> str:
    components = manifest.get("components", {})
    lines = [
        "# Todo Plus Manifest",
        "",
        f"- Project: `{manifest.get('project_name')}`",
        f"- Validation: **{manifest.get('validation')}**",
        f"- Production certified: **{manifest.get('productionCertified')}**",
        "",
        "## Components",
        "",
    ]
    for name, data in components.items():
        lines.extend([f"### {name}", ""])
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"- {key}: `{json.dumps(value, ensure_ascii=False)[:500]}`")
            else:
                lines.append(f"- {key}: `{value}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Todo Plus evidence collection.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--out", default="reports/atlas_plus")
    parser.add_argument("--atlas", action="append", default=[])
    parser.add_argument("--meta", action="append", default=[])
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--strict-unknown-missing", action="store_true")
    args = parser.parse_args(argv)
    manifest = run_todo_plus(
        Path(args.project_root),
        Path(args.out),
        atlas_paths=tuple(Path(value) for value in args.atlas),
        meta_paths=tuple(Path(value) for value in args.meta),
        package_paths=tuple(Path(value) for value in args.package),
        allow_unknown_missing=not args.strict_unknown_missing,
    )
    print(f"Todo Plus: {manifest['validation']} -> {manifest.get('manifest_md')}")
    return 0 if manifest["validation"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
