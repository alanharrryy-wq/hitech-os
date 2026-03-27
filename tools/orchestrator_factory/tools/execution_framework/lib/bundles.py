from __future__ import annotations

import zipfile
from pathlib import Path
from typing import Any

from .common import Issue, extract_zip_to_temp, normalize_relpath, read_json, sha256_file
from .config import load_path_policies
from .validators import validate_against_patterns, validate_payload_items, validate_required_fields


REQUIRED_BUNDLE_FILES = [
    "bundle_manifest.json",
    "package_report.json",
    "notes/summary.md",
]


def inspect_bundle_structure(zip_path: Path) -> list[Issue]:
    issues: list[Issue] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = {normalize_relpath(name) for name in zf.namelist()}
    for required in REQUIRED_BUNDLE_FILES:
        if required not in names:
            issues.append(Issue("missing_bundle_file", f"Bundle is missing '{required}'"))
    has_payload = any(name.startswith("payload/") and not name.endswith("/") for name in names)
    if not has_payload:
        issues.append(Issue("missing_payload", "Bundle must contain payload files under payload/"))
    return issues


def validate_bundle_zip(zip_path: Path, repo_root: Path) -> dict[str, Any]:
    path_policies = load_path_policies(repo_root)
    extracted = extract_zip_to_temp(zip_path)
    result: dict[str, Any] = {
        "bundle_path": str(zip_path),
        "schema_errors": [],
        "structure_errors": [],
        "ownership_errors": [],
        "payload_mismatches": [],
        "warnings": [],
        "ok": False,
    }
    structure_issues = inspect_bundle_structure(zip_path)
    result["structure_errors"] = [issue.to_dict() for issue in structure_issues]
    manifest_path = extracted / "bundle_manifest.json"
    report_path = extracted / "package_report.json"
    if not manifest_path.exists() or not report_path.exists():
        return result

    manifest = read_json(manifest_path)
    package_report = read_json(report_path)
    result["bundle_manifest"] = manifest
    result["package_report"] = package_report

    result["schema_errors"].extend(
        issue.to_dict()
        for issue in validate_required_fields(
            manifest,
            {
                "schema_version": "string",
                "project_id": "string",
                "run_id": "string",
                "round_id": "string",
                "package_id": "string",
                "bundle_id": "string",
                "bundle_version": "integer",
                "created_at_utc": "string",
                "status": "string",
                "payload_files": "array",
            },
            "bundle_manifest",
        )
    )
    result["schema_errors"].extend(issue.to_dict() for issue in validate_payload_items(manifest.get("payload_files", [])))
    result["schema_errors"].extend(
        issue.to_dict()
        for issue in validate_required_fields(
            package_report,
            {
                "schema_version": "string",
                "project_id": "string",
                "run_id": "string",
                "round_id": "string",
                "package_id": "string",
                "bundle_id": "string",
                "summary": "string",
                "status": "string",
                "highlights": "array",
                "known_gaps": "array",
            },
            "package_report",
        )
    )

    for field in ["project_id", "run_id", "round_id", "package_id", "bundle_id"]:
        if manifest.get(field) != package_report.get(field):
            result["schema_errors"].append({"code": "report_manifest_mismatch", "message": f"bundle_manifest and package_report disagree on '{field}'"})

    package_id = manifest.get("package_id")
    policy = path_policies.get(package_id, {})
    payload_dir = extracted / "payload"
    payload_paths: list[str] = []
    if payload_dir.exists():
        for file_path in sorted(payload_dir.rglob("*")):
            if file_path.is_file():
                payload_paths.append(normalize_relpath(file_path.relative_to(payload_dir)))
    declared_paths = [normalize_relpath(item["repo_path"]) for item in manifest.get("payload_files", []) if isinstance(item, dict) and "repo_path" in item]

    if not policy:
        result["ownership_errors"].append({"code": "unknown_package", "message": f"No path policy exists for package '{package_id}'"})
    else:
        result["ownership_errors"] = [
            issue.to_dict() for issue in validate_against_patterns(payload_paths, policy.get("allowed_paths", []), policy.get("forbidden_paths", []))
        ]

    declared_set = set(declared_paths)
    actual_set = set(payload_paths)
    for missing in sorted(declared_set - actual_set):
        result["payload_mismatches"].append({"code": "declared_but_missing", "path": missing})
    for undeclared in sorted(actual_set - declared_set):
        result["payload_mismatches"].append({"code": "undeclared_payload_file", "path": undeclared})

    for item in manifest.get("payload_files", []):
        if not isinstance(item, dict) or "repo_path" not in item:
            continue
        rel = normalize_relpath(item["repo_path"])
        file_path = payload_dir / rel
        if file_path.exists():
            actual_hash = sha256_file(file_path)
            if actual_hash != item.get("sha256"):
                result["payload_mismatches"].append({"code": "hash_mismatch", "path": rel})

    result["ok"] = not any([result["schema_errors"], result["structure_errors"], result["ownership_errors"], result["payload_mismatches"]])
    return result
