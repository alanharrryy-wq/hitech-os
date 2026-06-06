from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from code_atlas.core.io_utils import read_json, write_json, write_text, iso_now
from code_atlas.coverage.atlas_audit import CoverageAuditConfig, run_audit, save_audit


def evaluate_gate(report: dict[str, Any], *, allow_unknown_missing: bool = False) -> dict[str, Any]:
    missing_important = list(report.get("missing_important") or [])
    classes = report.get("missing_classification") or {}
    critical = list(classes.get("critical") or [])
    unknown = list(classes.get("unknown") or [])
    blockers = []
    if missing_important:
        blockers.append({"code": "missing_important_entrypoints", "count": len(missing_important), "items": missing_important})
    if critical:
        blockers.append({"code": "missing_critical_atlas_nodes", "count": len(critical), "items": critical})
    if unknown and not allow_unknown_missing:
        blockers.append({"code": "missing_unknown_atlas_nodes", "count": len(unknown), "items": unknown[:200]})
    status = "PASS" if not blockers else "FAIL"
    return {
        "kind": "important_files_gate_v1",
        "created_at": iso_now(),
        "status": status,
        "blockers_count": len(blockers),
        "blockers": blockers,
        "source_validation": report.get("validation"),
        "source_counts": report.get("counts", {}),
    }


def render_gate_markdown(gate: dict[str, Any]) -> str:
    lines = [
        "# Important Files Gate",
        "",
        f"- Status: **{gate.get('status')}**",
        f"- Blockers: **{gate.get('blockers_count', 0)}**",
        "",
    ]
    blockers = gate.get("blockers") or []
    if blockers:
        lines.append("## Blockers")
        lines.append("")
        for block in blockers:
            lines.append(f"### {block.get('code')} ×{block.get('count')}")
            lines.append("")
            for item in (block.get("items") or [])[:200]:
                lines.append(f"- `{item}`")
            lines.append("")
    else:
        lines.append("No blockers. La puerta está abierta, no como caseta tomada en puente largo.")
    return "\n".join(lines).rstrip() + "\n"


def save_gate(gate: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "important_files_gate.json"
    md_path = output_dir / "important_files_gate.md"
    write_json(json_path, gate)
    write_text(md_path, render_gate_markdown(gate))
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Important Files Gate.")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--coverage-report", default="")
    parser.add_argument("--atlas", action="append", default=[])
    parser.add_argument("--meta", action="append", default=[])
    parser.add_argument("--package", action="append", default=[])
    parser.add_argument("--out", default="reports/atlas_plus")
    parser.add_argument("--allow-unknown-missing", action="store_true")
    args = parser.parse_args(argv)

    out = Path(args.out)
    if args.coverage_report:
        report = read_json(args.coverage_report)
    else:
        report = run_audit(CoverageAuditConfig(
            project_root=Path(args.project_root),
            atlas_paths=tuple(Path(x) for x in args.atlas),
            meta_paths=tuple(Path(x) for x in args.meta),
            package_paths=tuple(Path(x) for x in args.package),
            output_dir=out,
        ))
        save_audit(report, out)
    gate = evaluate_gate(report, allow_unknown_missing=args.allow_unknown_missing)
    _, md = save_gate(gate, out)
    print(f"Important Files Gate: {gate['status']} -> {md}")
    return 0 if gate["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
