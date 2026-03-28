from __future__ import annotations

import re
from typing import Any, Dict, List

ZIP_FALLBACK_RE = re.compile(r"([A-Za-z]:\\[^\r\n|]*?\.zip)", re.IGNORECASE)
REUSE_RE = re.compile(
    r"\b(reused?|re-using|using existing|already exists?|existing artifact)\b",
    re.IGNORECASE,
)
WARNING_RE = re.compile(r"\b(warn(?:ing)?|caution)\b", re.IGNORECASE)
ERROR_RE = re.compile(r"\b(error|failed?|exception|fatal|traceback)\b", re.IGNORECASE)
BLOCKED_RE = re.compile(r"\b(blocked|denied|forbidden|policy violation|not allowed)\b", re.IGNORECASE)
SUCCESS_RE = re.compile(r"\b(success(?:ful|fully)?|completed?|done|finished)\b", re.IGNORECASE)
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
NON_ALNUM_RE = re.compile(r"[^a-z0-9-]+")
MULTI_DASH_RE = re.compile(r"-{2,}")

MODE_NEW = "new_project"
MODE_EXISTING = "existing_project"
POLICY_RESUME_LATEST = "resume_latest_round"
POLICY_OPEN_NEW = "open_new_round"
POLICY_UPGRADE = "upgrade"
VALID_POLICIES = {POLICY_RESUME_LATEST, POLICY_OPEN_NEW, POLICY_UPGRADE}

EXIT_CODE_MAP: Dict[int, str] = {
    0: "Succeeded",
    10: "FailedRetryable",
    20: "Failed",
    30: "Blocked",
    40: "Failed",
    50: "Blocked",
    60: "FailedRetryable",
}


def map_exit_code_to_contract_detail(
    exit_code: int,
    warnings_present: bool = False,
    timed_out: bool = False,
    contract_violations_present: bool = False,
    status_hint: str = "",
) -> str:
    if timed_out:
        return "LaunchTimeout"
    if contract_violations_present:
        return "Blocked"
    detail = EXIT_CODE_MAP.get(exit_code, "Failed")
    normalized_hint = (status_hint or "").strip().lower()
    if exit_code not in EXIT_CODE_MAP and normalized_hint in {
        "success",
        "reused",
        "blocked",
        "failed",
    }:
        detail = {
            "success": "Succeeded",
            "reused": "Succeeded",
            "blocked": "Blocked",
            "failed": "Failed",
        }[normalized_hint]
    if detail == "Succeeded" and warnings_present:
        return "SucceededWithWarnings"
    return detail


def normalize_contract_detail_to_ui_status(
    contract_detail: str,
    reused_detected: bool = False,
    status_hint: str = "",
) -> str:
    if contract_detail in ("Succeeded", "SucceededWithWarnings"):
        if reused_detected or (status_hint or "").strip().lower() == "reused":
            return "reused"
        return "success"
    if contract_detail == "Blocked":
        return "blocked"
    return "failed"


def normalize_mode(value: Any) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"new", "new_project"}:
        return MODE_NEW
    return MODE_EXISTING


def normalize_policy(value: Any, mode: str) -> str:
    raw = str(value or "").strip().lower()
    if mode == MODE_NEW:
        return POLICY_OPEN_NEW
    if raw in VALID_POLICIES:
        return raw
    return POLICY_RESUME_LATEST


def derive_project_id_from_name(name: Any) -> str:
    raw = str(name or "").strip().lower()
    raw = raw.replace("_", "-")
    raw = re.sub(r"\s+", "-", raw)
    raw = NON_ALNUM_RE.sub("-", raw)
    raw = MULTI_DASH_RE.sub("-", raw).strip("-")
    if not raw:
        raw = "new-project"
    if not raw[0].isalnum():
        raw = "p-" + raw
    return raw[:128]


def validate_request_payload(payload: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    mode = normalize_mode(payload.get("mode"))
    project_id = str(payload.get("project_id") or "").strip()
    project_name = str(payload.get("project_name") or "").strip()
    initiative_type = str(payload.get("initiative_type") or "").strip()
    raw_policy = str(payload.get("policy") or "").strip()
    policy = normalize_policy(raw_policy, mode)
    intent = str(payload.get("intent") or "").strip()
    non_interactive = bool(payload.get("non_interactive"))

    if mode == MODE_NEW:
        if not project_name:
            errors.append("Project name is required for new project mode.")
        if not initiative_type:
            errors.append("Initiative type is required for new project mode.")
        if not intent:
            errors.append("Intent is required for new project mode.")
        if policy != POLICY_OPEN_NEW:
            errors.append("New project mode only supports policy 'open_new_round'.")
    else:
        if not project_id:
            errors.append("Project ID is required for existing project mode.")
        if policy in {POLICY_OPEN_NEW, POLICY_UPGRADE} and not intent:
            errors.append(f"Intent is required when policy is '{policy}'.")

    if mode == MODE_EXISTING and non_interactive and not project_id:
        errors.append("Project ID is required when Non-interactive is enabled.")
    if project_id and not PROJECT_ID_RE.match(project_id):
        errors.append(
            "Project ID contains invalid characters. Use letters, numbers, dot, dash, or underscore only."
        )
    if not policy or policy not in VALID_POLICIES:
        errors.append(
            "Policy must be one of: resume_latest_round, open_new_round, upgrade."
        )
    if raw_policy and CONTROL_CHAR_RE.search(raw_policy):
        errors.append("Policy contains control characters. Clean the value and try again.")
    if intent and CONTROL_CHAR_RE.search(intent):
        errors.append("Intent contains control characters. Clean the text and try again.")
    if project_name and CONTROL_CHAR_RE.search(project_name):
        errors.append("Project name contains control characters. Clean the text and try again.")
    if initiative_type and CONTROL_CHAR_RE.search(initiative_type):
        errors.append("Initiative type contains control characters. Clean the text and try again.")
    return errors


__all__ = [
    "BLOCKED_RE",
    "CONTROL_CHAR_RE",
    "ERROR_RE",
    "EXIT_CODE_MAP",
    "PROJECT_ID_RE",
    "REUSE_RE",
    "SUCCESS_RE",
    "WARNING_RE",
    "ZIP_FALLBACK_RE",
    "derive_project_id_from_name",
    "map_exit_code_to_contract_detail",
    "normalize_mode",
    "normalize_policy",
    "normalize_contract_detail_to_ui_status",
    "validate_request_payload",
]
