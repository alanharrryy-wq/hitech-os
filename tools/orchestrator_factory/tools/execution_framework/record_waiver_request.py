from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import argparse
from pathlib import Path

from lib.common import discover_repo_root, read_json, stable_json_dumps
from lib.config import load_system_config
from lib.coordination import canonical_utc, normalize_repo_relative_refs, normalize_string_list, sanitize_identifier, validate_simple_schema
from lib.validators import validate_required_fields


def _validate_allowed(payload: dict, schema: dict, field: str, allowed_key: str, issues: list[dict[str, str]]) -> None:
    allowed = set(schema.get(allowed_key, []))
    if not allowed or field not in payload:
        return
    value = payload.get(field)
    if value not in allowed:
        issues.append({"code": "invalid_enum_value", "message": f"{field}='{value}' is not allowed"})


def _normalize(payload: dict) -> dict:
    normalized = dict(payload)
    for field in [
        "schema_version",
        "waiver_id",
        "project_id",
        "run_id",
        "round_id",
        "requested_by_chat_id",
        "decision_owner_chat_id",
        "decision_status",
        "status",
        "severity",
        "target_ref_type",
        "waiver_scope",
    ]:
        if field in normalized and normalized[field] is not None:
            normalized[field] = str(normalized[field]).strip()
    for field in [
        "requested_at_utc",
        "decision_due_at_utc",
        "approved_at_utc",
        "denied_at_utc",
        "revoked_at_utc",
        "expires_at_utc",
        "last_reviewed_at_utc",
        "owner_acknowledged_at_utc",
    ]:
        if field in normalized and normalized[field]:
            normalized[field] = canonical_utc(str(normalized[field]))

    if "affected_paths" in normalized:
        normalized["affected_paths"] = normalize_repo_relative_refs(normalized["affected_paths"], "affected_paths")
    if "target_refs" in normalized:
        normalized["target_refs"] = normalize_repo_relative_refs(normalized["target_refs"], "target_refs")
    for field in ["evidence_refs", "rule_refs", "related_entity_ids", "tags", "compensating_controls"]:
        if field in normalized:
            normalized[field] = normalize_string_list(normalized[field], field)
    return normalized


def _default_output_path(repo_root: Path, payload: dict) -> Path:
    system = load_system_config(repo_root)
    run_root = repo_root / system["runs_root"] / payload["run_id"]
    round_root = run_root / system["rounds_dir_name"] / payload["round_id"]
    return round_root / system["reports_dir_name"] / "waivers" / f"{sanitize_identifier(payload['waiver_id'])}.waiver_request.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and record a waiver_request artifact into the active run/round reports tree.")
    parser.add_argument("--input", required=True, help="Path to waiver_request JSON")
    parser.add_argument("--output", help="Optional explicit output path")
    args = parser.parse_args()

    repo_root = discover_repo_root(Path(__file__).resolve())
    schema = read_json(repo_root / "schemas/execution_framework/waiver_request.schema.json")
    payload = read_json(Path(args.input))

    issues = [issue.to_dict() for issue in validate_simple_schema(payload, schema, "waiver_request")]
    _validate_allowed(payload, schema, "decision_status", "allowed_decision_status_values", issues)
    _validate_allowed(payload, schema, "status", "allowed_status_values", issues)
    _validate_allowed(payload, schema, "severity", "allowed_severity_values", issues)
    _validate_allowed(payload, schema, "target_ref_type", "allowed_target_ref_type_values", issues)
    if "waiver_scope" in payload:
        _validate_allowed(payload, schema, "waiver_scope", "allowed_waiver_scope_values", issues)
    for field in ["requested_by_chat_id", "decision_owner_chat_id"]:
        _validate_allowed(payload, schema, field, "allowed_chat_id_values", issues)

    history_required = schema.get("history_item_required_fields", {})
    history = payload.get("history", [])
    if isinstance(history, list):
        for index, entry in enumerate(history):
            if isinstance(entry, dict):
                issues.extend(issue.to_dict() for issue in validate_required_fields(entry, history_required, f"history[{index}]"))
            else:
                issues.append({"code": "invalid_history_item", "message": f"history[{index}] must be an object"})
    else:
        issues.append({"code": "invalid_history", "message": "history must be an array"})

    if issues:
        print(
            stable_json_dumps(
                {
                    "ok": False,
                    "issues": issues,
                }
            )
        )
        return 1

    normalized = _normalize(payload)
    output_path = Path(args.output) if args.output else _default_output_path(repo_root, normalized)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(stable_json_dumps(normalized), encoding="utf-8")

    print(
        stable_json_dumps(
            {
                "ok": True,
                "output_path": str(output_path),
                "waiver_id": normalized.get("waiver_id"),
                "decision_status": normalized.get("decision_status"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
