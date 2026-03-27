from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from .bundles import validate_bundle_zip
from .common import SCHEMA_VERSION, utc_now, write_json
from .config import load_parallel_manifest


def compute_overlap(bundle_reports: list[dict[str, Any]]) -> dict[str, Any]:
    owners: dict[str, list[str]] = defaultdict(list)
    for report in bundle_reports:
        manifest = report.get("bundle_manifest") or {}
        package_id = manifest.get("package_id", "unknown")
        for payload in manifest.get("payload_files", []):
            if isinstance(payload, dict) and "repo_path" in payload:
                owners[payload["repo_path"]].append(package_id)
    conflicts = []
    for path, package_ids in sorted(owners.items()):
        unique_packages = sorted(set(package_ids))
        if len(unique_packages) > 1:
            conflicts.append({"path": path, "packages": unique_packages})
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": utc_now(),
        "conflicts": conflicts,
        "ok": len(conflicts) == 0,
    }


def build_acceptance_result(project_id: str, run_id: str, round_id: str, bundle_reports: list[dict[str, Any]], overlap_report: dict[str, Any]) -> dict[str, Any]:
    if not bundle_reports:
        return {
            "schema_version": SCHEMA_VERSION,
            "project_id": project_id,
            "run_id": run_id,
            "round_id": round_id,
            "generated_at_utc": utc_now(),
            "overall_status": "pending",
            "package_results": [],
            "overlap_ok": overlap_report.get("ok", False),
        }

    conflict_paths = {item["path"] for item in overlap_report.get("conflicts", [])}
    package_results = []
    overall_status = "accept"

    for report in bundle_reports:
        manifest = report.get("bundle_manifest") or {}
        package_id = manifest.get("package_id", "unknown")
        touched = {item.get("repo_path") for item in manifest.get("payload_files", []) if isinstance(item, dict)}
        package_conflicts = sorted(conflict_paths.intersection(touched))
        reasons: list[str] = []
        corrections: list[str] = []
        status = "accept"

        if report.get("schema_errors") or report.get("structure_errors") or report.get("ownership_errors") or report.get("payload_mismatches"):
            status = "reject"
            reasons.append("bundle failed validation checks")
            corrections.append("Fix schema, structure, ownership, and payload consistency errors.")

        if package_conflicts:
            status = "reject"
            reasons.append("bundle conflicts with another package on exact repo paths")
            corrections.append(f"Resolve conflicted paths: {', '.join(package_conflicts)}")

        if report.get("warnings") and status == "accept":
            status = "accept_with_conditions"
            corrections.append("Review warnings before integration.")

        if status == "reject":
            overall_status = "reject"
        elif status == "accept_with_conditions" and overall_status == "accept":
            overall_status = "accept_with_conditions"

        package_results.append({
            "package_id": package_id,
            "bundle_id": manifest.get("bundle_id", "unknown"),
            "status": status,
            "reasons": reasons,
            "corrections": corrections,
        })

    return {
        "schema_version": SCHEMA_VERSION,
        "project_id": project_id,
        "run_id": run_id,
        "round_id": round_id,
        "generated_at_utc": utc_now(),
        "overall_status": overall_status,
        "package_results": package_results,
        "overlap_ok": overlap_report.get("ok", False),
    }


def compute_apply_order(repo_root: Path, accepted_package_ids: list[str]) -> list[str]:
    manifest = load_parallel_manifest(repo_root)
    accepted = set(accepted_package_ids)
    graph = {pkg: [dep for dep in manifest[pkg]["depends_on"] if dep in accepted] for pkg in accepted_package_ids}
    indegree = {pkg: 0 for pkg in accepted_package_ids}
    for pkg, deps in graph.items():
        for dep in deps:
            indegree[pkg] += 1

    order: list[str] = []
    ready = sorted([pkg for pkg, deg in indegree.items() if deg == 0])
    while ready:
        pkg = ready.pop(0)
        order.append(pkg)
        for candidate in accepted_package_ids:
            if pkg in graph.get(candidate, []):
                indegree[candidate] -= 1
                if indegree[candidate] == 0 and candidate not in order and candidate not in ready:
                    ready.append(candidate)
                    ready.sort()

    if len(order) != len(accepted_package_ids):
        return accepted_package_ids
    return order


def validate_bundles_and_write_reports(project_id: str, run_id: str, round_id: str, bundle_paths: list[Path], repo_root: Path, reports_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    bundle_reports = [validate_bundle_zip(path, repo_root) for path in bundle_paths]
    overlap = compute_overlap(bundle_reports)
    acceptance = build_acceptance_result(project_id, run_id, round_id, bundle_reports, overlap)
    write_json(reports_dir / "bundle_validation_reports.json", bundle_reports)
    write_json(reports_dir / "overlap_report.json", overlap)
    write_json(reports_dir / "acceptance_report.json", acceptance)
    return bundle_reports, overlap, acceptance
