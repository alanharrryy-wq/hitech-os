from __future__ import annotations

import hashlib
import hmac
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import Issue, extract_zip_to_temp, is_safe_relative_path, normalize_relpath, read_json, sha256_file
from .config import load_path_policies, load_system_config
from .validators import validate_against_patterns, validate_payload_items, validate_required_fields


REQUIRED_BUNDLE_FILES = [
    "bundle_manifest.json",
    "package_report.json",
    "notes/summary.md",
]


def _coerce_positive_int(value: Any, default: int) -> int:
    try:
        coerced = int(value)
    except (TypeError, ValueError):
        return default
    return coerced if coerced > 0 else default


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _is_hex_digest(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value.lower())


def _parse_utc_or_none(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc).replace(microsecond=0)


def _validate_manifest_signature(
    extracted: Path,
    manifest: dict[str, Any],
    security: dict[str, Any],
    result: dict[str, Any],
) -> None:
    signature_path = extracted / "bundle_manifest.sig"
    require_signature = bool(security.get("require_manifest_signature", False))
    if not signature_path.exists():
        if require_signature:
            result["schema_errors"].append({"code": "missing_manifest_signature", "message": "bundle_manifest.sig is required by policy"})
        return

    raw_signature = signature_path.read_text(encoding="utf-8").strip().lower()
    if not _is_hex_digest(raw_signature):
        result["schema_errors"].append({"code": "invalid_manifest_signature_format", "message": "bundle_manifest.sig must contain a 64-char hex sha256 digest"})
        return

    algorithm = str(security.get("signature_algorithm", "hmac-sha256")).strip().lower()
    if algorithm != "hmac-sha256":
        result["schema_errors"].append({"code": "unsupported_signature_algorithm", "message": f"Unsupported signature_algorithm '{algorithm}'"})
        return

    env_var = str(security.get("signature_env_var", "UEF_BUNDLE_SIGNING_KEY")).strip() or "UEF_BUNDLE_SIGNING_KEY"
    secret = os.environ.get(env_var)
    if not secret:
        message = f"Manifest signature provided but '{env_var}' is not set; cannot verify"
        if require_signature:
            result["schema_errors"].append({"code": "missing_signature_key", "message": message})
        else:
            result["warnings"].append({"code": "signature_not_verified", "message": message})
        return

    expected = hmac.new(secret.encode("utf-8"), _canonical_json_bytes(manifest), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, raw_signature):
        result["schema_errors"].append({"code": "manifest_signature_mismatch", "message": "bundle_manifest.sig does not match bundle_manifest.json"})


def _validate_waiver_refs(
    repo_root: Path,
    manifest: dict[str, Any],
    result: dict[str, Any],
) -> None:
    waiver_refs = manifest.get("waiver_refs", [])
    if waiver_refs is None:
        return
    if not isinstance(waiver_refs, list):
        result["schema_errors"].append({"code": "invalid_waiver_refs", "message": "bundle_manifest.waiver_refs must be an array when present"})
        return

    schema_path = repo_root / "schemas/execution_framework/waiver_request.schema.json"
    waiver_schema = read_json(schema_path) if schema_path.exists() else {"required_fields": {}}
    required_fields = waiver_schema.get("required_fields", {})

    for ref in waiver_refs:
        if not isinstance(ref, str) or not ref.strip():
            result["schema_errors"].append({"code": "invalid_waiver_ref", "message": "waiver_ref entries must be non-empty strings"})
            continue
        rel = normalize_relpath(ref)
        if not is_safe_relative_path(rel):
            result["schema_errors"].append({"code": "invalid_waiver_ref_path", "message": f"waiver_ref '{ref}' is not a safe repo-relative path"})
            continue
        waiver_path = repo_root / rel
        if not waiver_path.exists():
            result["schema_errors"].append({"code": "missing_waiver_ref", "message": f"waiver_ref '{rel}' does not exist"})
            continue
        waiver = read_json(waiver_path)
        result["schema_errors"].extend(issue.to_dict() for issue in validate_required_fields(waiver, required_fields, f"waiver_request({rel})"))

        decision = str(waiver.get("decision_status", "")).strip().lower()
        if decision != "approved":
            result["schema_errors"].append({"code": "waiver_not_approved", "message": f"waiver_ref '{rel}' is not approved"})

        for field in ("project_id", "run_id", "round_id"):
            waiver_value = waiver.get(field)
            manifest_value = manifest.get(field)
            if waiver_value and manifest_value and waiver_value != manifest_value:
                result["schema_errors"].append(
                    {
                        "code": "waiver_context_mismatch",
                        "message": f"waiver_ref '{rel}' has {field}='{waiver_value}' but bundle manifest has '{manifest_value}'",
                    }
                )

        expires_at = _parse_utc_or_none(waiver.get("expires_at_utc"))
        if expires_at and expires_at < datetime.now(timezone.utc).replace(microsecond=0):
            result["schema_errors"].append({"code": "waiver_expired", "message": f"waiver_ref '{rel}' is expired at {waiver.get('expires_at_utc')}"})


def inspect_bundle_structure(zip_path: Path) -> list[Issue]:
    issues: list[Issue] = []
    names: set[str] = set()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            normalized = normalize_relpath(info.filename)
            if info.is_dir():
                normalized = normalized.rstrip("/")
                if not normalized:
                    continue
            if not is_safe_relative_path(normalized):
                issues.append(Issue("unsafe_archive_member", f"Bundle contains unsafe archive path '{info.filename}'", path=normalized))
                continue
            names.add(normalized)
    for required in REQUIRED_BUNDLE_FILES:
        if required not in names:
            issues.append(Issue("missing_bundle_file", f"Bundle is missing '{required}'"))
    has_payload = any(name.startswith("payload/") and not name.endswith("/") for name in names)
    if not has_payload:
        issues.append(Issue("missing_payload", "Bundle must contain payload files under payload/"))
    return issues


def validate_bundle_zip(zip_path: Path, repo_root: Path) -> dict[str, Any]:
    path_policies = load_path_policies(repo_root)
    system_config = load_system_config(repo_root)
    security = system_config.get("bundle_security", {})
    result: dict[str, Any] = {
        "bundle_path": str(zip_path),
        "schema_errors": [],
        "structure_errors": [],
        "ownership_errors": [],
        "payload_mismatches": [],
        "warnings": [],
        "ok": False,
    }
    max_bundle_size = _coerce_positive_int(security.get("max_bundle_size_bytes"), 0)
    if max_bundle_size > 0 and zip_path.exists():
        bundle_size = zip_path.stat().st_size
        if bundle_size > max_bundle_size:
            result["structure_errors"].append(
                {
                    "code": "bundle_too_large",
                    "message": f"bundle size {bundle_size} exceeds max_bundle_size_bytes={max_bundle_size}",
                }
            )
    structure_issues = inspect_bundle_structure(zip_path)
    result["structure_errors"].extend(issue.to_dict() for issue in structure_issues)
    try:
        extracted = extract_zip_to_temp(zip_path)
    except ValueError as exc:
        result["structure_errors"].append({"code": "unsafe_archive", "message": str(exc)})
        return result

    manifest_path = extracted / "bundle_manifest.json"
    report_path = extracted / "package_report.json"
    if not manifest_path.exists() or not report_path.exists():
        return result

    manifest = read_json(manifest_path)
    package_report = read_json(report_path)
    result["bundle_manifest"] = manifest
    result["package_report"] = package_report

    _validate_manifest_signature(extracted, manifest, security, result)
    _validate_waiver_refs(repo_root, manifest, result)

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
                rel = normalize_relpath(file_path.relative_to(payload_dir))
                if not is_safe_relative_path(rel):
                    result["payload_mismatches"].append({"code": "invalid_payload_path", "path": rel})
                    continue
                payload_paths.append(rel)
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
        if not is_safe_relative_path(rel):
            continue
        file_path = payload_dir / rel
        if file_path.exists():
            actual_hash = sha256_file(file_path)
            if actual_hash != item.get("sha256"):
                result["payload_mismatches"].append({"code": "hash_mismatch", "path": rel})
            declared_size = item.get("size_bytes")
            actual_size = file_path.stat().st_size
            if declared_size != actual_size:
                result["payload_mismatches"].append({"code": "size_mismatch", "path": rel})
            max_payload_size = _coerce_positive_int(security.get("max_payload_file_size_bytes"), 0)
            if max_payload_size > 0 and actual_size > max_payload_size:
                result["payload_mismatches"].append(
                    {"code": "payload_file_too_large", "path": rel, "message": f"{actual_size} exceeds max_payload_file_size_bytes={max_payload_size}"}
                )

    result["ok"] = not any([result["schema_errors"], result["structure_errors"], result["ownership_errors"], result["payload_mismatches"]])
    return result
