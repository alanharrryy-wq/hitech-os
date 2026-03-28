#!/usr/bin/env python3
"""Contract validator for canonical one-button session ZIP exports.

This module intentionally relies on Python's standard library only.
It validates the exported ZIP against the v1.2 contract descriptor,
checks required files, evaluates conditional packet/prompt groups,
verifies the exported session_file_index.json structure, validates the
session manifest shape, and confirms that acceptance_report.json is
compatible with acceptance_result.schema.json.

The validator is designed as a guardrail, not as a generic JSON Schema
engine. It consumes the local schema and contract documents, applies the
specific rules the one-button runtime depends on, and emits a structured
validation report that can be persisted by the caller.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


EXIT_VALID = 0
EXIT_INVALID = 1
EXIT_RUNTIME_ERROR = 2


REPO_SENTINEL_DIRNAME = "tools"
FRAMEWORK_DIRNAME = "orchestrator_factory"
EXECUTION_FRAMEWORK_DIRNAME = "execution_framework"


@dataclass(frozen=True)
class FileRecord:
    path: str
    size_bytes: int
    sha256: str


class ContractValidationError(Exception):
    """Raised when the validator cannot continue due to invalid inputs."""


class ValidationContext:
    def __init__(self, framework_root: Path, zip_path: Path) -> None:
        self.framework_root = framework_root
        self.zip_path = zip_path
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a canonical one-button session ZIP against the v1.2 export contract."
    )
    parser.add_argument(
        "--zip-path",
        required=False,
        help="Absolute or relative path to the session ZIP to validate.",
    )
    parser.add_argument(
        "--framework-root",
        default=None,
        help="Framework root. Defaults to auto-detection from this script location.",
    )
    parser.add_argument(
        "--contract-schema",
        default=None,
        help="Optional override path for session_zip_contract.schema.json.",
    )
    parser.add_argument(
        "--manifest-schema",
        default=None,
        help="Optional override path for session_manifest.schema.json.",
    )
    parser.add_argument(
        "--acceptance-schema",
        default=None,
        help="Optional override path for acceptance_result.schema.json.",
    )
    parser.add_argument(
        "--output-report",
        default=None,
        help="Optional path where the JSON validation report will be written.",
    )
    parser.add_argument(
        "--print-acceptance-stub",
        action="store_true",
        help="Print a valid stub acceptance report to stdout and exit.",
    )
    parser.add_argument("--project-id", default=None, help="Required with --print-acceptance-stub.")
    parser.add_argument("--run-id", default=None, help="Required with --print-acceptance-stub.")
    parser.add_argument("--round-id", default=None, help="Required with --print-acceptance-stub.")
    return parser.parse_args(argv)


def detect_framework_root(explicit: Optional[str]) -> Path:
    if explicit:
        return Path(explicit).resolve()
    script_path = Path(__file__).resolve()
    current = script_path.parent
    for candidate in (current, *current.parents):
        if candidate.name == FRAMEWORK_DIRNAME and candidate.parent.name == REPO_SENTINEL_DIRNAME:
            return candidate
    raise ContractValidationError(
        "Could not auto-detect framework root from validate_session_zip_contract.py location. Use --framework-root."
    )


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError as exc:
        raise ContractValidationError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ContractValidationError(f"Invalid JSON in {path}: {exc}") from exc


def build_acceptance_stub(project_id: str, run_id: str, round_id: str) -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "project_id": project_id,
        "run_id": run_id,
        "round_id": round_id,
        "generated_at_utc": utc_now_iso(),
        "overall_status": "pending",
        "package_results": [],
        "has_bundles": False,
        "accepted_bundles": [],
        "rejected_bundles": [],
        "notes": [
            "Acceptance report stub emitted because no integration bundles were present at session export time."
        ],
    }


def sha256_bytes(payload: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(payload)
    return digest.hexdigest()


def list_zip_files(zip_path: Path) -> Tuple[List[FileRecord], Dict[str, bytes]]:
    records: List[FileRecord] = []
    content_map: Dict[str, bytes] = {}
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                raw_bytes = archive.read(info.filename)
                normalized = info.filename.replace("\\", "/")
                content_map[normalized] = raw_bytes
                records.append(
                    FileRecord(
                        path=normalized,
                        size_bytes=len(raw_bytes),
                        sha256=sha256_bytes(raw_bytes),
                    )
                )
    except FileNotFoundError as exc:
        raise ContractValidationError(f"ZIP file not found: {zip_path}") from exc
    except zipfile.BadZipFile as exc:
        raise ContractValidationError(f"Invalid ZIP file: {zip_path}") from exc
    return records, content_map


def read_json_from_zip(content_map: Dict[str, bytes], relative_path: str, ctx: ValidationContext) -> Optional[Dict[str, Any]]:
    raw = content_map.get(relative_path)
    if raw is None:
        ctx.error(f"Missing JSON file in ZIP: {relative_path}")
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        ctx.error(f"JSON file is not valid UTF-8: {relative_path}")
        return None
    except json.JSONDecodeError as exc:
        ctx.error(f"JSON file is invalid: {relative_path}: {exc}")
        return None


def ensure_required_files(records: Sequence[FileRecord], required_files: Sequence[str], ctx: ValidationContext) -> bool:
    record_paths = {record.path for record in records}
    ok = True
    for required_path in required_files:
        if required_path not in record_paths:
            ok = False
            ctx.error(f"Missing required file: {required_path}")
    return ok


def match_pattern_count(records: Sequence[FileRecord], pattern: str) -> int:
    compiled = re.compile(pattern)
    return sum(1 for record in records if compiled.match(record.path))


def evaluate_conditional_groups(
    records: Sequence[FileRecord],
    flags: Dict[str, bool],
    contract_groups: Sequence[Dict[str, Any]],
    ctx: ValidationContext,
) -> bool:
    ok = True
    for group in contract_groups:
        flag_name = group["condition_flag"]
        enabled = bool(flags.get(flag_name, False))
        if not enabled:
            continue
        total_matches = 0
        for pattern in group.get("required_patterns", []):
            count = match_pattern_count(records, pattern)
            if count == 0:
                ctx.error(
                    f"Conditional group '{group['name']}' was enabled by flag '{flag_name}' but no file matched pattern: {pattern}"
                )
                ok = False
            total_matches += count
        if total_matches < int(group.get("minimum_matches", 0)):
            ctx.error(
                f"Conditional group '{group['name']}' matched {total_matches} files but requires at least {group.get('minimum_matches', 0)}."
            )
            ok = False
    return ok


def validate_required_keys(payload: Dict[str, Any], required_keys: Sequence[str], payload_name: str, ctx: ValidationContext) -> bool:
    ok = True
    for key in required_keys:
        if key not in payload:
            ok = False
            ctx.error(f"{payload_name} is missing required key: {key}")
    return ok


def validate_session_manifest(
    manifest_payload: Optional[Dict[str, Any]],
    manifest_schema: Dict[str, Any],
    ctx: ValidationContext,
) -> bool:
    if manifest_payload is None:
        return False
    required_keys = manifest_schema.get("required", [])
    ok = validate_required_keys(manifest_payload, required_keys, "session_manifest.json", ctx)

    if manifest_payload.get("schema_version") != "1.0":
        ctx.error("session_manifest.json must set schema_version='1.0'.")
        ok = False

    if manifest_payload.get("session_mode") not in {"existing_project", "new_project"}:
        ctx.error("session_manifest.json has invalid session_mode.")
        ok = False

    if manifest_payload.get("policy") not in {"resume_latest_round", "open_new_round", "upgrade"}:
        ctx.error("session_manifest.json has invalid policy.")
        ok = False

    if manifest_payload.get("status") not in {"ready_for_dispatch", "blocked", "failed", "reused"}:
        ctx.error("session_manifest.json has invalid status.")
        ok = False

    checks = manifest_payload.get("checks", {})
    for required_check in ("contracts", "smoke", "readiness_stage_install", "readiness_stage_round"):
        if required_check not in checks:
            ctx.error(f"session_manifest.json checks is missing '{required_check}'.")
            ok = False

    idempotency = manifest_payload.get("idempotency", {})
    context_hashes = idempotency.get("context_hashes", {})
    for hash_key in ("project_manifest_sha256", "run_manifest_sha256", "round_manifest_sha256"):
        if hash_key not in context_hashes:
            ctx.error(f"session_manifest.json idempotency.context_hashes is missing '{hash_key}'.")
            ok = False
        else:
            hash_value = str(context_hashes[hash_key])
            if hash_value != "none" and not re.fullmatch(r"[a-fA-F0-9]{64}", hash_value):
                ctx.error(f"session_manifest.json field '{hash_key}' must be 'none' or a 64-char SHA256.")
                ok = False

    intent = manifest_payload.get("intent", {})
    normalized_intent = intent.get("normalized")
    if not isinstance(normalized_intent, str) or not normalized_intent.strip():
        ctx.error("session_manifest.json intent.normalized must be a non-empty string.")
        ok = False

    issues = manifest_payload.get("issues")
    if not isinstance(issues, list):
        ctx.error("session_manifest.json issues must be an array.")
        ok = False

    return ok


def validate_acceptance_report(
    acceptance_payload: Optional[Dict[str, Any]],
    acceptance_schema_payload: Dict[str, Any],
    contract_schema_payload: Dict[str, Any],
    ctx: ValidationContext,
) -> bool:
    if acceptance_payload is None:
        return False
    required_by_acceptance_schema = acceptance_schema_payload.get("required", [])
    required_by_contract = contract_schema_payload.get("x-contract", {}).get("acceptance_report", {}).get("required_fields", [])

    required_keys = sorted(set(required_by_acceptance_schema) | set(required_by_contract))
    ok = validate_required_keys(acceptance_payload, required_keys, "acceptance_report.json", ctx)

    if acceptance_payload.get("schema_version") != "1.0":
        ctx.error("acceptance_report.json must set schema_version='1.0'.")
        ok = False

    if not isinstance(acceptance_payload.get("package_results"), list):
        ctx.error("acceptance_report.json package_results must be an array.")
        ok = False

    overall_status = acceptance_payload.get("overall_status")
    if not isinstance(overall_status, str) or not overall_status:
        ctx.error("acceptance_report.json overall_status must be a non-empty string.")
        ok = False

    has_bundles = acceptance_payload.get("has_bundles")
    package_results = acceptance_payload.get("package_results")
    if has_bundles is False and package_results == [] and overall_status != "pending":
        ctx.error(
            "acceptance_report.json stub with has_bundles=false and package_results=[] must use overall_status='pending'."
        )
        ok = False

    return ok


def validate_session_file_index(content_map: Dict[str, bytes], records: Sequence[FileRecord], ctx: ValidationContext) -> bool:
    payload = read_json_from_zip(content_map, "session/session_file_index.json", ctx)
    if payload is None:
        return False

    if not isinstance(payload, list):
        ctx.error("session/session_file_index.json must contain a JSON array.")
        return False

    indexed = {}
    ok = True
    for item in payload:
        if not isinstance(item, dict):
            ctx.error("session/session_file_index.json entries must be JSON objects.")
            ok = False
            continue
        for key in ("path", "sha256", "size_bytes"):
            if key not in item:
                ctx.error(f"session/session_file_index.json entry is missing key '{key}'.")
                ok = False
        if ok:
            indexed[str(item["path"])] = item

    record_lookup = {record.path: record for record in records}
    for path, record in record_lookup.items():
        if path == "session/session_file_index.json":
            continue
        entry = indexed.get(path)
        if entry is None:
            ctx.warn(f"session_file_index.json is missing an entry for '{path}'.")
            continue
        if entry.get("sha256") != record.sha256:
            ctx.error(f"session_file_index.json has sha256 mismatch for '{path}'.")
            ok = False
        if entry.get("size_bytes") != record.size_bytes:
            ctx.error(f"session_file_index.json has size mismatch for '{path}'.")
            ok = False
    return ok


def normalize_path(value: Optional[str], fallback: Path) -> Path:
    if value is None:
        return fallback
    return Path(value).resolve()


def build_validation_report(
    ctx: ValidationContext,
    records: Sequence[FileRecord],
    packets_generated: bool,
    prompts_generated: bool,
    required_present: bool,
    conditionals_ok: bool,
    manifest_ok: bool,
    acceptance_ok: bool,
    file_index_ok: bool,
) -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "contract_version": "1.2",
        "zip_path": str(ctx.zip_path),
        "files": [
            {
                "path": record.path,
                "size_bytes": record.size_bytes,
                "sha256": record.sha256,
            }
            for record in sorted(records, key=lambda item: item.path)
        ],
        "flags": {
            "packets_generated": packets_generated,
            "prompts_generated": prompts_generated,
        },
        "validation": {
            "required_files_present": required_present,
            "conditional_requirements_satisfied": conditionals_ok,
            "session_manifest_valid": manifest_ok,
            "acceptance_report_valid": acceptance_ok,
            "session_file_index_valid": file_index_ok,
            "errors": ctx.errors,
            "warnings": ctx.warnings,
        },
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    try:
        args = parse_args(argv)
        framework_root = detect_framework_root(args.framework_root)

        if args.print_acceptance_stub:
            missing = [
                name
                for name, value in (("project-id", args.project_id), ("run-id", args.run_id), ("round-id", args.round_id))
                if not value
            ]
            if missing:
                raise ContractValidationError(
                    "--print-acceptance-stub requires --project-id, --run-id, and --round-id. Missing: " + ", ".join(missing)
                )
            print(json.dumps(build_acceptance_stub(args.project_id, args.run_id, args.round_id), indent=2))
            return EXIT_VALID

        if not args.zip_path:
            raise ContractValidationError("--zip-path is required unless --print-acceptance-stub is used.")

        zip_path = Path(args.zip_path).resolve()
        ctx = ValidationContext(framework_root=framework_root, zip_path=zip_path)

        contract_schema_path = normalize_path(
            args.contract_schema,
            framework_root / "schemas" / EXECUTION_FRAMEWORK_DIRNAME / "session_zip_contract.schema.json",
        )
        manifest_schema_path = normalize_path(
            args.manifest_schema,
            framework_root / "schemas" / EXECUTION_FRAMEWORK_DIRNAME / "session_manifest.schema.json",
        )
        acceptance_schema_path = normalize_path(
            args.acceptance_schema,
            framework_root / "schemas" / EXECUTION_FRAMEWORK_DIRNAME / "acceptance_result.schema.json",
        )

        contract_schema_payload = load_json(contract_schema_path)
        manifest_schema_payload = load_json(manifest_schema_path)
        acceptance_schema_payload = load_json(acceptance_schema_path)

        records, content_map = list_zip_files(zip_path)
        required_files = contract_schema_payload.get("x-contract", {}).get("required_files", [])
        contract_groups = contract_schema_payload.get("x-contract", {}).get("conditional_groups", [])

        packets_generated = any(re.match(r"^round/packets/.+/work_packet\\.json$", record.path) for record in records)
        prompts_generated = any(re.match(r"^round/prompts/.+\\.prompt\\.md$", record.path) for record in records)

        required_present = ensure_required_files(records, required_files, ctx)
        conditionals_ok = evaluate_conditional_groups(
            records,
            {"packets_generated": packets_generated, "prompts_generated": prompts_generated},
            contract_groups,
            ctx,
        )

        manifest_payload = read_json_from_zip(content_map, "session/session_manifest.json", ctx)
        acceptance_payload = read_json_from_zip(content_map, "round/reports/acceptance_report.json", ctx)

        manifest_ok = validate_session_manifest(manifest_payload, manifest_schema_payload, ctx)
        acceptance_ok = validate_acceptance_report(
            acceptance_payload,
            acceptance_schema_payload,
            contract_schema_payload,
            ctx,
        )
        file_index_ok = validate_session_file_index(content_map, records, ctx)

        report = build_validation_report(
            ctx=ctx,
            records=records,
            packets_generated=packets_generated,
            prompts_generated=prompts_generated,
            required_present=required_present,
            conditionals_ok=conditionals_ok,
            manifest_ok=manifest_ok,
            acceptance_ok=acceptance_ok,
            file_index_ok=file_index_ok,
        )

        if args.output_report:
            output_path = Path(args.output_report).resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as fh:
                json.dump(report, fh, indent=2)
                fh.write("\n")

        if ctx.errors:
            print(json.dumps(report, indent=2))
            return EXIT_INVALID

        print(json.dumps(report, indent=2))
        return EXIT_VALID
    except ContractValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR
    except Exception as exc:  # pragma: no cover
        print(f"UNEXPECTED ERROR: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
