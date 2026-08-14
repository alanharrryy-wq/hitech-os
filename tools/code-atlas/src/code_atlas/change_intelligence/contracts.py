from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

DECISIONS = {"PASS", "BLOCKED", "UNKNOWN"}
SUPPORT_LEVELS = {"SUPPORTED", "INFERRED", "UNKNOWN", "CONFLICTED"}
PACK_SCHEMA = "code_atlas_agent_authority_pack.v1"
VERIFY_SCHEMA = "code_atlas_change_verification.v1"
POLICY_SCHEMA = "code_atlas_customer_policy.v1"
CONNECTOR_SCHEMA = "code_atlas_evidence_connector.v1"
ROI_SCHEMA = "code_atlas_roi_event.v1"
SESSION_SCHEMA = "code_atlas_agent_session.v1"

_RAW_SECRET_KEYS = {
    "secret", "secretvalue", "token", "tokenvalue", "password", "passwd",
    "credential", "credentialvalue", "apikey", "api_key", "privatekey", "private_key",
    "accesskey", "access_key", "clientsecret", "client_secret",
}


class ContractError(ValueError):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_json(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()


def require_string_list(value: Any, field: str, *, allow_empty: bool = True) -> list[str]:
    if value is None and allow_empty:
        return []
    if not isinstance(value, list):
        raise ContractError(f"{field} must be a list")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(require_nonempty_string(item, f"{field}[{index}]"))
    if not allow_empty and not result:
        raise ContractError(f"{field} must not be empty")
    return result


def normalize_repo_path(value: str) -> str:
    raw = require_nonempty_string(value, "path").replace("\\", "/")
    if raw.startswith("/") or re.match(r"^[A-Za-z]:/", raw):
        raise ContractError(f"absolute path is not allowed: {value!r}")
    path = PurePosixPath(raw)
    parts = path.parts
    if any(part in {"..", ""} for part in parts):
        raise ContractError(f"unsafe path is not allowed: {value!r}")
    normalized = path.as_posix()
    if normalized in {".", ""}:
        raise ContractError("path must identify a repository-relative location")
    return normalized.rstrip("/")


def normalize_scope(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_repo_path(value)
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return sorted(result)


def path_matches_scope(path: str, scopes: Iterable[str]) -> bool:
    candidate = normalize_repo_path(path)
    for scope in scopes:
        normalized = normalize_repo_path(scope)
        if candidate == normalized or candidate.startswith(normalized + "/"):
            return True
    return False


def ensure_no_raw_secret_values(value: Any, *, location: str = "payload") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized_key = str(key).replace("-", "").replace(" ", "").lower()
            if normalized_key in _RAW_SECRET_KEYS and isinstance(item, str) and item.strip():
                raise ContractError(f"raw secret-like value rejected at {location}.{key}")
            ensure_no_raw_secret_values(item, location=f"{location}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            ensure_no_raw_secret_values(item, location=f"{location}[{index}]")


def require_exact_digest(value: Any, field: str) -> str:
    text = require_nonempty_string(value, field)
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", text):
        raise ContractError(f"{field} must be sha256:<64 lowercase hex chars>")
    return text


def decision_precedence(*states: str) -> str:
    cleaned = [state for state in states if state]
    unknown = [state for state in cleaned if state not in DECISIONS]
    if unknown:
        raise ContractError(f"invalid decision state(s): {unknown}")
    if "BLOCKED" in cleaned:
        return "BLOCKED"
    if "UNKNOWN" in cleaned:
        return "UNKNOWN"
    return "PASS"
